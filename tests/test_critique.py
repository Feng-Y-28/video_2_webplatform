"""critique_gate.py: PASS/FAIL, retry budget, verification, staleness, schema."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import (CRIT, critique_json, failing_round, new_piece_dir,  # noqa: E402
                      new_project, run_py, write_round)


def fixture(tmp):
    """A gate-B piece: the three stamped inputs exist and are non-empty."""
    project = new_project(tmp)
    piece = new_piece_dir(project)
    (piece / "principle.md").write_text("# principle\nmechanism\n", encoding="utf-8")
    (piece / "brief.md").write_text("# brief\nhook\n", encoding="utf-8")
    refs = piece / "refs"
    refs.mkdir()
    (refs / "refcard.md").write_text("# refcard\n", encoding="utf-8")
    return piece


def d_fixture(tmp):
    """A gate-D piece with every declared input present."""
    piece = fixture(tmp)
    (piece / "publish.md").write_text(
        "# publish\n\n**Title:** demo\n\n**Body:**\nA line.\n\n"
        "**Tags:** #demo\n\n**Cover:** frame at 2.2 s\n\n"
        "**Declarations:** AI-generated content: yes\n\n**Status:** drafted\n",
        encoding="utf-8")
    (piece / "LOG.md").write_text(
        "## v1 review\n\nChecks: all pass\nWeakest shot: none\n", encoding="utf-8")
    (piece / "renders").mkdir(exist_ok=True)
    (piece / "renders" / "share.mp4").write_bytes(b"video")
    (piece / "renders" / "audio.wav").write_bytes(b"audio")
    review = piece / "review"
    review.mkdir(exist_ok=True)
    (review / "shot01-sheet.jpg").write_bytes(b"jpg")
    (review / "phone.jpg").write_bytes(b"jpg")
    return piece


def gate(piece, *flags):
    return run_py(CRIT / "critique_gate.py", piece, "B", *flags)


def stamp(piece, gate_letter="B"):
    proc = run_py(CRIT / "critique_gate.py", piece, gate_letter, "--stamp")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc


def gate_d(piece, *flags):
    return run_py(CRIT / "critique_gate.py", piece, "D", *flags)


class CritiqueGateTest(unittest.TestCase):
    def test_pass_stamped(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            write_round(piece, "B", 1)
            stamp(piece)
            proc = gate(piece)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("PASS", proc.stdout)
            self.assertIn("inputs verified", proc.stdout)

    def test_pass_legacy_round_only_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            write_round(piece, "B", 1)  # no inputs stamp
            proc = gate(piece)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("legacy", proc.stdout.lower())
            self.assertIn("PASS", proc.stdout)

    def test_fail_with_automatic_retry_left(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            failing_round(piece, "B", 1)
            stamp(piece)
            proc = gate(piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("FAIL", proc.stdout)
            self.assertIn("retr", proc.stdout)

    def test_budget_exhausted(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            for n in (1, 2, 3):
                failing_round(piece, "B", n)
                stamp(piece)
            proc = gate(piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("automatic retries exhausted", proc.stdout)
            self.assertIn("--verify", proc.stdout)

    def test_verification_round_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            for n in (1, 2, 3):
                failing_round(piece, "B", n)
                stamp(piece)
            write_round(piece, "B", 4)
            stamp(piece)
            proc = gate(piece, "--verify")
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("PASS", proc.stdout)

    def test_verification_round_fail_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            for n in (1, 2, 3, 4):
                failing_round(piece, "B", n)
                stamp(piece)
            proc = gate(piece, "--verify")
            self.assertEqual(proc.returncode, 2, proc.stdout)
            self.assertIn("verification round failed", proc.stdout)

    def test_verification_round_needs_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            for n in (1, 2, 3):
                failing_round(piece, "B", n)
                stamp(piece)
            write_round(piece, "B", 4)
            stamp(piece)
            proc = gate(piece)  # latest is the verification round
            self.assertEqual(proc.returncode, 3, proc.stdout)
            self.assertIn("--verify", proc.stdout)

    def test_stale_after_input_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            write_round(piece, "B", 1)
            stamp(piece)
            (piece / "brief.md").write_text("# brief\nchanged\n", encoding="utf-8")
            proc = gate(piece)
            self.assertEqual(proc.returncode, 4, proc.stdout)
            self.assertIn("STALE", proc.stdout)

    def test_stamp_refuses_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            (piece / "brief.md").unlink()
            proc = gate(piece, "--stamp")
            self.assertEqual(proc.returncode, 4, proc.stdout)
            self.assertIn("missing input", proc.stdout)

    def test_invalid_json_is_bad_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            (piece / "critique" / "B-r1.json").write_text("{not json", encoding="utf-8")
            proc = gate(piece)
            self.assertEqual(proc.returncode, 3, proc.stdout)
            self.assertIn("invalid JSON", proc.stdout)

    def test_bad_score_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            data = critique_json("B", 1)
            data["items"][0]["score"] = "high"
            (piece / "critique" / "B-r1.json").write_text(
                json.dumps(data), encoding="utf-8")
            proc = gate(piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("not 1-5", proc.stdout)

    def test_round_gap_is_a_layout_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            write_round(piece, "B", 1)
            write_round(piece, "B", 3)
            proc = gate(piece)
            self.assertEqual(proc.returncode, 3, proc.stdout)
            self.assertIn("non-contiguous", proc.stdout)

    def test_stray_round_file_is_ignored_with_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = fixture(tmp)
            write_round(piece, "B", 1)
            (piece / "critique" / "B-notes.json").write_text("{}", encoding="utf-8")
            proc = gate(piece)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("ignoring non-round file", proc.stdout)

    def test_d8_required_by_schema_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            stamp(piece, "D")
            data = critique_json("D", 1, schema=2)
            data["items"] = [i for i in data["items"] if i["id"] != "D8"]
            (piece / "critique" / "D-r1.json").write_text(
                json.dumps(data), encoding="utf-8")
            proc = gate_d(piece)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("D8", proc.stdout)

    def test_legacy_d_without_d8_only_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            data = critique_json("D", 1, schema=1)
            data["items"] = [i for i in data["items"] if i["id"] != "D8"]
            (piece / "critique" / "D-r1.json").write_text(
                json.dumps(data), encoding="utf-8")
            proc = gate_d(piece)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("legacy rubric", proc.stdout)

    def test_schema_2_without_stamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            write_round(piece, "D", 1, schema=2)
            proc = gate_d(piece)
            self.assertEqual(proc.returncode, 3, proc.stdout)
            self.assertIn("no inputs stamp", proc.stdout)

    def test_log_append_does_not_stale_d(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            stamp(piece, "D")
            write_round(piece, "D", 1, schema=2)
            self.assertEqual(gate_d(piece).returncode, 0)
            with (piece / "LOG.md").open("a", encoding="utf-8") as f:
                f.write("\n- critique D summary appended after the round\n")
            self.assertEqual(gate_d(piece).returncode, 0)

    def test_publish_status_change_does_not_stale_d(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            stamp(piece, "D")
            write_round(piece, "D", 1, schema=2)
            self.assertEqual(gate_d(piece).returncode, 0)
            text = (piece / "publish.md").read_text(encoding="utf-8")
            (piece / "publish.md").write_text(
                text.replace("**Status:** drafted",
                             "**Status:** published 2026-01-01 https://example.org/post"),
                encoding="utf-8")
            self.assertEqual(gate_d(piece).returncode, 0)

    def test_publish_body_change_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            stamp(piece, "D")
            write_round(piece, "D", 1, schema=2)
            self.assertEqual(gate_d(piece).returncode, 0)
            text = (piece / "publish.md").read_text(encoding="utf-8")
            (piece / "publish.md").write_text(
                text.replace("A line.", "A different line."), encoding="utf-8")
            proc = gate_d(piece)
            self.assertEqual(proc.returncode, 4, proc.stdout)
            self.assertIn("publish.md", proc.stdout)

    def test_publish_upload_metadata_does_not_stale_d(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            stamp(piece, "D")
            write_round(piece, "D", 1, schema=2)
            self.assertEqual(gate_d(piece).returncode, 0)
            text = (piece / "publish.md").read_text(encoding="utf-8")
            text = text.replace("**Cover:** frame at 2.2 s",
                                "**Cover:** frame at 2.2 s · read back: 2.2")
            text = text.replace("**Declarations:** AI-generated content: yes",
                                "**Declarations:** AI-generated content: yes "
                                "· state read back: checked")
            text = text.replace("**Status:** drafted",
                                "**Form verification:** pass\n"
                                "**File size:** 9.3 MB\n"
                                "**Limit check:** 9.3 vs 10 MB → PASS\n"
                                "**sha256:** abcdef123456\n"
                                "**Status:** published 2026-01-01 https://example.org/post")
            (piece / "publish.md").write_text(text, encoding="utf-8")
            self.assertEqual(gate_d(piece).returncode, 0)

    def test_publish_cover_change_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece = d_fixture(tmp)
            stamp(piece, "D")
            write_round(piece, "D", 1, schema=2)
            self.assertEqual(gate_d(piece).returncode, 0)
            text = (piece / "publish.md").read_text(encoding="utf-8")
            (piece / "publish.md").write_text(
                text.replace("frame at 2.2 s", "frame at 3.0 s"), encoding="utf-8")
            self.assertEqual(gate_d(piece).returncode, 4)


if __name__ == "__main__":
    unittest.main()
