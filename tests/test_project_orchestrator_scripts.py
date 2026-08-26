from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def skill_root() -> Path:
    candidates = (
        REPO_ROOT / ".agents" / "skills" / "project-orchestrator",
        REPO_ROOT / "_agents_building" / "skills" / "project-orchestrator",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("project-orchestrator skill directory not found")


def run_script(script_name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    script = skill_root() / "scripts" / script_name
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def make_valid_project(root: Path, host: str = "codex") -> Path:
    instruction_name = "AGENTS.md" if host == "codex" else "CLAUDE.md"
    skills_root = Path(".agents/skills") if host == "codex" else Path(".claude/skills")
    (root / instruction_name).write_text(
        "# Project guidance\n\nUse the local sample workflow for sample tasks.\n",
        encoding="utf-8",
    )
    skill = root / skills_root / "sample-workflow"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: sample-workflow\n"
        "description: Handle recurring sample project work when durable validation is needed.\n"
        "---\n\n"
        "# Sample workflow\n\n"
        "Read [checks](references/checks.md) when validating outputs.\n",
        encoding="utf-8",
    )
    (skill / "references" / "checks.md").write_text("# Checks\n", encoding="utf-8")
    return skill / "SKILL.md"


def make_instruction_only_project(root: Path, host: str = "codex") -> None:
    instruction_name = "AGENTS.md" if host == "codex" else "CLAUDE.md"
    (root / instruction_name).write_text(
        "# Project guidance\n\nFollow the current project contract and verified artifacts.\n",
        encoding="utf-8",
    )


class ValidateProjectTests(unittest.TestCase):
    def test_supported_markdown_and_frontmatter_do_not_false_positive(self) -> None:
        frontmatter = (
            "---\n"
            "name: sample-workflow\n"
            "description: Handle recurring sample project work when durable validation is needed.\n"
            "---\n\n"
        )
        cases = {
            "link-title": frontmatter + '[checks](references/checks.md "Checks")\n',
            "fenced-example": frontmatter
            + "```markdown\n[example](references/missing.md)\n```\n",
            "indented-code-example": frontmatter
            + "\n    [example](references/missing.md)\n    TODO: example only\n",
            "indented-code-after-list-scope": frontmatter
            + "- A completed list item.\n\n"
            + "Top-level paragraph ends the list.\n\n"
            + "    [example](references/missing.md)\n",
            "existing-image": frontmatter + "![diagram](references/checks.md)\n",
            "embedded-image": frontmatter + "![pixel](data:image/png;base64,AAAA)\n",
            "existing-reference-style": frontmatter
            + "See [guide][checks].\n\n[checks]: references/checks.md \"Checks\"\n",
            "folded-description": (
                "---\n"
                "name: sample-workflow\n"
                "description: >-\n"
                "  Handle recurring sample project work with durable validation and clear\n"
                "  acceptance evidence across future sessions and supported agent hosts.\n"
                "metadata:\n"
                "  short-description: Sample workflow\n"
                "---\n\n"
                "# Sample workflow\n"
            ),
            "plain-multiline-description": (
                "---\n"
                "name: sample-workflow\n"
                "description:\n"
                "  Handle recurring sample project work with durable validation and clear\n"
                "  acceptance evidence across future sessions and supported agent hosts.\n"
                "---\n\n"
                "# Sample workflow\n"
            ),
            "documented-placeholder": frontmatter
            + "Stop when a file still contains a `TODO:` marker.\n",
            "multiline-code-span": frontmatter
            + "A code span may contain `one line\nTODO: still code` without a placeholder.\n",
        }

        for case, content in cases.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                skill_file = make_valid_project(root)
                skill_file.write_text(content, encoding="utf-8")
                result = run_script("validate_project.py", str(root), "--json")

                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_instruction_only_project_passes_by_default(self) -> None:
        for host in ("codex", "claude"):
            with self.subTest(host=host), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                make_instruction_only_project(root, host)
                result = run_script(
                    "validate_project.py",
                    str(root),
                    "--host",
                    host,
                    "--json",
                )

                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["skill_count"], 0)

    def test_require_skill_rejects_instruction_only_project(self) -> None:
        for host in ("codex", "claude"):
            with self.subTest(host=host), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                make_instruction_only_project(root, host)
                result = run_script(
                    "validate_project.py",
                    str(root),
                    "--host",
                    host,
                    "--require-skill",
                    "--json",
                )

                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertTrue(
                    any("No project-local" in item for item in payload["errors"])
                )

    def test_valid_project_passes_and_returns_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_valid_project(root)
            result = run_script("validate_project.py", str(root), "--json")

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["skill_count"], 1)
            self.assertIn("AGENTS.md", payload["sha256"])

    def test_valid_claude_project_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_valid_project(root, host="claude")
            result = run_script(
                "validate_project.py",
                str(root),
                "--host",
                "claude",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["host"], "claude")
            self.assertIn("CLAUDE.md", payload["sha256"])

    def test_missing_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_file = make_valid_project(root)
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8").replace(
                    "references/checks.md", "references/missing.md"
                ),
                encoding="utf-8",
            )
            result = run_script("validate_project.py", str(root), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertTrue(any("missing linked resource" in item for item in payload["errors"]))

    def test_standalone_placeholder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_file = make_valid_project(root)
            with skill_file.open("a", encoding="utf-8") as handle:
                handle.write("\nTODO: replace this unfinished scaffold.\n")
            result = run_script("validate_project.py", str(root), "--json")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertTrue(
                any("unfinished scaffold placeholder" in item for item in payload["errors"])
            )

    def test_cross_paragraph_backticks_do_not_hide_defects(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_file = make_valid_project(root)
            with skill_file.open("a", encoding="utf-8") as handle:
                handle.write(
                    "\nUse the ` character with care.\n\n"
                    "See [the reference](references/gone.md) for detail.\n"
                    "TODO: fill this in\n"
                    "Another ` character.\n"
                )
            result = run_script("validate_project.py", str(root), "--json")

            self.assertEqual(result.returncode, 1)
            errors = json.loads(result.stdout)["errors"]
            self.assertTrue(any("missing linked resource" in item for item in errors))
            self.assertTrue(any("unfinished scaffold placeholder" in item for item in errors))

    def test_list_indented_blocks_are_scanned_consistently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_file = make_valid_project(root)
            with skill_file.open("a", encoding="utf-8") as handle:
                handle.write(
                    "\n- Add a rule:\n\n"
                    "      see [link A](references/a.md)\n\n"
                    "      see [link B](references/b.md)\n"
                    "      TODO: finish block B\n"
                )
            result = run_script("validate_project.py", str(root), "--json")

            self.assertEqual(result.returncode, 1)
            errors = json.loads(result.stdout)["errors"]
            missing = [item for item in errors if "missing linked resource" in item]
            self.assertEqual(len(missing), 2)
            self.assertTrue(any("references\\a.md" in item or "references/a.md" in item for item in missing))
            self.assertTrue(any("references\\b.md" in item or "references/b.md" in item for item in missing))
            self.assertTrue(any("unfinished scaffold placeholder" in item for item in errors))

    def test_missing_image_and_reference_definition_targets_fail(self) -> None:
        cases = {
            "image": "![diagram](references/gone.png)\n",
            "reference-style": "See [guide][r].\n\n[r]: references/gone.md\n",
            "list-continuation": "- Reference:\n\n    [guide](references/gone.md)\n",
        }
        for case, addition in cases.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                skill_file = make_valid_project(root)
                with skill_file.open("a", encoding="utf-8") as handle:
                    handle.write("\n" + addition)
                result = run_script("validate_project.py", str(root), "--json")

                self.assertEqual(result.returncode, 1)
                errors = json.loads(result.stdout)["errors"]
                self.assertTrue(any("missing linked resource" in item for item in errors))

    def test_unresolved_reference_links_warn_without_failing(self) -> None:
        cases = {
            "array-subscript": ("Index as a[i][j] when walking.\n", "[j]"),
            "undefined-reference": ("See [guide][missing].\n", "[missing]"),
            "collapsed-reference": ("See [guide][].\n", "[guide]"),
        }
        for case, (addition, expected) in cases.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                skill_file = make_valid_project(root)
                with skill_file.open("a", encoding="utf-8") as handle:
                    handle.write("\n" + addition)
                result = run_script("validate_project.py", str(root), "--json")

                self.assertEqual(result.returncode, 0)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "pass")
                self.assertEqual(payload["errors"], [])
                self.assertTrue(
                    any(
                        "unresolved reference link" in item and expected in item
                        for item in payload["warnings"]
                    )
                )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_file = make_valid_project(root)
            with skill_file.open("a", encoding="utf-8") as handle:
                handle.write("\nSee [guide][missing].\n")
            result = run_script("validate_project.py", str(root))

            self.assertEqual(result.returncode, 0)
            self.assertIn("status: pass", result.stdout)
            self.assertIn("WARNING: ", result.stdout)
            self.assertNotIn("ERROR: ", result.stdout)

    def test_short_description_and_name_mismatch_still_fail(self) -> None:
        cases = {
            "short-description": (
                "---\nname: sample-workflow\ndescription: Too short.\n---\n"
            ),
            "name-mismatch": (
                "---\n"
                "name: another-workflow\n"
                "description: Handle recurring sample project work when validation is needed.\n"
                "---\n"
            ),
        }
        for case, content in cases.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                skill_file = make_valid_project(root)
                skill_file.write_text(content, encoding="utf-8")
                result = run_script("validate_project.py", str(root), "--json")

                self.assertEqual(result.returncode, 1)
                errors = json.loads(result.stdout)["errors"]
                expected = "too vague" if case == "short-description" else "does not match folder"
                self.assertTrue(any(expected in item for item in errors))

    def test_missing_project_root_reports_the_path_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "does-not-exist"
            result = run_script(
                "validate_project.py",
                str(root),
                "--host",
                "claude",
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            errors = json.loads(result.stdout)["errors"]
            self.assertEqual(len(errors), 1)
            self.assertIn("Project root does not exist", errors[0])
            self.assertNotIn("CLAUDE.md", errors[0])

    def test_instruction_budget_warning_describes_single_file_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "AGENTS.md").write_text("x" * (33 * 1024), encoding="utf-8")
            result = run_script("validate_project.py", str(root), "--json")

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            warnings = json.loads(result.stdout)["warnings"]
            self.assertEqual(len(warnings), 1)
            self.assertIn("AGENTS.md alone exceeds", warnings[0])


class InstructionStateTests(unittest.TestCase):
    def test_snapshot_without_skill_uses_host_instruction(self) -> None:
        for host, instruction_name in (("codex", "AGENTS.md"), ("claude", "CLAUDE.md")):
            with self.subTest(host=host), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                make_instruction_only_project(root, host)
                created = run_script(
                    "instruction_state.py",
                    "snapshot",
                    str(root),
                    "--host",
                    host,
                    "--task-id",
                    "instruction-only",
                )

                self.assertEqual(created.returncode, 0, created.stderr or created.stdout)
                payload = json.loads(created.stdout)
                self.assertEqual([item["path"] for item in payload["files"]], [instruction_name])

                with (root / instruction_name).open("a", encoding="utf-8") as handle:
                    handle.write("\nChanged guidance.\n")
                stale = run_script("instruction_state.py", "check", str(root))
                self.assertEqual(stale.returncode, 1)
                self.assertTrue(
                    any(item["path"] == instruction_name for item in json.loads(stale.stdout)["stale"])
                )

    def test_instruction_file_override_keeps_agents_alias_compatible(self) -> None:
        for option in ("--instruction-file", "--agents"):
            with self.subTest(option=option), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                custom = root / "PROJECT_GUIDANCE.md"
                custom.write_text("# Custom guidance\n", encoding="utf-8")
                created = run_script(
                    "instruction_state.py",
                    "snapshot",
                    str(root),
                    option,
                    custom.name,
                )

                self.assertEqual(created.returncode, 0, created.stderr or created.stdout)
                payload = json.loads(created.stdout)
                self.assertEqual([item["path"] for item in payload["files"]], [custom.name])

    def test_snapshot_is_current_then_stale_after_guidance_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_file = make_valid_project(root)
            skill_relative = skill_file.relative_to(root).as_posix()

            created = run_script(
                "instruction_state.py",
                "snapshot",
                str(root),
                "--skill",
                skill_relative,
                "--task-id",
                "case-1",
            )
            self.assertEqual(created.returncode, 0, created.stderr or created.stdout)

            current = run_script(
                "instruction_state.py",
                "check",
                str(root),
                "--task-id",
                "case-1",
            )
            self.assertEqual(current.returncode, 0, current.stderr or current.stdout)
            self.assertEqual(json.loads(current.stdout)["status"], "current")

            with (root / "AGENTS.md").open("a", encoding="utf-8") as handle:
                handle.write("\nUpdated instruction.\n")

            stale = run_script("instruction_state.py", "check", str(root))
            self.assertEqual(stale.returncode, 1)
            payload = json.loads(stale.stdout)
            self.assertEqual(payload["status"], "stale")
            self.assertTrue(any(item["path"] == "AGENTS.md" for item in payload["stale"]))


if __name__ == "__main__":
    unittest.main()
