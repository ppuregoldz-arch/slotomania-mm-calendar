#!/usr/bin/env python3
"""Push current branch to github.com/ppuregoldz-arch/slotomania-mm-calendar (repo must exist)."""
from __future__ import annotations

import os
import subprocess
import sys

OWNER = "ppuregoldz-arch"
REPO = "slotomania-mm-calendar"


def _load_local_token() -> str | None:
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    env_path = os.path.join(root, ".cursor", "github.env")
    if not os.path.isfile(env_path):
        return None
    for line in open(env_path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("GITHUB_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or _load_local_token()
    if not token:
        print("Set GITHUB_TOKEN to a PAT with Contents: write on this repo.", file=sys.stderr)
        sys.exit(1)
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    clone_url = f"https://github.com/{OWNER}/{REPO}.git"
    push_url = clone_url.replace("https://", f"https://x-access-token:{token}@")
    subprocess.run(["git", "remote", "remove", "origin"], cwd=root, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", push_url], cwd=root, check=True)
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
    if not branch:
        subprocess.run(["git", "checkout", "-b", "main"], cwd=root, check=True)
        branch = "main"
    if branch == "master":
        subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True)
        branch = "main"
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=root, check=True)
    subprocess.run(["git", "remote", "set-url", "origin", clone_url], cwd=root, check=True)
    print(f"OK: https://github.com/{OWNER}/{REPO}")


if __name__ == "__main__":
    main()
