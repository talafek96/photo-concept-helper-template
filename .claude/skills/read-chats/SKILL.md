---
name: read-chats
description: Read the photographer's conversations with a model or producer - WhatsApp (optional WhatsApp MCP) and Instagram DMs (via read-instagram) - for a time window like "since yesterday", including the photos and voice notes they sent, and turn them into shoot facts (deadline, date, what she owns, what she wants, limits). Use whenever the photographer says "read our chat", "see what she sent me", "what did we agree", gives a phone number or a WhatsApp screenshot, or a brief depends on what was said in messages.
---

# Read the chats

Shoot planning happens in chats, so the real brief (deadline, outfits she owns, what she wants to try,
what she won't do) is usually there and not in what the photographer typed to you. Read before asking them.

Which sources this photographer has set up is in `memory/user-photographer.md` → Tools available.

## WhatsApp (optional; tools `mcp__whatsapp__*`)
WhatsApp access needs a local WhatsApp MCP server, e.g. [lharries/whatsapp-mcp](https://github.com/lharries/whatsapp-mcp)
or a fork of it: a Go **bridge** logs in as a linked device (QR code once), stores messages in a local SQLite DB,
and a Python MCP server reads that DB. Set `WHATSAPP_BRIDGE_DIR` (in the shell profile, or `env` in
`.claude/settings.local.json`) to the bridge folder (the one with the bridge's `main.go`).
**No `mcp__whatsapp__*` tools in this session** → WhatsApp isn't set up: say so in one line, read the
Instagram DMs instead, and ask the photographer to paste or screenshot what matters from WhatsApp. Never guess
what a chat says.

1. **Find the chat.** Phone number given → digits only with country code (e.g. "+1 555-010-0199" →
   `15550100199`) → `get_direct_chat_by_contact`. Name given → `search_contacts` (try spellings in every
   language the photographer uses: contact names are often descriptive, e.g. "Maya model Tel Aviv" in the
   local script). Also look for a group with the producer (`list_chats` with her name).
2. **Read the window.** `list_messages(chat_jid=..., after="<ISO date>", sort_by="oldest", limit=200)`.
   "Since yesterday" = `after` = yesterday's date at 00:00 in the photographer's time zone (check `date`;
   don't guess the date). Page with `page=1,2...` until a page comes back short. If the window is quiet, widen
   it once and say so.
3. **Media.** For every image/video: `view_media` to look at it (fast), `download_media` to keep it
   (copy the returned file into `models/<name>/wa/`, named by date). Voice notes: `transcribe_audio`.
   Treat what she sends as her references and her wardrobe/props: describe each one in the profile.
   (Tool names follow the lharries-style server; a fork may name them differently: use what's listed.)
4. **Bridge down?** The MCP only reads a local DB that the Go bridge fills. If the newest message across
   `list_chats` is hours old, or the tools error, check `pgrep -f whatsapp-bridge`. If it isn't running,
   start it as a background job (`cd "$WHATSAPP_BRIDGE_DIR" && go run .`; if the variable is unset, ask the
   photographer where the bridge lives and suggest setting it), wait for "Successfully connected" in its log,
   then give the offline sync a minute or two before reading. That's in scope whenever the photographer asked
   for the chat, because the bridge only receives; sending stays forbidden. If the log shows a QR code, the
   device is unpaired: stop and tell the photographer (they scan it from WhatsApp → Linked devices).

## Instagram DMs
`read-instagram` skill → `scripts/dm.py <handle>`. Same window logic: read `dm.txt`, keep what's after the
date, look at the `dm_NN.jpg` photos. When the photographer names both WhatsApp and Instagram, read both:
one doesn't replace the other.

## Read-only, and why
These are the photographer's private conversations and the people in them can see activity. Don't send,
react, mark as read or reply unless the photographer explicitly asks you to, and then show them the exact
text first.

## What to write down
Into `shoots/<id>/brief.md` (or `models/<name>/profile.md` for things about her, not this shoot):
- **Deadline / dates** with the exact wording and the date it was said ("needs the board by Friday").
- What she **owns** (outfits, props, accessories) with the photo filename.
- What she **wants** to shoot, references she sent, places she suggested.
- **Limits** and comfort level in her words, summarised.
- Open questions for the photographer (in chat to them, never on a shared board).
Summarise; don't paste private messages into tracked files.
