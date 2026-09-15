# Runtime requirements

- Hermes: Python >=3.11,<3.14; use a fresh Linux virtual environment.
- RedSage v2/v3: recreate fresh Linux Python environments from their requirement files; current Windows audit interpreter was Python 3.14.7, but verify package compatibility on the target.
- Frontend: install Node.js/npm compatible with the lockfile; run `npm ci` in RedSage_v2/frontend.
- Linux system basics: git, Python development tooling/venv, build tools for any package without a wheel, Node.js/npm, and optional Docker only if later required.
- Do not copy any Windows virtual environment or executable.
