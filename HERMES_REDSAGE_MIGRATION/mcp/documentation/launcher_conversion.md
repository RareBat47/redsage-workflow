# MCP launcher conversion

The Windows launchers were inspected. Each changed directory to RedSage_v3 and ran `python -m <module>`. The Linux scripts preserve the logical server names and modules while using `$REDSAGE_V2_ROOT`, `$REDSAGE_V3_ROOT`, and `$PYTHON_BIN`. `redsage_kb.sh` runs the v2 `interfaces.mcp_server` module. No `.cmd` or `.exe` launcher is treated as portable.
