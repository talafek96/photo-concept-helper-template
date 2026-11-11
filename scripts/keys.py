"""API keys, looked up by name on any OS. Never print them.

Order: environment variable (name upper-cased, '-' -> '_': photoprep-gemini-key -> PHOTOPREP_GEMINI_KEY),
then the macOS Keychain (`security`), then the OS credential store via the `keyring` package (Windows
Credential Manager, Linux Secret Service): `python -m pip install keyring`, then store a key with
`python -m keyring set photoprep-gemini-key default` (it prompts, so the key never lands in shell history).
"""
import os, subprocess, sys


def get_key(name):
    v = os.environ.get(name.upper().replace("-", "_"))
    if v:
        return v.strip()
    if sys.platform == "darwin":
        r = subprocess.run(["security", "find-generic-password", "-s", name, "-w"], capture_output=True, text=True)
        if r.stdout.strip():
            return r.stdout.strip()
    try:
        import keyring
        return (keyring.get_password(name, "default") or "").strip()
    except Exception:
        return ""
