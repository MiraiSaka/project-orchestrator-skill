from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "project-orchestrator"
PUBLIC_ROOTS = (
    SKILL_ROOT,
    REPO_ROOT / "evals",
    REPO_ROOT / "tests",
    REPO_ROOT / ".github",
)
PUBLIC_FILES = (REPO_ROOT / "README.md", REPO_ROOT / "LICENSE")
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".txt"}
ABSOLUTE_LOCAL_PATH_PATTERNS = (
    re.compile(r"(?i)(?<![A-Za-z0-9])[A-Z]:[\\/]"),
    re.compile(r"(?<![\w/])/(?:Users|home)/[^/\s]+/"),
)


def public_text_files() -> list[Path]:
    files = [path for path in PUBLIC_FILES if path.is_file()]
    for root in PUBLIC_ROOTS:
        if root.is_dir():
            files.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    return sorted(set(files))


class PublicPackageTests(unittest.TestCase):
    def test_skill_frontmatter_and_links(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8-sig")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("\nname: project-orchestrator\n", text)
        self.assertRegex(text, r"(?m)^description:\s*\S")

        for raw_target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = raw_target.split("#", 1)[0]
            if target and "://" not in target:
                self.assertTrue((skill_file.parent / target).is_file(), target)

    def test_public_files_contain_no_absolute_local_paths(self) -> None:
        for path in public_text_files():
            text = path.read_text(encoding="utf-8-sig")
            for pattern in ABSOLUTE_LOCAL_PATH_PATTERNS:
                self.assertIsNone(pattern.search(text), f"{path}: {pattern.pattern}")

    def test_local_evidence_is_git_ignored(self) -> None:
        ignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8-sig")
        for entry in ("/test1/", "/test2/", "/HANDOFF.md", "/全局项目编排Skill开发计划.md"):
            self.assertIn(entry, ignore)


if __name__ == "__main__":
    unittest.main()
