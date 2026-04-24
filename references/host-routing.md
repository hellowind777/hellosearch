# Host Routing

## Default order

Use this order unless the user gives a stricter requirement:

1. Current host native web search
2. Current host native page open or fetch

Do not invent a backend that is not actually available in the current session.
Do not depend on extra search infrastructure for this skill to be usable.

## Codex

- Prefer the native web search path available in the current Codex session.
- Fetch or open pages when snippet-level evidence is not enough.
- If live web is disabled in the current session, say that live verification is unavailable.

## Claude Code

- Prefer the current workspace's enabled native web tools.
- Respect project routing rules when a workspace explicitly disables built-in tools.
- Do not assume project-level routing changes apply outside the current workspace.

## OpenClaw

- Prefer the current configured native web provider or built-in web tool.
- Use provider-native search when it already returns source metadata and fetch capability.

## No live-web capability

- State clearly that the current environment cannot verify live web information.
- Offer a best-effort offline answer only if the user still wants one.
- Avoid words such as “latest”, “currently”, or “verified” unless you truly checked the web.
