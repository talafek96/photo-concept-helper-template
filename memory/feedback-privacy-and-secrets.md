---
name: feedback-privacy-and-secrets
description: "Keys only from the OS credential store (scripts/keys.py), never printed/committed; never send the photographer's email/name to third parties; WhatsApp read-only; model photos never committed"
metadata:
  type: feedback
  origin: template-default
  modified: 2026-11-11
---
Keys: OS credential store via `scripts/keys.py` (`photoprep-gemini-key`, `fal-key`, `openrouter-key`) and `~/.config/google-maps-mcp.env`.
Use generic User-Agents. WhatsApp: read/download only unless the photographer asks to send, and show the text
first. Model photos, WhatsApp media and generated frames stay in gitignored folders.
**Why:** a research subagent once put part of the photographer's email username into a Wikimedia request header.
**How to apply:** every script, subagent brief and commit.
