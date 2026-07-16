#!/usr/bin/env python3
"""Minimal Monday.com GraphQL v2 client. Loads token from .cursor/monday.env."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

API_URL = "https://api.monday.com/v2"
REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".cursor" / "monday.env"


def load_token() -> str:
    token = os.environ.get("MONDAY_API_TOKEN")
    if token:
        return token.strip()
    if not ENV_FILE.is_file():
        sys.exit(f"Missing {ENV_FILE} and MONDAY_API_TOKEN not set")
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() == "MONDAY_API_TOKEN":
            return val.strip().strip('"').strip("'")
    sys.exit("MONDAY_API_TOKEN not found in env file")


def gql(query: str, variables: dict | None = None) -> dict:
    token = load_token()
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": token,
            "API-Version": "2024-10",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())
    if body.get("errors"):
        raise RuntimeError(json.dumps(body["errors"], indent=2))
    return body.get("data") or {}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: monday_client.py '<graphql query>'", file=sys.stderr)
        sys.exit(1)
    data = gql(sys.argv[1])
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
