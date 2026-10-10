# Automated maintenance

The skill lives at `.agents/skills/refresh-ai-resources`. Its runner calls `codex exec` explicitly with `$refresh-ai-resources` and the skill path, even if discovery varies between CLI versions.

## Prerequisites

Run as the user with working Codex and Git credentials. Python 3.10+, Git, Codex CLI, Node.js, and `npx` must be on `PATH`. The runner uses `npx --yes --package=prettier@latest prettier` for the latest stable Markdown formatter. It needs network access to Codex, web search, the npm registry, and the upstream. It uses your configured Codex model unless `--model` is supplied.

Configure Git identity and an upstream branch beforehand. Verify authentication interactively outside cron; the job never opens a browser or requests a token. For a GitHub CLI credential helper, `gh auth status` should succeed. Keep credentials out of cron commands and remote URLs.

Use a clean, dedicated checkout. The runner refuses uncommitted files, local-only commits, and divergent history. It fetches upstream and fast-forwards the checkout before a publishing run. Push failures retain the new local commit for recovery.

## Invocation

From any directory:

```bash
python3 /absolute/path/to/AI/.agents/skills/refresh-ai-resources/scripts/run.py
```

Preview a researched and formatted diff without changing the checkout, committing, or pushing:

```bash
python3 /absolute/path/to/AI/.agents/skills/refresh-ai-resources/scripts/run.py --dry-run
```

Dry runs still fetch upstream and require a clean checkout without local-only commits. They research an isolated clone of the upstream state and retain the report and diff.

Optional arguments: `--model MODEL`, `--timeout SECONDS` (default 2700 for Codex research), and `--repo PATH` for another checkout. Git/npm operations have separate 120-second timeouts. Codex receives `workspace-write`, live search, and approval policy `never`; the host performs publishing afterward without disabling the agent sandbox.

Direct skill invocation is also supported:

```bash
codex --search exec -C /absolute/path/to/AI 'Use $refresh-ai-resources to research, update README.md, commit, and push.'
```

Use the Python runner for cron: direct execution can encounter sandbox restrictions on Git metadata or networking even when README editing succeeds.

## Cron example

Weekly on Monday at 06:00 in the cron host's timezone; adjust the path and schedule. This example does not install a job:

```cron
PATH=/home/grischa/.local/bin:/usr/local/bin:/usr/bin:/bin
0 6 * * 1 /usr/bin/python3 /home/grischa/Projects/AI/.agents/skills/refresh-ai-resources/scripts/run.py
```

Cron captures the short output. Configure `MAILTO` or redirect it to your logging system if desired. Overlapping runs for the same repository exit successfully without starting another review.

## Reports and failures

Each run saves `result.json`, `codex.jsonl`, `codex.stderr`, `README.diff`, and `outcome.json` as stages are reached. Files live in the Git common directory under `ai-resources-maintenance/runs/`, outside tracked content. Review or rotate those logs as needed. Temporary research checkouts are removed on success and handled failures; reports and diffs remain.

Exit status is zero for a completed refresh, completed no-change review, successful dry run, or overlapping-job skip. Dependency, authentication, incomplete research, validation, timeout, concurrent-edit, commit, and push failures return nonzero. Missing/malformed output and `blocked` reports cannot publish, even if Codex exits zero.

The runner applies only the validated README diff, checking that the original checkout is still clean and at the expected commit first. It never undoes a local commit after push failure or resolves divergence automatically. Fix the issue, inspect the retained diff/local commit, and perform the appropriate normal push or manual reconciliation before rerunning.

Offline regression checks:

```bash
python3 /absolute/path/to/AI/.agents/skills/refresh-ai-resources/scripts/test_run.py
```

These use temporary local Git repositories and fake Codex/formatter executables; they do not spend model credits, browse the web, or push to GitHub.

The interface and skill location follow [official noninteractive documentation](https://learn.chatgpt.com/docs/non-interactive-mode) and [official skill documentation](https://learn.chatgpt.com/docs/build-skills).
