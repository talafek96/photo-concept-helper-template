---
name: reference-tools-and-access
description: "How to reach Instagram (OpenCLI browser bridge), WhatsApp (optional WhatsApp MCP), Google Places, Commons and the image APIs"
metadata:
  type: reference
  modified: 2026-11-11
---
- **Browser:** `opencli browser <session> open|eval|scroll ...` drives the photographer's Chrome (OpenCLI
  extension; `opencli doctor`). Use a distinct session name per agent/job. On Apple Silicon PATH needs
  `/opt/homebrew/bin`. Sites that block curl (Booking, Instagram) work through it; Airbnb listing pages work
  with plain HTTP.
- **Instagram:** `read-instagram` skill (posts from embedded post JSON, DMs via the profile Message button → /direct/t/<id>); `opencli instagram profile|user` hits 429 fast.
- **WhatsApp (optional):** `mcp__whatsapp__*` tools from a whatsapp-mcp server (lharries/whatsapp-mcp style:
  a Go bridge fills a local DB, the MCP reads it). Bridge folder: `$WHATSAPP_BRIDGE_DIR` (see `read-chats`).
  Not set up → say so and use Instagram DMs / what the photographer pastes.
- **Google Places (New):** `scripts/places.py` with the key in `~/.config/google-maps-mcp.env` (the google-maps
  MCP server is often down; the script calls the API directly). Street View API may not be enabled on the key.
- **Commons:** `scripts/commons/` (sequential; 429 on parallel).
- **Image gen:** `references/image-generation.md`.
- What this photographer actually has set up: `user-photographer.md` → Tools available.
