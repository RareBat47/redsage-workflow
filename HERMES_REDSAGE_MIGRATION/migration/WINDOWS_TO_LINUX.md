# Windows to Linux conversions

- `D:\HIGH LEVELS OF WORKS\RedSage_v2` -> `$HOME/projects/RedSage_v2`.
- `D:\HIGH LEVELS OF WORKS\RedSage_v3` -> `$HOME/projects/RedSage_v3`.
- `C:\Users\arifi\AppData\Local\hermes` -> `$HERMES_HOME` (normally `$HOME/.hermes` on Linux).
- `C:\Python314\python.exe` -> a fresh Linux `$PYTHON_BIN`.
- `.cmd` launchers -> executable scripts under `mcp/linux/`, using direct `python -m` execution.
- Windows `.venv`, `.venv_test`, Hermes venv, `.exe`, PowerShell, Electron caches, and node_modules are excluded and must be recreated.
- The sanitized Hermes config is a template; inspect and adapt paths before installing it.
