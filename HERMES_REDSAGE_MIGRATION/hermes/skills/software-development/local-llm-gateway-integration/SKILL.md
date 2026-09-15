---
name: local-llm-gateway-integration
description: "Use when routing Hermes through a local LLM gateway."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    editorial_name: Local LLM Gateway Integration
    editorial_description: Safely connect Hermes to a local OpenAI-compatible gateway with deterministic model roles and real verification.
    requires_tools: [terminal, skill_manage]
    requires_toolsets: [file]
    requires_plugins: []
---

# Local LLM Gateway Integration

Use this skill when Hermes must route through a locally running OpenAI-compatible gateway such as OmniRoute, without exposing the gateway publicly or adding direct upstream providers to Hermes.

## Always-on rules

- Inspect the installed Hermes version, gateway process, endpoint, authentication mechanism, live model catalog, and current Hermes configuration before editing anything; never infer a port, model ID, or config schema from a generic tutorial.
- Back up Hermes settings before every routing change. Back up gateway files or databases only when they will be modified; do not alter unrelated gateway providers.
- Keep the gateway local unless the user explicitly requests remote exposure. Prefer `127.0.0.1` over a wildcard bind for local-only integrations.
- Use the gateway's raw, live model IDs with Hermes aliases; do not create gateway combos or aliases unless raw IDs cannot express the required routing.
- Treat Hermes aliases as deterministic convenience names, not quality-based routing. Configure fallbacks only for actual availability failures and never silently replace an unavailable requested model.
- Keep credentials in the protected Hermes secret store or `.env`; never print, read back, or include secret values in reports. Reuse existing credentials only with explicit scope awareness, and prefer a dedicated least-privilege gateway key when creating one is allowed.
- Validate the full chain `Hermes → local gateway → upstream provider → selected model`; a successful `/models` response proves discovery/authentication only, not inference.
- Report partial completion precisely: distinguish local health, catalog availability, Hermes routing, and upstream inference. Do not claim all aliases work when only some routes were tested.

## Procedure

1. **Discover installed surfaces.** Run `hermes --version`, `hermes config path`, `hermes config env-path`, and the gateway's own version/help command if available. Locate the active gateway process and listening ports using OS-native process and network inspection.
2. **Identify the real API contract.** Probe local health and unauthenticated/authenticated `/v1/models` without exposing keys. Confirm the actual OpenAI-compatible chat path, bearer authentication requirement, and the gateway's advertised model IDs. Inspect persisted provider metadata read-only when the dashboard is locked or its CLI generator is unavailable.
3. **Create backups.** Copy the active Hermes config to a timestamped backup before any edit. If gateway configuration must change, back up its database/config using a safe copy or documented export path first. Never overwrite the original backup.
4. **Map requested roles to live IDs.** Build a table of desired role, exact live model ID, and availability. Configure only exact matches. If a requested ID is absent, leave that alias/delegation route unset and ask before using an equivalent; suffixes, free-tier markers, and provider prefixes are semantically significant.
5. **Configure Hermes using its installed syntax.** For current Hermes custom OpenAI-compatible routing, use supported CLI setters rather than hand-editing YAML. The reliable shape is a bare `custom` active provider plus `providers.custom.base_url`, `providers.custom.key_env`, `providers.custom.api_mode`, and `providers.custom.model`. Do not select a named `custom:<name>` provider unless the installed resolver demonstrably supports its endpoint override; named custom resolution may ignore the top-level local endpoint.
6. **Add aliases only for verified IDs.** Use `model.aliases.<name>` with the provider/model form supported by the installed Hermes release. Keep the main default on the required model. Configure `delegation.model`, `delegation.provider`, and `delegation.base_url` only after the delegated model is live and inference-tested. Configure a vision/auxiliary route only when the installed release exposes a separate setting and the model's input capability is verified.
7. **Remove unintended automatic routing.** Inspect `fallback_providers`, provider pools, and gateway combos. Remove only fallback entries that would violate the requested deterministic policy; preserve unrelated provider definitions unless the user explicitly requests their removal.
8. **Validate in layers.** Run `hermes config check`; check local gateway health; authenticate `/v1/models`; send minimal harmless chat probes to each configured live ID; then run a minimal `hermes chat -q` against the default. Record HTTP status, selected model, and whether the request reached the intended upstream. Test delegation through an actual `delegate_task` path when possible rather than assuming config propagation.
9. **Diagnose failures by layer.** A local 401/403 indicates gateway-key scope/authentication; a local 404 indicates endpoint/path/model resolution; a gateway log showing correct routing followed by upstream 403/404/429/5xx is an upstream account, policy, catalog, or quota problem. Do not “fix” an upstream block by changing Hermes to an unrelated provider or silently substituting a model.
10. **Report exactly.** Include versions, local endpoint, active Hermes provider fields, default, delegation and vision status, aliases, validation results by layer, modified files, backups, and unresolved blockers. Never include keys, cookies, tokens, or full secret-bearing config contents.

## Topic references

- `references/local-gateway-probes.md` — read-only endpoint discovery, model-catalog checks, and layered interpretation.
- `references/hermes-routing-shapes.md` — current Hermes custom-provider and deterministic-alias patterns, including named-provider resolution pitfalls.
