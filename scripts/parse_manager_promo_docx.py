#!/usr/bin/env python3
"""
Extract manager-filled promo guidelines from Word (.docx) for AI / repo ingest.

Usage:
  python3 parse_manager_promo_docx.py path/to/sm_mm_calendar_core_MANAGER.docx
  python3 parse_manager_promo_docx.py ~/Desktop/mm_calendar_subject_docs/*.docx

Output: JSON to stdout (one object per file) with promo blocks keyed by PROMO_ID.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from docx import Document

AI_FIELD_RE = re.compile(r"^AI_FIELD:\s*(\S+)\s*$")
PROMO_START_RE = re.compile(r"^\[PROMO_ID:\s*([^\]]+)\]", re.I)
PROMO_END_RE = re.compile(r"^=== PROMO_BLOCK_END \| id=(\S+) ===")


def _para_texts(doc: Document) -> list[str]:
    out: list[str] = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if t:
            out.append(t)
    return out


def parse_docx(path: Path) -> dict:
    lines = _para_texts(Document(str(path)))
    form: dict[str, str] = {}
    promos: dict[str, dict[str, str | list[str]]] = {}
    current_id: str | None = None
    pending_field: str | None = None
    pending_values: list[str] = []

    def flush_field() -> None:
        nonlocal pending_field, pending_values
        if not pending_field:
            return
        text = "\n".join(pending_values).strip()
        if not text or text.replace("_", "").strip() == "":
            text = ""
        if current_id:
            bucket = promos.setdefault(current_id, {})
            if pending_field.startswith("promo.") and ".promotion_variant_" in pending_field:
                variants = bucket.setdefault("promotion_variants", [])
                if isinstance(variants, list) and text:
                    variants.append(text)
            elif pending_field.startswith("promo.") and ".calendar_example_" in pending_field:
                examples = bucket.setdefault("calendar_examples", [])
                if isinstance(examples, list) and text:
                    examples.append(text)
            else:
                bucket[pending_field] = text
        else:
            form[pending_field] = text
        pending_field = None
        pending_values = []

    for line in lines:
        if PROMO_END_RE.match(line):
            flush_field()
            current_id = None
            continue
        m_start = PROMO_START_RE.search(line)
        if m_start:
            flush_field()
            current_id = m_start.group(1).strip()
            promos.setdefault(current_id, {})
            continue
        m_field = AI_FIELD_RE.match(line)
        if m_field:
            flush_field()
            pending_field = m_field.group(1)
            continue
        if line.startswith("רפרנס מהמערכת") or line.startswith("מילוי שלכם"):
            continue
        if line.startswith("==="):
            continue
        if pending_field and not line.startswith("☐") and not line.endswith(":"):
            if line.startswith(_FILL := "___"):
                continue
            if re.match(r"^\d+\.\s*_+$", line):
                continue
            pending_values.append(line)

    flush_field()
    return {
        "source_file": str(path),
        "form": form,
        "promos": promos,
    }


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]]
    if not paths:
        print("Usage: parse_manager_promo_docx.py <file.docx> [...]", file=sys.stderr)
        return 1
    for path in paths:
        if not path.is_file():
            print(json.dumps({"error": f"not found: {path}"}))
            continue
        print(json.dumps(parse_docx(path), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
