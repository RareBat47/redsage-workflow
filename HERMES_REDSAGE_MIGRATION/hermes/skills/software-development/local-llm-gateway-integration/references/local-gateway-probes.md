# Local Gateway Probes

## Read-only discovery

1. Find the gateway process and listening port with the host OS tools.
2. Probe `GET /health`, `GET /api/health`, and `GET /v1/models` without credentials to distinguish liveness from authenticated API access.
3. Obtain an existing credential through the approved secret store or gateway API-key mechanism; never print it.
4. Query `/v1/models` and filter the response programmatically for requested provider/model prefixes.
5. Send a minimal `POST /v1/chat/completions` request with a harmless exact-response prompt and a small token limit.

## Interpretation

| Observation | Meaning | Next action |
|---|---|---|
| Health 200, models 401 | Gateway is live; API authentication is required | Use the approved key path, then retry catalog discovery |
| Models 200, chat 404 | Gateway is reachable but model/path is wrong | Compare the requested ID and chat path with the live catalog |
| Gateway logs show the intended route, then upstream 403/404 | Hermes and gateway routing worked | Diagnose upstream credentials, account policy, catalog, or anti-bot controls; do not change Hermes providers |
| Minimal direct chat 200 | Gateway-to-upstream inference works for that exact ID | Test the same route through Hermes |
| Hermes reports a different endpoint than configured | A higher-precedence provider definition or named-provider resolver won | Inspect the resolver's supported config shape; prefer the installed bare `custom` provider shape when appropriate |

Always separate catalog availability from inference availability: a model can appear in `/v1/models` yet fail at inference because the upstream account is blocked or lacks permission.
