---
name: project-agent-identity
description: "Use when dedicating Hermes to one project. Set identity."
version: 1.0.0
metadata:
  hermes:
    editorial_name: "Dedicated Project Agent"
    editorial_description: "Configure a project-focused agent identity without confusing it with repository rules."
    requires_tools: [terminal, read_file, write_file]
    requires_toolsets: []
    requires_plugins: []
---

# Dedicated Project Agent Identity

## Procedure

1. Establish the intended scope before changing configuration: distinguish a dedicated Hermes installation/profile identity from project-specific repository instructions.
2. Resolve the active Hermes home from `HERMES_HOME`; do not assume `~/.hermes` or another profile path.
3. Inspect the active `$HERMES_HOME/SOUL.md` and identify whether it expresses the intended project mission rather than only generic response style.
4. Write a concise `SOUL.md` that states:
   - the dedicated project and its mission;
   - operating principles and safety boundaries;
   - durable project execution context that applies across sessions;
   - the standard for verification and completion claims.
5. Keep repository-local build commands, architecture detail, and code-style rules in repository context files or skills, not in `SOUL.md`.
6. Confirm the exact active path and the write result. State that the identity applies to new sessions; do not imply it retroactively changes the current session prompt.

## Rules and pitfalls

- Inspect the active `SOUL.md` before replacing it — profile homes are isolated, so editing a plausible but inactive path has no effect.
- Use `SOUL.md` for cross-session identity and priorities; use `.hermes.md` or `AGENTS.md` for repository rules because project context discovery and scope differ.
- Preserve explicit safety boundaries in dedicated-product identities: local-first handling, honest uncertainty, human approval for consequential external actions, and real verification before completion claims.
- Do not claim prior strategic discussions have been implemented merely because a memory summary exists — verify the governing identity and configuration files themselves.
- Keep the identity short and durable; detailed procedures belong in skills, and volatile project state belongs in repository files or session context.
