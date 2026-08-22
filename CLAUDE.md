# Apps Homepage — Project Instructions

This project follows the global `AGENTS.md` and `SECURITY_BASELINE.md`.
The notes below cover only what's specific to this repository.

## Version identifier

`api/index.py` — the `APP_VERSION` constant. This is the homepage's own
version, distinct from each catalog tile's `version`, which is fetched
dynamically from that app's own deployment at request time (see README).

## Local development

`api/index.py` is a Flask app deployed as a Vercel function; there's no
local runner for it in this repo. For UI-only preview work, use the
static mock server instead:

- `python preview_server.py 8080` (or `start_preview.bat`) — serves
  `index.html` plus a hardcoded 3-app mock of `/api/apps` on port 8080.
  It does not reflect the real catalog or live version data.

## Known deferred security issue

`api/index.py` line 19 hardcodes a real Vercel API token as the
default fallback value for the `VERCEL_API_TOKEN` environment variable,
violating `SECURITY_BASELINE.md`'s "never hardcode a fallback secret"
rule. This was identified and explicitly deferred pending rotation —
see the platform migration history. Do not remove or rotate without
explicit approval.
