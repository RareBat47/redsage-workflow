# <Project> — Independent Code Review

Reviewed at commit `<sha>` (`<branch>`, <N> tracked files) by cloning the repo,
installing it in a fresh venv, and running the suite. Everything below is from
real execution, not reading.

## What I measured

| Metric | Value |
|---|---|
| Tracked files | |
| Backend LOC | |
| Frontend LOC | |
| Test files | |
| Suite result (fresh venv, e2e excluded) | |
| Compile / typecheck | |
| CI | |

## The good — and it is genuinely good

<!-- One numbered item per strength. Each MUST name the mechanism, not the vibe.
     Rank code-enforced constraints above prose-documented ones. -->

**1. <Claim>.** <File:line or symbol>. <Why it holds under refactor, not just today>.

## Real bugs I reproduced

<!-- Each entry: cause -> consequence -> command that shows it.
     Include the flake ratio when the failure is nondeterministic. -->

**1. <Title> (<severity>).**
`<file:line>`. <Mechanism>. <Consequence for a user of the software>.
Reproduced: <command> -> <observed result>.

## Where this sits for <purpose>

**What a reviewer sees in 90 seconds:** <the first-impression read>

**The three questions an interviewer will ask, and the answers you should have cold:**

1. "<question>" -> <where in the code to point>
2. "<question>" -> <where in the code to point>
3. "<question>" -> <where in the code to point>

**Highest-leverage next steps, in order:** <2-4 items, most impactful first>

## Honest limits of this review

- Did not exercise: <suite / benchmark / subsystem>
- Reason: <no credential, platform restriction, marked do-not-modify>
- My numbers differ from the documented baseline because: <explicit cause>

<!-- Deliverable is this file as an attachment, not a chat message. -->
