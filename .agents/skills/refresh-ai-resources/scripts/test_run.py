#!/usr/bin/env python3
"""Offline integration tests for the maintenance runner (no model/network access)."""

from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
BASE_README = """# Curated AI resources

**Last reviewed: REVIEW_DATE.**

## Table of contents

- [Assistants](#assistants)
- [Personal agents](#personal-agents)

## Assistants

- [Example](https://example.com/) - Existing assistant.

## Personal agents

- [Agent](https://example.com/agent) - Existing personal agent.
"""
BASE_README = BASE_README.replace(
    "REVIEW_DATE",
    dt.datetime.now(dt.timezone.utc).strftime("%B %d, %Y").replace(" 0", " "),
)

FAKE_CODEX = r"""
import datetime
import json
import os
from pathlib import Path
import sys
import time

args = sys.argv[1:]
assert "--search" in args, "Live web search must be explicitly enabled"
assert args[args.index("-a") + 1] == "never", "Approval policy must be noninteractive"
assert "exec" in args
assert args[args.index("--sandbox") + 1] == "workspace-write"
assert "--ephemeral" in args
assert "--json" in args
assert args[args.index("--color") + 1] == "never"
assert Path(args[args.index("--output-schema") + 1]).is_file()
checkout = Path(args[args.index("-C") + 1])
output = Path(args[args.index("-o") + 1])
assert "$refresh-ai-resources" in args[-1]
scenario = os.environ.get("FAKE_SCENARIO", "ready")
with Path(os.environ["FAKE_CALL_LOG"]).open("a") as log:
    log.write(json.dumps({
        "tool": "codex", "args": args,
        "readme": (checkout / "README.md").read_text(),
    }) + "\n")
if scenario == "timeout":
    time.sleep(30)
    sys.exit(0)
if scenario == "malformed":
    output.write_text("not JSON")
    sys.exit(0)
today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
result = {
    "status": "ready",
    "review_date": today,
    "reviewed_sections": ["Assistants", "Personal agents"],
    "summary": "Verified resources against official documentation.",
    "changes": [{
        "resource": "Example", "action": "update",
        "reason": "Official documentation confirms the current capability.",
        "sources": ["https://example.com/docs"],
    }],
    "evidence": [{"section": "Assistants", "topic": "Example",
                  "url": "https://example.com/docs",
                  "finding": "The resource now supports web research."},
                 {"section": "Personal agents", "topic": "Agent",
                  "url": "https://example.com/agent",
                  "finding": "The existing agent description remains accurate."}],
}
readme = checkout / "README.md"
if scenario == "no_changes":
    result["status"] = "no_changes"
    result["changes"] = []
else:
    readme.write_text(readme.read_text().replace(
        "Existing assistant.", "Assistant with web research."
    ))
if scenario == "blocked":
    result["status"] = "blocked"
    result["summary"] = "Research source could not be verified."
if scenario == "unexpected_file":
    (checkout / "UNEXPECTED.txt").write_text("must not publish")
if scenario == "incomplete":
    result["reviewed_sections"] = ["Assistants"]
if scenario == "incomplete_evidence":
    result["evidence"] = result["evidence"][:1]
if scenario == "empty_readme":
    readme.write_text("")
output.write_text(json.dumps(result))
print(json.dumps({"type": "turn.completed"}))
"""

FAKE_NPX = r"""
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
assert args == [
    "--yes", "--package=prettier@latest", "prettier", "--write", "README.md",
]
assert Path("README.md").is_file()
with Path(os.environ["FAKE_CALL_LOG"]).open("a") as log:
    log.write(json.dumps({"tool": "npx", "args": args}) + "\n")
"""


class RunnerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ai-maintenance-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "checkout"
        self.upstream = self.root / "upstream.git"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.call_log = self.root / "calls.jsonl"
        self.env = os.environ.copy()
        self.env.update(
            PATH=f"{self.bin}{os.pathsep}{self.env.get('PATH', '')}",
            FAKE_CALL_LOG=str(self.call_log),
            FAKE_SCENARIO="ready",
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="Maintenance Test",
            GIT_AUTHOR_EMAIL="test@example.com",
            GIT_COMMITTER_NAME="Maintenance Test",
            GIT_COMMITTER_EMAIL="test@example.com",
            CODEX_HOME=str(self.root / "codex-home"),
            npm_config_cache=str(self.root / "npm-cache"),
        )
        # No real Codex, npm, or formatter can run through this test environment.
        for name, body in (("codex", FAKE_CODEX), ("npx", FAKE_NPX)):
            script = self.bin / name
            script.write_text(f"#!{sys.executable}\n{body}")
            script.chmod(0o755)
        self.git(
            "init", "--bare", "--initial-branch=main", str(self.upstream), cwd=self.root
        )
        self.git("init", "--initial-branch=main", str(self.repo), cwd=self.root)
        self.skill = self.repo / ".agents" / "skills" / "refresh-ai-resources"
        shutil.copytree(SKILL, self.skill, ignore=shutil.ignore_patterns("__pycache__"))
        (self.repo / "README.md").write_text(BASE_README)
        self.git("add", ".")
        self.git("commit", "-m", "Initial fixture")
        self.git("remote", "add", "origin", str(self.upstream))
        self.git("push", "-u", "origin", "main")
        self.start_head = self.git("rev-parse", "HEAD")
        self.runner = self.skill / "scripts" / "run.py"

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or self.repo,
            env=self.env,
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip()

    def run_runner(
        self, scenario: str = "ready", *args: str
    ) -> subprocess.CompletedProcess[str]:
        env = self.env | {"FAKE_SCENARIO": scenario}
        return subprocess.run(
            [sys.executable, str(self.runner), "--repo", str(self.repo), *args],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=20,
        )

    def assert_ok(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_failed(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_source_unchanged(self) -> None:
        self.assertEqual(self.git("rev-parse", "HEAD"), self.start_head)
        self.assertEqual((self.repo / "README.md").read_text(), BASE_README)
        self.assertEqual(
            self.git("--git-dir", str(self.upstream), "rev-parse", "main"),
            self.start_head,
        )

    def advance_upstream(self) -> tuple[str, str]:
        peer = self.root / "peer"
        self.git("clone", str(self.upstream), str(peer), cwd=self.root)
        readme = BASE_README.replace(
            "Existing personal agent.", "Updated upstream personal agent."
        )
        (peer / "README.md").write_text(readme)
        self.git("add", "README.md", cwd=peer)
        self.git("commit", "-m", "Update from another maintainer", cwd=peer)
        self.git("push", "origin", "main", cwd=peer)
        return self.git("rev-parse", "HEAD", cwd=peer), readme

    def test_success_commits_and_pushes_only_readme(self) -> None:
        result = self.run_runner("ready", "--model", "test-model")
        self.assert_ok(result)
        head = self.git("rev-parse", "HEAD")
        self.assertNotEqual(head, self.start_head)
        self.assertEqual(
            self.git("--git-dir", str(self.upstream), "rev-parse", "main"), head
        )
        self.assertEqual(
            self.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"),
            "README.md",
        )
        self.assertIn(
            "Assistant with web research.", (self.repo / "README.md").read_text()
        )
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertIn("test-model", self.call_log.read_text())
        reports = self.repo / ".git" / "ai-resources-maintenance" / "runs"
        self.assertTrue(list(reports.rglob("result.json")))
        self.assertTrue(list(reports.rglob("README.diff")))
        self.assertTrue(list(reports.rglob("outcome.json")))

    def test_no_changes_does_not_commit(self) -> None:
        self.assert_ok(self.run_runner("no_changes"))
        self.assert_source_unchanged()
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_dry_run_does_not_publish(self) -> None:
        self.assert_ok(self.run_runner("ready", "--dry-run"))
        self.assert_source_unchanged()
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_dry_run_reviews_upstream_without_fast_forwarding_source(self) -> None:
        upstream_head, upstream_readme = self.advance_upstream()
        self.assert_ok(self.run_runner("ready", "--dry-run"))
        self.assertEqual(self.git("rev-parse", "HEAD"), self.start_head)
        self.assertEqual((self.repo / "README.md").read_text(), BASE_README)
        self.assertEqual(
            self.git("--git-dir", str(self.upstream), "rev-parse", "main"),
            upstream_head,
        )
        codex_call = json.loads(self.call_log.read_text().splitlines()[0])
        self.assertEqual(codex_call["readme"], upstream_readme)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_publishing_fast_forwards_source_before_review(self) -> None:
        upstream_head, upstream_readme = self.advance_upstream()
        self.assert_ok(self.run_runner())
        self.assertEqual(self.git("rev-parse", "HEAD^"), upstream_head)
        self.assertEqual(
            self.git("--git-dir", str(self.upstream), "rev-parse", "main"),
            self.git("rev-parse", "HEAD"),
        )
        codex_call = json.loads(self.call_log.read_text().splitlines()[0])
        self.assertEqual(codex_call["readme"], upstream_readme)
        self.assertEqual(
            (self.repo / "README.md").read_text(),
            upstream_readme.replace(
                "Existing assistant.", "Assistant with web research."
            ),
        )
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_blocked_result_cannot_publish(self) -> None:
        self.assert_failed(self.run_runner("blocked"))
        self.assert_source_unchanged()

    def test_dirty_source_refuses_before_codex(self) -> None:
        dirty = BASE_README + "\nUncommitted user edit.\n"
        (self.repo / "README.md").write_text(dirty)
        self.assert_failed(self.run_runner())
        self.assertEqual((self.repo / "README.md").read_text(), dirty)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.start_head)
        self.assertFalse(self.call_log.exists())

    def test_unexpected_file_cannot_publish(self) -> None:
        self.assert_failed(self.run_runner("unexpected_file"))
        self.assert_source_unchanged()
        self.assertFalse((self.repo / "UNEXPECTED.txt").exists())

    def test_incomplete_section_coverage_cannot_publish(self) -> None:
        self.assert_failed(self.run_runner("incomplete"))
        self.assert_source_unchanged()

    def test_incomplete_evidence_cannot_publish(self) -> None:
        result = self.run_runner("incomplete_evidence")
        self.assert_failed(result)
        self.assert_source_unchanged()
        self.assertIn("evidence", (result.stdout + result.stderr).lower())

    def test_empty_readme_cannot_publish(self) -> None:
        result = self.run_runner("empty_readme")
        self.assert_failed(result)
        self.assert_source_unchanged()
        self.assertIn(
            "README title unexpectedly changed", result.stdout + result.stderr
        )

    def test_local_ahead_refuses_before_codex(self) -> None:
        self.git("commit", "--allow-empty", "-m", "Unpublished user commit")
        ahead_head = self.git("rev-parse", "HEAD")
        self.assert_failed(self.run_runner())
        self.assertEqual(self.git("rev-parse", "HEAD"), ahead_head)
        self.assertEqual(
            self.git("--git-dir", str(self.upstream), "rev-parse", "main"),
            self.start_head,
        )
        self.assertFalse(self.call_log.exists())

    def test_concurrent_lock_skips_successfully(self) -> None:
        lock = self.repo / ".git" / "ai-resources-maintenance" / "run.lock"
        lock.parent.mkdir(parents=True)
        with lock.open("w") as file:
            fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assert_ok(self.run_runner())
        self.assert_source_unchanged()
        self.assertFalse(self.call_log.exists())

    def test_timeout_fails_without_publication(self) -> None:
        self.assert_failed(self.run_runner("timeout", "--timeout", "0.1"))
        self.assert_source_unchanged()
        self.assertTrue(self.call_log.exists(), "Codex must start before timing out")

    def test_malformed_output_cannot_publish(self) -> None:
        self.assert_failed(self.run_runner("malformed"))
        self.assert_source_unchanged()

    def test_push_failure_retains_local_commit(self) -> None:
        hook = self.upstream / "hooks" / "pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.assert_failed(self.run_runner())
        self.assertNotEqual(self.git("rev-parse", "HEAD"), self.start_head)
        self.assertEqual(
            self.git("--git-dir", str(self.upstream), "rev-parse", "main"),
            self.start_head,
        )
        self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
