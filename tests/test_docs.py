"""Docs and publish-skill contracts, plus the examples/minimal smoke run."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import ORCH, PUBLISH, REPO, run_py  # noqa: E402

README = REPO / "README.md"
ARCH = REPO / "docs" / "architecture.md"
DEPS = REPO / "docs" / "dependencies.md"
MAINT = REPO / "docs" / "maintaining.md"
CHANGELOG = REPO / "CHANGELOG.md"
AGENTS = REPO / "AGENTS.md"
EXAMPLES = REPO / "examples" / "minimal"


def text(path):
    return path.read_text(encoding="utf-8")


class PublishDocsTest(unittest.TestCase):
    """R6: the publish skill states the operational checks it performs."""

    COMMON = {
        "DOM read-back": "DOM read-back",
        "campaign consent": "allow_campaign_topics",
        "campaign default-deny": "missing means false",
        "config cap": "max_upload_mb",
        "live limit": "live upload-page limit",
        "size + hash": "sha256",
        "live-post update": "live post",
        "cover read-back": "cover",
        "declaration read-back": "declaration",
        "cropped screenshot": "cropped",
        "account chrome": "account chrome",
    }

    def test_skill_and_platforms_state_the_checks(self):
        for path in (PUBLISH / "SKILL.md", PUBLISH / "references" / "platforms.md"):
            body = " ".join(text(path).split())  # ignore line wrapping
            for label, token in self.COMMON.items():
                self.assertIn(token, body, f"{path.name} lacks {label}")
            self.assertIn("read back", body.lower(), path.name)

    def test_no_undocumented_fixed_cap(self):
        for path in (PUBLISH / "SKILL.md", PUBLISH / "references" / "platforms.md"):
            self.assertNotIn("about 10 MB", text(path), path.name)

    def test_template_has_preflight_and_status_fields(self):
        body = text(PUBLISH / "references" / "publish-template.md")
        for token in ("File size", "Limit check", "sha256", "Status:",
                      "updated <date>", "published <date>", "read back"):
            self.assertIn(token, body, token)

    def test_template_status_vocabulary(self):
        body = text(PUBLISH / "references" / "publish-template.md")
        for token in ("drafted", "approved", "filled (not published)",
                      "published <date>", "updated <date>", "blocked"):
            self.assertIn(token, body, token)


class DocsConsistencyTest(unittest.TestCase):
    def test_readme_puts_critique_c_before_the_full_build(self):
        body = text(README)
        self.assertIn("before the full build", body)
        self.assertIn("完整成片之前", body)
        self.assertIn("max_retries", body)
        self.assertNotIn("look / board / cut", body)

    def test_architecture_defines_retries_and_m(self):
        body = text(ARCH)
        self.assertIn("automatic retries", body)
        self.assertIn("verification round", body)
        self.assertIn("before the full build", body)
        self.assertIn("score.js", body)
        self.assertIn("manual or agent read", body)
        self.assertIn("cannot detect", body)

    def test_dependencies_required_set_and_check_env(self):
        body = text(DEPS)
        for token in ("Python 3.9+", "drawtext", "Node 18+", "Playwright",
                      "Chromium", "animate", "check_env.py", "npm root -g",
                      "NODE_PATH"):
            self.assertIn(token, body, token)

    def test_maintaining_mentions_tests_and_release(self):
        body = text(MAINT)
        self.assertIn("unittest discover -s tests", body)
        self.assertIn("0.2.0", body)

    def test_agents_layout_mentions_tests(self):
        self.assertIn("tests/", text(AGENTS))

    def test_changelog_has_020(self):
        body = text(CHANGELOG)
        self.assertIn("## [0.2.0]", body)
        self.assertIn("## [Unreleased]", body)
        for token in ("STALE", "verification round", "check_env.py", "tests/"):
            self.assertIn(token, body, token)

    def test_stage_order_is_consistent(self):
        stages = ["distill", "reference", "script", "production", "score",
                  "review", "publish"]
        for path in (README, ARCH):
            blocks = re.findall(r"```(.*?)```", text(path), re.S)
            ordered = []
            for block in blocks:
                positions = [block.find(stage) for stage in stages]
                ordered.append(all(pos >= 0 for pos in positions)
                               and positions == sorted(positions))
            self.assertTrue(any(ordered), f"{path.name}: no pipeline block in order")


class ExamplesTest(unittest.TestCase):
    def test_example_orders_a_before_b(self):
        body = text(EXAMPLES / "README.md")
        self.assertIn("gate A before gate B", body)
        self.assertIn("Expected output", body)
        self.assertLess(
            body.index("cache-miss A"),
            body.index("cache-miss B"),
        )
        data = json.loads((EXAMPLES / "critique" / "A-r1.json").read_text())
        self.assertEqual(data["gate"], "A")

    def test_example_smoke_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo"
            animate = Path(tmp) / "animate" / "templates" / "beat-cut"
            (animate / "src").mkdir(parents=True)
            (animate / "piece.json").write_text(json.dumps({
                "name": "template", "format": "9:16", "style": "isometric",
                "scenes": ["src/scenes.js"]}), encoding="utf-8")
            (animate / "src" / "scenes.js").write_text("// fixture\n", encoding="utf-8")

            init = run_py(ORCH / "init_project.py", project, "--no-git", "--no-link")
            self.assertEqual(init.returncode, 0, init.stdout)
            piece = project / "pieces" / "cache-miss"
            env = {"ANIMATE_DIR": str(Path(tmp) / "animate")}
            new = run_py(ORCH / "new_piece.py", project, "cache-miss",
                         "--input", "Why does walking a matrix by columns run so much slower than by rows?",
                         env=env)
            self.assertEqual(new.returncode, 0, new.stdout)
            for name in ("principle.md", "brief.md"):
                (piece / name).write_text(
                    (EXAMPLES / name).read_text(), encoding="utf-8")
            for name in ("A-r1.json", "B-r1.json"):
                (piece / "critique" / name).write_text(
                    (EXAMPLES / "critique" / name).read_text(), encoding="utf-8")

            proc_a = run_py(REPO / "skills/v2w-critique/scripts/critique_gate.py",
                            piece, "A")
            self.assertEqual(proc_a.returncode, 0, proc_a.stdout)
            proc_b = run_py(REPO / "skills/v2w-critique/scripts/critique_gate.py",
                            piece, "B")
            self.assertEqual(proc_b.returncode, 0, proc_b.stdout)
            proc_v = run_py(ORCH / "validate_piece.py", piece)
            self.assertEqual(proc_v.returncode, 0, proc_v.stdout)


class SetupHelpTest(unittest.TestCase):
    def test_help_hides_the_shell_strictness_line(self):
        proc = subprocess.run(
            ["bash", str(REPO / "setup.sh"), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("set -euo pipefail", proc.stdout)
        self.assertIn("bash setup.sh <project-dir>", proc.stdout)
        self.assertIn("--dev", proc.stdout)


if __name__ == "__main__":
    unittest.main()
