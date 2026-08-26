#!/usr/bin/env python3
"""Create or verify an optional instruction-state receipt for managed tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RECEIPT = Path(".project-orchestrator/instruction-state.json")
HOST_INSTRUCTION_FILES = {
    "codex": Path("AGENTS.md"),
    "claude": Path("CLAUDE.md"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_from_root(root: Path, value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def stored_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def snapshot(
    root: Path,
    instruction_file: Path,
    skill: Path | None,
    contract: Path | None,
    task_id: str | None,
    receipt: Path,
) -> dict[str, Any]:
    root = root.resolve()
    files = [instruction_file.resolve()]
    if skill is not None:
        files.append(skill.resolve())
    if contract is not None:
        files.append(contract.resolve())

    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing instruction files: " + ", ".join(missing))

    record = {
        "schema_version": 1,
        "task_id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {"path": stored_path(root, path), "sha256": sha256(path)} for path in files
        ],
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipt.with_suffix(receipt.suffix + ".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, receipt)
    return record


def check(root: Path, receipt: Path, task_id: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    record = json.loads(receipt.read_text(encoding="utf-8-sig"))
    stale: list[dict[str, str]] = []

    if task_id is not None and record.get("task_id") != task_id:
        stale.append(
            {
                "path": "<task-id>",
                "reason": f"expected {task_id!r}, found {record.get('task_id')!r}",
            }
        )

    for item in record.get("files", []):
        raw_path = Path(item["path"])
        path = resolve_from_root(root, raw_path)
        if not path.is_file():
            stale.append({"path": item["path"], "reason": "missing"})
            continue
        actual = sha256(path)
        if actual != item.get("sha256"):
            stale.append({"path": item["path"], "reason": "hash changed"})

    return {
        "status": "current" if not stale else "stale",
        "task_id": record.get("task_id"),
        "receipt": str(receipt),
        "stale": stale,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("project_root", type=Path)
    snapshot_parser.add_argument("--host", choices=sorted(HOST_INSTRUCTION_FILES), default="codex")
    snapshot_parser.add_argument("--skill", type=Path)
    snapshot_parser.add_argument(
        "--instruction-file",
        "--agents",
        dest="instruction_file",
        type=Path,
        help="Override the host-native project instruction file",
    )
    snapshot_parser.add_argument("--contract", type=Path)
    snapshot_parser.add_argument("--task-id")
    snapshot_parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("project_root", type=Path)
    check_parser.add_argument("--task-id")
    check_parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.project_root.resolve()
    try:
        receipt = resolve_from_root(root, args.receipt)
        if args.command == "snapshot":
            instruction_file = args.instruction_file or HOST_INSTRUCTION_FILES[args.host]
            record = snapshot(
                root=root,
                instruction_file=resolve_from_root(root, instruction_file),
                skill=resolve_from_root(root, args.skill) if args.skill else None,
                contract=resolve_from_root(root, args.contract) if args.contract else None,
                task_id=args.task_id,
                receipt=receipt,
            )
            result = {"status": "created", "receipt": str(receipt), **record}
            code = 0
        else:
            result = check(root, receipt, args.task_id)
            code = 0 if result["status"] == "current" else 1
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Instruction-state error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
