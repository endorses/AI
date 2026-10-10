#!/usr/bin/env python3
"""Research README updates in isolation, then validate, commit, and push."""

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


class MaintenanceError(Exception):
    pass


def redact(text):
    text = re.sub(r"(https?://)[^/\s]+@", r"\1[redacted]@", text)
    return re.sub(r"gh[pousr]_[A-Za-z0-9_]+", "[redacted]", text)


def command(args, cwd, env, timeout=120, check=True):
    try:
        result = subprocess.run(
            args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise MaintenanceError(f"{args[0]} timed out after {timeout} seconds") from exc
    if check and result.returncode:
        detail = redact((result.stderr or result.stdout).strip())
        raise MaintenanceError(f"{args[0]} failed ({result.returncode}): {detail}")
    return result.stdout.strip() if check else result


def git(repo, env, *args, check=True):
    return command(["git", *args], repo, env, check=check)


def require_clean(repo, env):
    if git(repo, env, "status", "--porcelain", "--untracked-files=all"):
        raise MaintenanceError(
            "Checkout has uncommitted files; refusing to mix changes"
        )


def sections(text):
    return [h for h in re.findall(r"^## (.+)$", text, re.M) if h != "Table of contents"]


def valid_url(url):
    if not isinstance(url, str):
        return False
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
        )
    except ValueError:
        return False


def validate_report(path, original, today):
    try:
        report = json.loads(path.read_text())
        if not isinstance(report, dict):
            raise ValueError("report must be an object")
        if report["status"] == "blocked":
            raise MaintenanceError(f"Research blocked: {report['summary']}")
        if report["status"] not in {"ready", "no_changes"}:
            raise ValueError("unknown status")
        if report["review_date"] != today:
            raise ValueError("review_date must be today's UTC date")
        reviewed = report["reviewed_sections"]
        if not isinstance(reviewed, list) or set(reviewed) != set(sections(original)):
            raise ValueError("reviewed_sections must cover all original categories")
        if not isinstance(report["summary"], str) or not report["summary"].strip():
            raise ValueError("missing review summary")
        evidence = report["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise ValueError("missing research evidence")
        urls = set()
        evidenced_sections = set()
        for item in evidence:
            if (
                not item["section"]
                or not item["topic"]
                or not item["finding"]
                or not valid_url(item["url"])
            ):
                raise ValueError("invalid evidence item")
            urls.add(item["url"])
            evidenced_sections.add(item["section"])
        if not set(sections(original)).issubset(evidenced_sections):
            raise ValueError("opened evidence must cover every original category")
        if not isinstance(report["changes"], list):
            raise ValueError("changes must be a list")
        if report["status"] == "no_changes" and report["changes"]:
            raise ValueError("no_changes report lists edits")
        if report["status"] == "ready" and not report["changes"]:
            raise ValueError("ready report must explain edits")
        for item in report["changes"]:
            if not item["resource"] or not item["reason"]:
                raise ValueError("missing change explanation")
            if item["action"] not in {"add", "update", "remove"}:
                raise ValueError("invalid change action")
            if not item["sources"] or any(url not in urls for url in item["sources"]):
                raise ValueError("each change must cite opened evidence")
        return report
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise MaintenanceError(f"Missing or invalid research report: {exc}") from exc


def validate_readme(path, original, today):
    if path.is_symlink() or not path.is_file():
        raise MaintenanceError("README.md must remain a regular file")
    text = path.read_text()
    if not text.splitlines() or text.splitlines()[0] != original.splitlines()[0]:
        raise MaintenanceError("README title unexpectedly changed")
    headings = re.findall(r"^#{1,6} (.+)$", text, re.M)
    anchors = [re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings]
    if len(anchors) != len(set(anchors)):
        raise MaintenanceError("README has duplicate heading anchors")
    links = re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", text)
    toc = [url[1:] for url in links if url.startswith("#")]
    if len(toc) != len(set(toc)) or set(toc) != set(anchors[2:]):
        raise MaintenanceError("README table of contents does not match its headings")
    if any(not valid_url(url) for url in links if not url.startswith("#")):
        raise MaintenanceError(
            "README has invalid or credential-bearing external links"
        )
    date_label = dt.date.fromisoformat(today).strftime("%B %d, %Y").replace(" 0", " ")
    if f"**Last reviewed: {date_label}.**" not in text:
        raise MaintenanceError("README must record today's completed review date")


def run_codex(workspace, skill, logs, env, model, timeout, today):
    prompt = (
        "Use $refresh-ai-resources. Read "
        ".agents/skills/refresh-ai-resources/SKILL.md explicitly. "
        f"This is a runner-managed unattended review. Today's UTC date is {today}. "
        "Research the live web, review all current categories and emerging candidates, "
        "and update only README.md. The host will format, validate, commit, and push. "
        "Do not run Git mutations, npm, or the runner. Do not ask questions or "
        "initiate "
        "login. Report blocked if research cannot finish. Return the required JSON "
        "with opened-source evidence for all factual edits and category coverage."
    )
    args = [
        "codex",
        "--search",
        "-a",
        "never",
        "exec",
        "--sandbox",
        "workspace-write",
        "-C",
        str(workspace),
        "--ephemeral",
        "--json",
        "--color",
        "never",
        "--output-schema",
        str(skill / "result.schema.json"),
        "-o",
        str(logs / "result.json"),
    ]
    if model:
        args.extend(["--model", model])
    args.append(prompt)
    with (
        (logs / "codex.jsonl").open("w") as stdout,
        (logs / "codex.stderr").open("w") as stderr,
    ):
        process = subprocess.Popen(
            args,
            cwd=workspace,
            env=env,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        try:
            returncode = process.wait(timeout=timeout)
        except BaseException:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise
    if returncode:
        raise MaintenanceError(
            f"Codex failed ({returncode}); see {logs / 'codex.stderr'}"
        )


def refresh(repo, env, logs, args):
    require_clean(repo, env)
    branch = git(repo, env, "symbolic-ref", "--quiet", "--short", "HEAD")
    remote = git(repo, env, "config", "--get", f"branch.{branch}.remote")
    target = git(repo, env, "config", "--get", f"branch.{branch}.merge")
    if remote == "." or not target.startswith("refs/heads/"):
        raise MaintenanceError("Configure an upstream branch on a remote repository")
    # Never print the remote URL: older clones may contain embedded credentials.
    git(repo, env, "fetch", "--quiet", remote)
    upstream = git(repo, env, "rev-parse", "@{upstream}")
    ancestor = git(
        repo, env, "merge-base", "--is-ancestor", "HEAD", upstream, check=False
    )
    if ancestor.returncode:
        raise MaintenanceError(
            "Checkout is ahead of or diverged from upstream; reconcile it first"
        )
    if not args.dry_run:
        git(repo, env, "merge", "--ff-only", upstream)
        git(repo, env, "push", "--dry-run", remote, f"HEAD:{target}")
    baseline = git(repo, env, "rev-parse", "HEAD")
    git(repo, env, "var", "GIT_AUTHOR_IDENT")
    git(repo, env, "var", "GIT_COMMITTER_IDENT")
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()

    with tempfile.TemporaryDirectory(prefix="ai-resources-review-") as temporary:
        workspace = Path(temporary) / "checkout"
        git(
            repo,
            env,
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--single-branch",
            "--branch",
            branch,
            str(repo),
            str(workspace),
        )
        # Clone the local history, then review the already-fetched upstream snapshot.
        git(workspace, env, "checkout", "--quiet", upstream)
        skill = workspace / ".agents/skills/refresh-ai-resources"
        if not (skill / "SKILL.md").is_file():
            raise MaintenanceError(
                "Commit the repo-local skill before running maintenance"
            )
        readme = workspace / "README.md"
        if readme.is_symlink() or not readme.is_file():
            raise MaintenanceError("README.md must be a regular file")
        original = readme.read_text()
        initial_mode = readme.stat().st_mode
        try:
            run_codex(workspace, skill, logs, env, args.model, args.timeout, today)
        except subprocess.TimeoutExpired as exc:
            raise MaintenanceError(
                f"Codex timed out after {args.timeout} seconds"
            ) from exc
        report = validate_report(logs / "result.json", original, today)
        if git(workspace, env, "rev-parse", "HEAD") != upstream:
            raise MaintenanceError("Agent unexpectedly changed Git history")
        changed = git(workspace, env, "diff", "--name-only").splitlines()
        staged = git(workspace, env, "diff", "--cached", "--name-only")
        untracked = git(workspace, env, "ls-files", "--others", "--exclude-standard")
        if staged or untracked or any(name != "README.md" for name in changed):
            raise MaintenanceError("Agent changed files outside its README-only scope")
        if (
            readme.is_symlink()
            or not readme.is_file()
            or readme.stat().st_mode != initial_mode
        ):
            raise MaintenanceError("Agent changed README file type or permissions")
        if report["status"] == "no_changes" and changed:
            raise MaintenanceError("no_changes report does not match the actual diff")
        command(
            [
                "npx",
                "--yes",
                "--package=prettier@latest",
                "prettier",
                "--write",
                "README.md",
            ],
            workspace,
            env,
        )
        validate_readme(readme, original, today)
        git(workspace, env, "diff", "--check")
        diff = git(workspace, env, "diff", "--", "README.md")
        (logs / "README.diff").write_text(diff + ("\n" if diff else ""))
        if args.dry_run:
            return {"status": "dry_run", "summary": report["summary"]}
        if not diff:
            return {"status": "no_changes", "summary": report["summary"]}

        require_clean(repo, env)
        if git(repo, env, "rev-parse", "HEAD") != baseline:
            raise MaintenanceError(
                "Checkout advanced during research; refusing to apply the diff"
            )
        destination = repo / "README.md"
        if destination.is_symlink() or not destination.is_file():
            raise MaintenanceError("Original README is no longer a regular file")
        destination.write_bytes(readme.read_bytes())
        git(repo, env, "diff", "--check")
        git(repo, env, "add", "--", "README.md")
        if git(repo, env, "diff", "--cached", "--name-only").splitlines() != [
            "README.md"
        ]:
            raise MaintenanceError(
                "Staged changes exceed README scope; inspect the checkout"
            )
        git(
            repo,
            env,
            "commit",
            "--only",
            "-m",
            f"docs: refresh AI resources ({today})",
            "--",
            "README.md",
        )
        commit = git(repo, env, "rev-parse", "HEAD")
        git(repo, env, "push", remote, f"HEAD:{target}")
        remote_head = git(
            repo, env, "ls-remote", "--exit-code", remote, target
        ).split()[0]
        if remote_head != commit:
            raise MaintenanceError(
                "Push completed but upstream does not match the new commit"
            )
        return {"status": "pushed", "commit": commit, "summary": report["summary"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parents[4]
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Research and save a diff without publishing",
    )
    parser.add_argument("--model", help="Override the configured Codex model")
    parser.add_argument(
        "--timeout", type=float, default=2700, help="Codex research timeout in seconds"
    )
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    env = dict(
        os.environ,
        GIT_TERMINAL_PROMPT="0",
        GCM_INTERACTIVE="Never",
        GH_PROMPT_DISABLED="1",
        LC_ALL="C",
    )
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=15")
    logs = None
    try:
        for name in ["git", "codex", "npx"]:
            if not shutil.which(name):
                raise MaintenanceError(f"Required command is not on PATH: {name}")
        repo = Path(git(args.repo.resolve(), env, "rev-parse", "--show-toplevel"))
        common = Path(
            git(repo, env, "rev-parse", "--path-format=absolute", "--git-common-dir")
        )
        state = common / "ai-resources-maintenance"
        state.mkdir(mode=0o700, exist_ok=True)
        with (state / "run.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("Skipped: another AI resource review is running")
                return 0
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            logs = state / "runs" / stamp
            logs.mkdir(parents=True, mode=0o700)
            result = refresh(repo, env, logs, args)
            result["logs"] = str(logs)
            (logs / "outcome.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result))
        return 0
    except (MaintenanceError, OSError, ValueError) as exc:
        result = {"status": "failed", "error": redact(str(exc))}
        if logs:
            result["logs"] = str(logs)
            (logs / "outcome.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
