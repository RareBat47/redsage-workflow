# Hermes Routing Shapes

For current Hermes releases, configure a local OpenAI-compatible gateway through the installed CLI and verify the resolved values afterward:

```bash
hermes config set model.default <gateway-model-id>
hermes config set model.provider custom
hermes config set model.base_url http://127.0.0.1:<port>/v1
hermes config set model.key_env <HERMES_SECRET_ENV_NAME>
hermes config set model.api_mode chat_completions
hermes config set providers.custom.base_url http://127.0.0.1:<port>/v1
hermes config set providers.custom.key_env <HERMES_SECRET_ENV_NAME>
hermes config set providers.custom.api_mode chat_completions
hermes config set providers.custom.model <gateway-model-id>
```

Use `hermes config get model` and `hermes config check` after writes. Some releases resolve the active bare `custom` provider from `providers.custom`; a named custom provider can retain or select its own endpoint instead of honoring the top-level override. Test with a harmless `hermes chat -q` and trust the endpoint shown by the runtime, not only the YAML setter output.

Aliases should point at the exact live gateway IDs and remain deterministic:

```bash
hermes config set model.aliases.default custom/<gateway-model-id>
```

Do not put non-secret behavior settings in `.env`; use `config.yaml`. Keep only gateway credentials in `.env` or the approved secret store.
