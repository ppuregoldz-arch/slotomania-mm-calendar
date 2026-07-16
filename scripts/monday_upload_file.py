#!/usr/bin/env python3
"""Upload a file to a Monday update; returns asset id if present in response."""

from __future__ import annotations

import json
import mimetypes
import sys
import uuid
from pathlib import Path

import urllib.request

from monday_client import load_token

FILE_URL = "https://api.monday.com/v2/file"


def upload_to_update(update_id: str, file_path: Path) -> dict:
    token = load_token()
    file_path = file_path.resolve()
    mime, _ = mimetypes.guess_type(str(file_path))
    mime = mime or "application/octet-stream"
    query = (
        "mutation ($file: File!, $updateId: ID!) { "
        "add_file_to_update(file: $file, update_id: $updateId) { id } }"
    )
    variables = {"updateId": str(update_id), "file": None}
    data = file_path.read_bytes()

    boundary = f"----MondayFormBoundary{uuid.uuid4().hex}"
    parts: list[bytes] = []

    def add_part(name: str, content: str | bytes, filename: str | None = None, ctype: str | None = None) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        if filename:
            parts.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode())
            parts.append(f"Content-Type: {ctype or 'application/octet-stream'}\r\n\r\n".encode())
            parts.append(content if isinstance(content, bytes) else content.encode())
        else:
            parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            parts.append(content if isinstance(content, bytes) else content.encode())
        parts.append(b"\r\n")

    add_part("query", query)
    add_part("variables", json.dumps(variables))
    add_part("map", json.dumps({"file": ["variables.file"]}))
    add_part("file", data, filename=file_path.name, ctype=mime)
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        FILE_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": token,
            "API-Version": "2024-10",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def asset_url(asset_id: str, filename: str) -> str:
    return f"https://playtika.monday.com/protected_static/7996532/resources/{asset_id}/{filename}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: monday_upload_file.py <update_id> <file_path>", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(upload_to_update(sys.argv[1], Path(sys.argv[2])), indent=2))
