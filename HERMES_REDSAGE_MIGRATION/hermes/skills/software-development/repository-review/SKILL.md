---
name: repository-review
description: "Review an external repo cold: clone, run, verify, report."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, repository, audit, portfolio, hiring, verification]
    related_skills: [codebase-inspection, requesting-code-review, github]
---

# Reviewing an External Repository

Review a repo you did not write — a portfolio project, a candidate submission,
an unfamiliar open-source dependency, a pre-adoption audit. The deliverable is a
written review backed by things you actually ran, not an impression formed by
reading the README.

**vs `requesting-code-review`:** that verifies YOUR changes before commit. This
assesses someone else's whole repository.
**vs `github`:** that posts inline comments on a PR. This produces a standalone
review document.

## When to Use

- "Review this repo", "what do you think of my project", portfolio or candidate assessment
- Deciding whether to adopt or depend on a third-party project
- The user shares a repo URL as a sample of their work

## Core rule: run it, don't read it

Every claim in the review must trace to a command you ran. A README states
intent; the code is behavior. Reviews built from reading alone miss exactly the
things that matter — dead tests, stale docs, flaky suites — and are
indistinguishable from a summary, which the user can get for free.

## Procedure

### 1. Clone to a scratch dir, not the user's workspace

```bash
cd "$LOCALAPPDATA/Temp" && rm -rf <name>-review
git clone --depth 1 <url> <name>-review
git -C <native-path> log --oneline | head
git -C <native-path> branch -a
```

Record the commit you reviewed — a review without a pinned revision is not
reproducible. Note whether `main` is a single commit (see Pitfalls).

**Confirm whose repo it is before you write anything.** A scratch clone is the
right working copy for a genuinely third-party repo, but when the URL turns out
to be the user's own project, their real checkout is the review target — not
your temp copy. Stale scratch clones from earlier sessions persist and look
identical (`git remote -v` matches, same commit), so nothing signals that you
are in the wrong tree. The user's stated local path always wins: locate it
(search the non-temp drives for the project name) and operate there. Ask
before writing if you cannot tell whose repo it is.

### 2. Inventory before installing

```bash
find . -path ./.git -prune -o -type f -print | sed 's/.*\.//' | sort | uniq -c | sort -rn
git ls-files | wc -l
find backend -name '*.py' | xargs wc -l | sort -n | tail -40
find tests -type f | head -40
cat .github/workflows/*.yml
cat .gitignore
```

Read the CI config early — it tells you what the author believes a passing
build means. Then read `.gitignore` against `git ls-files`: a lockfile that is
ignored, or a `.env` that is tracked, are findings in themselves.

### 3. Read the onboarding doc and the ground-truth doc

Serious repos ship a START_HERE / EXPLANATION / ARCHITECTURE doc that declares
its own authority order (commonly "the code wins, then this doc"). Use that
ordering when they disagree, and say so in the review.

### 4. Install in an isolated venv, then run the suite

**Probe the interpreters already present before you build a venv.** The
`python` on PATH is frequently an unrelated environment — some tool's own venv
with none of the project's dependencies — so `No module named pytest` from that
one proves nothing about the repo. Enumerate and test the candidates for the
project's stack:

```bash
which -a python python3
for p in $(which -a python python3); do echo "== $p"; "$p" -c "import pytest; print(pytest.__version__)" 2>&1 | tail -1; done
```

Reuse a candidate that already carries the full stack; build the venv only when
none does, or when you need isolation. State in the review which interpreter you
ran under — a test count taken under a different dependency set is not
comparable to the documented baseline.

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
./.venv/Scripts/python.exe -m pytest -m "not e2e" -q
python -m compileall -q backend
```

Run the tests the way the repo documents, then compare your numbers to the
documented baseline. If they differ, explain the delta (excluded a directory
at collection, deselected a marker, different Python) — never present a
measurement difference as a contradiction.

### 5. Reproduce every failure before characterizing it

One red run tells you a test failed. It does not tell you whether the code is
broken or the test is flaky. Run the specific failing test **three times** and
report the ratio:

```bash
for i in 1 2 3; do ./venv/bin/python -m pytest path::test -q 2>&1 | grep -E "passed|failed"; done
```

"1 failed, 2 passed across three runs" is a finding — it proves nondeterminism
and localizes it. One red run is an anecdote: do not write it up as a bug, and
do not write it up as flakiness either until you have the ratio.

### 6. Trace each failure to the line, then to the user consequence

Get the mechanism (`order_by(created_at, id)` where `id` is a random UUID4 is a
coin-flip tie-break), then the human consequence (the transcript can render the
answer above the question). A finding without a consequence is a nitpick; a
consequence without a cause is unactionable.

### 7. Verify the repo's own issue list against HEAD

If the repo documents "known open issues", check each entry against the current
code. Stale issue lists are common and the direction matters:

- Docs claiming bugs that are already fixed → the author undersells the work.
- Docs claiming health that is actually broken → the author doesn't know the repo.

Either way it is a headline finding: "does the issue list match reality" is the
cheapest available proxy for engineering rigor.

### 8. Write the review

Use `templates/review-template.md`. The section order that works:

1. **What I measured** — metrics table: files, LOC, test files, suite result, CI.
2. **The good** — and say *why* each thing is good. Rank constraints enforced
   in code (schema validators, type-level rejection) above constraints
   documented in prose: the code-enforced one survives refactors.
3. **Real bugs I reproduced** — cause, consequence, and the command that shows it.
4. **Where this sits for its purpose** — hiring, adoption, risk.
5. **Honest limits** — what you could not exercise, and why.

Write the review to a file and deliver it as an attachment. Chat scrolls; a
file does not.

## Always-on rules

- **Pin the revision and state it.** "Reviewed at commit `abc1234`."
- **Separate measured from inferred.** Label anything you did not run.
- **A red suite outranks every feature observation.** For any repo a third
  party will clone, a failing test is the highest-severity finding no matter
  how good the architecture is. Lead with it.
- **Praise must be specific and mechanism-based.** "Good architecture" is
  noise. "The Pydantic field validator rejects the unsafe markers at parse
  time, so no route can execute" is a claim the reader can verify.
- **Never fabricate a run.** If something cannot be exercised, name it and mark
  it as a limit — never as a pass.
- **Offer the fix, don't silently push.** Fix the top findings when asked; get
  the go-ahead before writing to a remote the user owns.
- **Read the repo's claimed guarantees out of the source, not the docs.** When
  the docs and the code disagree, the code wins and the disagreement is itself
  a finding.

## Pitfalls

- **Dev/E2E dependencies declared in the main requirements file.** Browser-test
  packages in `requirements.txt` mean a single blocked native binary aborts
  pytest *collection*, so no unit test runs at all. When a dependency import
  aborts collection, isolate it with `--ignore=tests/e2e` and flag the
  packaging as a finding; state the resulting test count and the cause of the
  delta from the documented baseline explicitly. (Dev/test-only deps belong in
  a separate requirements file — that is the finding, not "the dep is broken".)
- **Reporting a flake from a single run.** See step 5 — three runs, report the ratio.
- **Treating the README as ground truth.** It describes intent and often lags
  the code by several commits.
- **Reviewing the doc's architecture instead of the code's.** The map in
  START_HERE is a claim; open the files it points at.
- **Single-commit repos.** `git log` showing one "feat: initial" commit means
  there is no history to read, so commit hygiene and intent cannot be assessed.
  Note it as a limit and lean on the code and the tests.
- **Counting tests instead of running them.** A large `tests/` tree with a
  suite that aborts at collection is worse than a small green one.
