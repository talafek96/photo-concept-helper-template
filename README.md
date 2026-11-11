# photo-concept-helper

> Owner: {{PHOTOGRAPHER_NAME}} ({{INSTAGRAM_HANDLE}}), {{HOME_BASE}}. *(Filled in at onboarding.)*

A creative director and shoot producer for photographers, running as a Claude Code agent in its own repo
("repo-as-agent"). Open the repo in Claude Code and say what's coming up: *"new shoot with @handle in
December"*, *"more bold ideas for Maya"*, *"find a real location for concept 3"*, *"remake frame 4, it doesn't
look like her"*.

It will:
1. **Intake** the shoot with a few questions (model, team, date, goal, boldness, budget, who sees the board).
2. **Study the model**: her Instagram (through your Chrome via OpenCLI), your WhatsApp chat with her and the
   references she sent (read-only), then write her profile and pick identity reference photos.
3. **Develop concepts**: continuous stories in one real location, rooted in something true, in season, lit
   with your kit.
4. **Scout real locations**: recent dated photos, Commons photos with credits, Google Maps pins, permits,
   cheap bookable interiors screened by photo at scale.
5. **Generate storyboards** of the actual model (Nano Banana Pro, directly or via OpenRouter; fal.ai Seedream
   as a weaker last resort),
   reviewed for likeness and continuity.
6. **Draw lighting diagrams** per frame: a metric plan on the real ground, rendered as a camera-POV view and an
   overview, in a style you choose (`references/diagram-style/`), checked against the frame.
7. **Publish a board** (a claude.ai artifact, in your language, RTL or LTR) you can share with the producer
   and model.
8. **Learn from your feedback**: every correction becomes a rule in `memory/`, committed and pushed, and
   injected into every future session.

It ships with the habits another photographer already taught it (the `memory/` rules and `PITFALLS.md`),
as **defaults you can override**: tell it you see things differently and it rewrites the rule.

## 1. Create your own repo (don't clone this one)
This repo is a shared **template**. You can't push to it, and your shoots, models and memory must not end up
here.
Make it **private**: it will hold notes about the people you photograph. Either way works:

**From the terminal** (the [GitHub CLI](https://cli.github.com), after `gh auth login`): creates the repo
and clones it, with `origin` already pointing at it:
```bash
gh repo create my-photo-concepts --template talafek96/photo-concept-helper-template --private --clone
cd my-photo-concepts
```

**On the website:** click **Use this template → Create a new repository**, choose **Private**, then clone
your new repo.

Work only in your new repo.

If you cloned the template by mistake, the agent warns you at start-up; fix it with
`git remote set-url origin <url-of-your-new-repo>`.

## 2. Prerequisites
Written for macOS; **Windows** works too, with the differences listed under *On Windows* below.

**Required**
- [Claude Code](https://docs.claude.com/en/docs/claude-code) (a claude.ai plan with Artifacts, for the boards).
- Python 3 with Pillow, and [uv](https://docs.astral.sh/uv/):
  ```bash
  brew install python uv
  python3 -m pip install --user Pillow   # if pip refuses (externally managed): brew install pillow
  python3 -c "import PIL; print('Pillow ok')"
  ```
- At least one image-generation key, stored in the macOS Keychain under these exact names (the scripts look
  them up by name). Each command prompts for the key, so it never lands in your shell history:
  ```bash
  security add-generic-password -a "$USER" -s photoprep-gemini-key -w   # Google AI Studio key (Nano Banana Pro); best likeness
  security add-generic-password -a "$USER" -s openrouter-key -w         # OpenRouter key; the same Nano Banana Pro without Google's daily limit
  security add-generic-password -a "$USER" -s fal-key -w                # fal.ai key (Seedream); forgiving but less coherent, last resort
  ```
  Gemini + OpenRouter is the recommended pair (same model, two quotas); add fal only if you want a fallback for
  content Google refuses. To replace a key, add `-U`. Check one exists (without printing it):
  `security find-generic-password -s fal-key >/dev/null && echo ok`.
  The scripts also read keys from environment variables of the same name in capitals (`PHOTOPREP_GEMINI_KEY`,
  `OPENROUTER_KEY`, `FAL_KEY`) and from the Windows/Linux credential store (`scripts/keys.py`).
- [OpenCLI](https://github.com/jackwener/opencli) + its Chrome extension (Browser Bridge), for Instagram
  (posts, highlights, DMs) and listing sites, through your own logged-in Chrome:
  ```bash
  npm install -g @jackwener/opencli      # needs Node.js: brew install node
  # install the Browser Bridge extension in Chrome (see the OpenCLI README), log in to Instagram in that profile
  opencli doctor                         # must show: Extension: connected
  ```

**Optional**
- **Google Maps / Places** (map pins and current photos of places): a Google Cloud API key with
  *Places API (New)* enabled, in `~/.config/google-maps-mcp.env`:
  ```bash
  mkdir -p ~/.config && printf 'GOOGLE_MAPS_API_KEY=%s\nPLACES_REGION_CODE=%s\n' '<your key>' 'IL' > ~/.config/google-maps-mcp.env
  chmod 600 ~/.config/google-maps-mcp.env
  ```
  (`PLACES_REGION_CODE` is your two-letter country code.) The same file can feed a Google Maps MCP server if
  you use one; the scripts call the API directly either way.
- **WhatsApp** (read your chats with models, including photos and voice notes): a local WhatsApp MCP server
  such as [lharries/whatsapp-mcp](https://github.com/lharries/whatsapp-mcp) (Go bridge + Python MCP; needs
  `brew install go`). Follow its README, pair it by scanning the QR code from WhatsApp → Linked devices, add
  the MCP server to Claude Code, and tell the agent where the bridge lives:
  `export WHATSAPP_BRIDGE_DIR=~/path/to/whatsapp-mcp/whatsapp-bridge` (in `~/.zshrc`). Without it, the agent
  reads Instagram DMs and whatever you paste.

### On Windows
- Install [Git for Windows](https://git-scm.com/download/win) (Claude Code uses its Git Bash; the memory hook
  is a bash script), [Python 3](https://www.python.org/downloads/) (tick "Add to PATH"), Node.js and the GitHub
  CLI: `winget install Git.Git Python.Python.3.12 OpenJS.NodeJS GitHub.cli astral-sh.uv`.
- Pillow: `py -m pip install Pillow keyring`.
- **Keys** go in Windows Credential Manager instead of the Keychain (each command prompts for the key):
  ```powershell
  py -m keyring set photoprep-gemini-key default
  py -m keyring set openrouter-key default
  py -m keyring set fal-key default
  ```
  Or set them as user environment variables (`PHOTOPREP_GEMINI_KEY`, ...) in System → Environment Variables.
- If `python3` isn't found in Git Bash, run `py` once to check Python is installed, then add an alias:
  `echo "alias python3=py" >> ~/.bashrc`.
- Maps key file: `%USERPROFILE%\.config\google-maps-mcp.env` (same content as above).
- OpenCLI and its Chrome extension work the same. The WhatsApp bridge (Go) builds on Windows too but needs a C
  compiler for SQLite (see its README); it's optional.

## 3. Say hi
Open Claude Code in **your** repo and say hi. On the first run it interviews you (a few questions at a time):
your name and Instagram, where you're based, languages and board language, what you shoot and your style, your
gear, your usual team, how bold you go, your budget habits, and which of the tools above you have. It can read
your own Instagram to learn your style. Then it writes your profile, gear list and region files, tells you
which optional tools are missing and how to add them, and commits.

After that, just tell it about your next shoot.

## Layout
```
CLAUDE.md                 role, workflow, hard rules, how it adapts to you
.claude/skills/           onboard · new-shoot · study-model · read-instagram · read-chats · develop-concepts ·
                          scout-locations · generate-storyboard · lighting-diagram · publish-board · learn-from-feedback
.claude/agents/           location-scout (parallel research subagent)
.claude/hooks/            inject-memory.sh (SessionStart: memory, pitfalls, first-run and template warnings)
memory/                   durable lessons (MEMORY.md index); user-photographer.md = you
references/               creative principles · gear · image generation · <region> locations + seasonality (Israel as the example)
models/<name>/            profile.md, identity.txt (+ gitignored refs/, ig/, wa/)
shoots/<id>/              brief, concepts/*.json, board/board.json + index.html, notes.md
scripts/                  gen · sheet · places · commons/ · listings/ · diagram · build_board
templates/                board CSS + example board.json, example concept, model profile/identity templates
```

Private images (model photos, WhatsApp media, generated frames, downloaded location photos) are gitignored
and stay on the machine that made them.
