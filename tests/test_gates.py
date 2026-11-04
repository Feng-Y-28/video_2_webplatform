"""validate_piece.py: gate labels, order, revalidation and artefact rules."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import (ORCH, REPO, load_module, new_piece_dir, new_project,  # noqa: E402
                      run_py, rubric_items)

mod = load_module(ORCH / "validate_piece.py", "validate_piece_under_test")


def checked(labels):
    return "# piece — status\n\n## Gates\n" + "\n".join(
        f"- [x] {label}" for label in labels) + "\n"


def write_status(piece, labels):
    piece.mkdir(parents=True, exist_ok=True)
    (piece / "STATUS.md").write_text(checked(labels), encoding="utf-8")


def touch(path, text="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class GateLabelsTest(unittest.TestCase):
    def test_all_labels_parse_when_ticked(self):
        labels = [label for label, _ in mod.GATES]
        parsed = mod.gates(checked(labels))
        self.assertTrue(all(parsed[label] for label in labels), parsed)

    def test_user_suffix_is_parsed(self):
        status = "- [x] sample approved (user)\n"
        parsed = mod.gates(status)
        sample = [label for label, key in mod.GATES if key == "sample"][0]
        self.assertTrue(parsed[sample])

    def test_template_labels_are_known(self):
        template = (REPO / "skills/v2w-orchestra/templates/STATUS.md").read_text()
        labels = re.findall(r"^- \[[ xX]\] (.+)$", template, re.M)
        self.assertEqual(len(labels), len(mod.GATES), labels)
        for label in labels:
            self.assertTrue(
                any(label == known or label.startswith(known)
                    for known, _ in mod.GATES),
                f"template label not known by validate_piece: {label!r}",
            )


class GateOrderTest(unittest.TestCase):
    def test_illegal_order_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = new_project(tmp)
            piece = new_piece_dir(project)
            write_status(piece, ["C visual critique passed"])
            proc = run_py(ORCH / "validate_piece.py", piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("ILLEGAL", proc.stdout)
            self.assertIn("ticked while", proc.stdout)

    def test_sample_before_gates_is_illegal(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = new_project(tmp)
            piece = new_piece_dir(project)
            write_status(piece, ["sample approved"])
            proc = run_py(ORCH / "validate_piece.py", piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("ILLEGAL", proc.stdout)

    def test_ticked_gate_is_revalidated(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = new_project(tmp)
            piece = new_piece_dir(project)
            write_status(piece, ["A content critique passed"])
            # principle.md missing on purpose
            proc = run_py(ORCH / "validate_piece.py", piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("principle.md", proc.stdout)

    def test_open_gate_with_waiver_is_not_illegal(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = new_project(tmp)
            piece = new_piece_dir(project)
            (piece / "STATUS.md").write_text(
                "# demo\n\n## Gates\n"
                "- [ ] A content critique passed\n"
                "- [x] B script critique passed\n"
                "- [ ] C visual critique passed\n"
                "- [ ] music checks passed\n"
                "- [ ] review checks passed\n"
                "- [ ] D final critique passed\n"
                "- [ ] sample approved\n"
                "- [ ] published\n\n"
                "## User waivers\n"
                "- A accepted with open issues by user (2026-01-01): legacy\n",
                encoding="utf-8")
            proc = run_py(ORCH / "validate_piece.py", piece)
            self.assertNotIn("ILLEGAL", proc.stdout)
            self.assertIn("user waiver", proc.stdout)


class ReviewArtefactTest(unittest.TestCase):
    def test_missing_review_artefacts_fail(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "piece"
            piece.mkdir()
            mod.check_review(piece, out)
        messages = " ".join(msg for _, msg in out)
        self.assertTrue(any(level == "FAIL" for level, _ in out), out)
        self.assertIn("shot", messages)
        self.assertIn("phone.jpg", messages)

    def test_complete_review_artefacts_pass(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "piece"
            touch(piece / "review" / "shot1-sheet.jpg")
            touch(piece / "review" / "phone.jpg")
            touch(piece / "renders" / "share.mp4")
            touch(piece / "LOG.md",
                  "# log\n\n## v1 review\nChecks: all pass\nWeakest shot: hook\n")
            mod.check_review(piece, out)
        self.assertFalse([m for level, m in out if level == "FAIL"], out)


class DAndPublishedRulesTest(unittest.TestCase):
    def test_d_gate_needs_publish_md(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "piece"
            piece.mkdir()
            mod.check_ticked("D", piece, out, legacy=True)
        self.assertIn("publish.md", " ".join(msg for _, msg in out))
        self.assertTrue(any(level == "FAIL" for level, _ in out), out)

    def test_sample_needs_d_critique_video_and_copy(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "piece"
            (piece / "critique").mkdir(parents=True)
            mod.check_artifacts("sample", piece, out)
            mod.check_sample_critique(piece, out, legacy=False)
        messages = " ".join(msg for _, msg in out)
        self.assertIn("D critique", messages)
        self.assertIn("share.mp4", messages)
        self.assertIn("publish.md", messages)

    def _failed_d_piece(self, piece, waiver):
        (piece / "critique").mkdir(parents=True)
        items = [{"id": key, "score": 2 if key == "D1" else 5,
                  "evidence": "fixture", "fix": "fixture"} for key in rubric_items("D")]
        (piece / "critique" / "D-r1.json").write_text(json.dumps({
            "gate": "D", "round": 1, "schema": 1, "items": items,
            "takeaway": "fixture", "must_fix": [], "summary": "fixture",
        }), encoding="utf-8")
        if waiver:
            (piece / "STATUS.md").write_text(
                "# demo\n\n## User waivers\n"
                "- D accepted with open issues by user (2026-01-01): D1\n",
                encoding="utf-8")

    def test_sample_waiver_allows_failed_d(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "piece"
            self._failed_d_piece(piece, waiver=True)
            mod.check_sample_critique(piece, out, legacy=False)
        self.assertFalse([m for level, m in out if level == "FAIL"], out)
        self.assertTrue(any("waiver" in msg for _, msg in out), out)

    def test_sample_without_waiver_fails_on_failed_d(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "piece"
            self._failed_d_piece(piece, waiver=False)
            mod.check_sample_critique(piece, out, legacy=False)
        self.assertTrue(any(level == "FAIL" for level, _ in out), out)

    def test_published_needs_an_export(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            project = new_project(tmp)
            (project / "exports").mkdir()
            piece = new_piece_dir(project)
            mod.check_published(piece, out)
        self.assertTrue(any("exports" in msg for _, msg in out), out)

    def test_published_status_with_url_passes(self):
        out = []
        with tempfile.TemporaryDirectory() as tmp:
            project = new_project(tmp)
            (project / "exports").mkdir()
            touch(project / "exports" / "demo.mp4")
            piece = new_piece_dir(project)
            touch(piece / "publish.md",
                  "# publish\n\n**Status:** published 2026-01-01 https://example.org/post\n")
            mod.check_published(piece, out)
        self.assertFalse([m for level, m in out if level == "FAIL"], out)


class SourcedLinesTest(unittest.TestCase):
    def test_top_level_indented_and_ordered_lines(self):
        out = []
        block = "\n".join([
            "- Cache line is 64 B — https://example.org/ref",
            "  - 16 floats per line — simplified example: 32-bit floats",
            "1. Row walk uses 16/16 — derived",
            "- See Table 2 for the timing",
        ])
        mod.sourced_lines(block, out, "fixture")
        self.assertFalse([m for level, m in out if level == "FAIL"], out)

    def test_chinese_and_internal_sources(self):
        out = []
        block = "\n".join([
            "- 7 个阶段 — v2w-orchestra/SKILL.md → Pipeline",
            "- 示意评分 4/5/2 — simplified example: rounded",
            "- 结果 — 推导",
            "- 数字 — 表 2",
            "- 评审 — v2w-critique/SKILL.md",
        ])
        mod.sourced_lines(block, out, "fixture")
        self.assertFalse([m for level, m in out if level == "FAIL"], out)

    def test_bare_source_word_is_not_enough(self):
        out = []
        mod.sourced_lines("- 42 — source", out, "fixture")
        self.assertTrue(any(level == "FAIL" for level, _ in out), out)

    def test_unsourced_line_fails(self):
        out = []
        mod.sourced_lines("- this number has no source", out, "fixture")
        self.assertTrue(any(level == "FAIL" for level, _ in out), out)

    def test_empty_block_fails(self):
        out = []
        mod.sourced_lines("", out, "fixture")
        self.assertTrue(any("empty" in msg for _, msg in out), out)


if __name__ == "__main__":
    unittest.main()
