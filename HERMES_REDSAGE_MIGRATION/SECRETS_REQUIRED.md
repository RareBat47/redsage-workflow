# Secrets required on the new machine

No secret values are included in this archive. Configure securely, never commit these values:

- `AZURE_FOUNDRY_API_KEY`: Azure Foundry/OpenAI-compatible model access configured by Hermes.
- `CO_API_KEY`: Cohere embeddings used by RedSage v2/v3 KB build/rebuild workflows.
- Local/custom AgentRouter credentials or service authentication, if the local `127.0.0.1:20128/v1` router is retained.
- Any other provider credentials actually selected in Hermes (OpenAI, Anthropic, Google, OpenRouter, Kimi, GLM, MiniMax, etc.).
- GitHub authentication for private repository access/pushes.
- Telegram bot credentials only if Telegram is enabled.
- SSH keys/agent credentials only if remote access is needed.
- OAuth/browser authentication must be completed afresh; do not copy cookies or auth databases.

Enter values through the target system's secret manager, Hermes setup/auth flow, or protected environment files. Never print them.
