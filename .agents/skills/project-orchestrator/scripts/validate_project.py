#!/usr/bin/env python3
"""Validate structural invariants of a managed Codex or Claude project.

This intentionally checks structure, references, and unfinished placeholders.
It does not judge plan quality or prove that an agent followed a skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


FRONTMATTER_BOUNDARY = "---"
TOP_LEVEL_YAML_FIELD = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")
BLOCK_SCALAR_HEADER = re.compile(r"^[>|](?:[1-9])?[+-]?$|^[>|][+-](?:[1-9])?$")
MARKDOWN_LINK = re.compile(r"!?\[[^\]]+\]\(([^)\n]+)\)")
REFERENCE_DEFINITION = re.compile(r"(?im)^[ \t]{0,3}\[([^\]\n]+)\]:[ \t]*(\S.*)$")
REFERENCE_LINK = re.compile(r"!?\[([^\]\n]+)\]\[([^\]\n]*)\]")
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
WINDOWS_DRIVE_PATH = re.compile(r"^[A-Za-z]:[\\/]")
FENCE_START = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)((?:(?!\n[ \t]*\n).)*?)\1", re.DOTALL)
LIST_ITEM = re.compile(r"^[ \t]{0,3}(?:[-+*]|\d+[.)])(?:[ \t]+|$)")
PLACEHOLDER_LINE = re.compile(
    r"(?im)^[ \t]*(?:(?:[-*+]\s+)|(?:#{1,6}\s+))?"
    r"(?:\[TODO(?:[^\]]*)?\]|TODO:|TBD:|REPLACE_ME)(?:\s|$)"
)
HOST_LAYOUTS = {
    "codex": {
        "instruction_file": "AGENTS.md",
        "skills_dir": Path(".agents/skills"),
        "instruction_budget": 32 * 1024,
    },
    "claude": {
        "instruction_file": "CLAUDE.md",
        "skills_dir": Path(".claude/skills"),
        "instruction_budget": None,
    },
}


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frontmatter_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_BOUNDARY:
        return []
    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == FRONTMATTER_BOUNDARY
        )
    except StopIteration:
        return []
    return lines[1:end]


def fold_block_scalar(lines: list[str], style: str) -> str:
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        return ""
    indent = min(len(line) - len(line.lstrip()) for line in nonempty)
    normalized = [line[indent:] if line.strip() else "" for line in lines]
    if style == "|":
        return "\n".join(normalized).strip()

    paragraphs: list[str] = []
    current: list[str] = []
    for line in normalized:
        if line:
            current.append(line.strip())
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return "\n".join(paragraphs).strip()


def plain_block_scalar(lines: list[str]) -> str:
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        return ""
    indent = min(len(line) - len(line.lstrip()) for line in nonempty)
    normalized = [line[indent:] if line.strip() else "" for line in lines]
    if any(
        TOP_LEVEL_YAML_FIELD.match(line) or re.match(r"^-[ \t]+", line)
        for line in normalized
        if line
    ):
        return ""
    return fold_block_scalar(lines, ">")


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = frontmatter_lines(text)
    if not lines:
        return {}

    values: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        match = TOP_LEVEL_YAML_FIELD.match(line)
        if not match:
            index += 1
            continue
        key, raw_value = match.groups()
        value = (raw_value or "").strip()
        if BLOCK_SCALAR_HEADER.fullmatch(value):
            block: list[str] = []
            index += 1
            while index < len(lines) and (not lines[index] or lines[index][0].isspace()):
                block.append(lines[index])
                index += 1
            values[key] = fold_block_scalar(block, value[0])
            continue
        if not value and index + 1 < len(lines) and (
            not lines[index + 1] or lines[index + 1][0].isspace()
        ):
            block = []
            index += 1
            while index < len(lines) and (not lines[index] or lines[index][0].isspace()):
                block.append(lines[index])
                index += 1
            values[key] = plain_block_scalar(block)
            continue
        values[key] = value.strip('"').strip("'")
        index += 1
    return values


def leading_indent(line: str) -> int:
    columns = 0
    for character in line:
        if character == " ":
            columns += 1
        elif character == "\t":
            columns += 4 - (columns % 4)
        else:
            break
    return columns


def markdown_prose(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == FRONTMATTER_BOUNDARY:
        try:
            end = next(
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() == FRONTMATTER_BOUNDARY
            )
            lines = lines[end + 1 :]
        except StopIteration:
            lines = []
    prose: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    in_indented_code = False
    previous_blank = True
    list_context_active = False
    for line in lines:
        match = FENCE_START.match(line)
        if match:
            marker = match.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
                continue
            if marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = None
                fence_length = 0
                continue
        if fence_char is not None:
            continue

        is_blank = not line.strip()
        indent = leading_indent(line)
        if in_indented_code:
            if is_blank or indent >= 4:
                continue
            in_indented_code = False
        if LIST_ITEM.match(line):
            list_context_active = True
        elif not is_blank and indent < 4:
            list_context_active = False
        if (
            not is_blank
            and indent >= 4
            and previous_blank
            and not list_context_active
        ):
            in_indented_code = True
            continue

        prose.append(line)
        previous_blank = is_blank
    return INLINE_CODE.sub("", "\n".join(prose))


def markdown_destination(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")].strip()
    return re.split(r"(?<!\\)\s+", target, maxsplit=1)[0].replace(r"\ ", " ")


def reference_label(value: str) -> str:
    return " ".join(value.split()).casefold()


def markdown_links(skill_file: Path, text: str) -> tuple[list[Path], list[str]]:
    paths: list[Path] = []
    prose = markdown_prose(text)
    definitions = {
        reference_label(label): raw_target
        for label, raw_target in REFERENCE_DEFINITION.findall(prose)
    }
    raw_targets = list(MARKDOWN_LINK.findall(prose))
    raw_targets.extend(definitions.values())
    for raw_target in raw_targets:
        target = markdown_destination(raw_target).split("#", 1)[0].strip()
        if (
            not target
            or target.startswith("#")
            or (URI_SCHEME.match(target) and not WINDOWS_DRIVE_PATH.match(target))
        ):
            continue
        paths.append((skill_file.parent / target).resolve())

    unresolved: list[str] = []
    for text_label, target_label in REFERENCE_LINK.findall(prose):
        label = target_label or text_label
        if reference_label(label) not in definitions:
            unresolved.append(label)
    return paths, unresolved


def validate_project(
    root: Path,
    require_contract: bool = False,
    host: str = "codex",
    require_skill: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    hashes: dict[str, str] = {}
    layout = HOST_LAYOUTS[host]

    if not root.exists():
        return {
            "status": "fail",
            "root": str(root),
            "host": host,
            "skill_count": 0,
            "errors": [f"Project root does not exist: {root}"],
            "warnings": [],
            "sha256": {},
        }
    if not root.is_dir():
        return {
            "status": "fail",
            "root": str(root),
            "host": host,
            "skill_count": 0,
            "errors": [f"Project root is not a directory: {root}"],
            "warnings": [],
            "sha256": {},
        }

    instruction_name = str(layout["instruction_file"])
    instruction_file = root / instruction_name
    if not instruction_file.is_file():
        errors.append(f"Missing project {instruction_name}")
    else:
        instruction_text = read_utf8(instruction_file)
        if not instruction_text.strip():
            errors.append(f"{instruction_name} is empty")
        instruction_budget = layout["instruction_budget"]
        if instruction_budget and instruction_file.stat().st_size > instruction_budget:
            warnings.append(
                f"{instruction_name} alone exceeds Codex's default 32 KiB combined instruction budget"
            )
        hashes[instruction_name] = sha256(instruction_file)

    skills_dir = root / Path(layout["skills_dir"])
    skill_files = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []
    if require_skill and not skill_files:
        errors.append(f"No project-local {Path(layout['skills_dir']).as_posix()}/*/SKILL.md found")

    names: dict[str, Path] = {}
    for skill_file in skill_files:
        relative = skill_file.relative_to(root).as_posix()
        text = read_utf8(skill_file)
        prose = markdown_prose(text)
        metadata = parse_frontmatter(text)
        name = metadata.get("name", "")
        description = metadata.get("description", "")

        if not name:
            errors.append(f"{relative}: missing frontmatter name")
        elif name != skill_file.parent.name:
            errors.append(
                f"{relative}: frontmatter name {name!r} does not match folder {skill_file.parent.name!r}"
            )
        elif name in names:
            errors.append(f"Duplicate skill name {name!r}: {names[name]} and {skill_file}")
        else:
            names[name] = skill_file

        if not description or len(description) < 20:
            errors.append(f"{relative}: description is missing or too vague")
        if PLACEHOLDER_LINE.search(prose):
            errors.append(f"{relative}: unfinished scaffold placeholder found")

        linked_paths, unresolved_labels = markdown_links(skill_file, text)
        for linked_path in linked_paths:
            if not linked_path.exists():
                errors.append(f"{relative}: missing linked resource {linked_path}")
        for label in unresolved_labels:
            warnings.append(f"{relative}: unresolved reference link [{label}]")

        hashes[relative] = sha256(skill_file)

    contract_file = root / ".project-orchestrator" / "PROJECT.md"
    if require_contract and not contract_file.is_file():
        errors.append("Managed project contract is required but .project-orchestrator/PROJECT.md is missing")
    if contract_file.is_file():
        if not read_utf8(contract_file).strip():
            errors.append(".project-orchestrator/PROJECT.md is empty")
        hashes[contract_file.relative_to(root).as_posix()] = sha256(contract_file)

    return {
        "status": "pass" if not errors else "fail",
        "root": str(root),
        "host": host,
        "skill_count": len(skill_files),
        "errors": errors,
        "warnings": warnings,
        "sha256": hashes,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--host", choices=sorted(HOST_LAYOUTS), default="codex")
    parser.add_argument("--require-contract", action="store_true")
    parser.add_argument("--require-skill", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = validate_project(
            args.project_root,
            require_contract=args.require_contract,
            host=args.host,
            require_skill=args.require_skill,
        )
    except (OSError, UnicodeError) as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARNING: {message}")
        print(f"skills: {result['skill_count']}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
