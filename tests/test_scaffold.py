"""init_project.py and new_piece.py: idempotence, config, input classification."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import ORCH, run_py  # noqa: E402

INIT = ORCH / "init_project.py"
NEW_PIECE = ORCH / "new_piece.py"


def make_animate(root):
    """A minimal animate template fixture, so no real animate install is read."""
    template = Path(root) / "animate" / "templates" / "beat-cut"
    (template / "src").mkdir(parents=True)
    (template / "piece.json").write_text(json.dumps({
        "name": "template",
        "format": "9:16",
        "style": "isometric",
        "scenes": ["src/scenes.js"],
    }), encoding="utf-8")
    (template / "src" / "scenes.js").write_text("// fixture\n", encoding="utf-8")
    return Path(root) / "animate"


def init_project(tmp):
    project = Path(tmp) / "project"
    proc = run_py(INIT, project, "--no-git", "--no-link")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return project


class InitProjectTest(unittest.TestCase):
    def test_idempotent_and_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(tmp)
            first = sorted(p.relative_to(project).as_posix()
                           for p in project.rglob("*"))
            proc = run_py(INIT, project, "--no-git", "--no-link")
            self.assertEqual(proc.returncode, 0, proc.stdout)
            second = sorted(p.relative_to(project).as_posix()
                            for p in project.rglob("*"))
            self.assertEqual(first, second)
            for name in ("develop_log", "pieces", "exports", "third_party",
                         "v2w.config.json", ".gitignore"):
                self.assertTrue((project / name).exists(), name)
            self.assertIn("# >>> v2w", (project / ".gitignore").read_text())

    def test_consent_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = init_project(tmp)
            cfg = json.loads((project / "v2w.config.json").read_text())
            self.assertIs(cfg.get("allow_campaign_topics"), False)
            self.assertIn("max_upload_mb", cfg)
            self.assertEqual(cfg.get("max_retries"), 2)

    def test_existing_config_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            (project / "v2w.config.json").write_text('{"max_retries": 5}\n')
            proc = run_py(INIT, project, "--no-git", "--no-link")
            self.assertEqual(proc.returncode, 0, proc.stdout)
            cfg = json.loads((project / "v2w.config.json").read_text())
            self.assertEqual(cfg["max_retries"], 5)


class NewPieceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.project = init_project(self.tmp)
        self.animate = make_animate(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def new_piece(self, name, *args):
        return run_py(NEW_PIECE, self.project, name, *args,
                      env={"ANIMATE_DIR": str(self.animate)})

    def test_creates_layer_and_is_idempotent(self):
        proc = self.new_piece("demo", "--input", "an idea about caches")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        piece = self.project / "pieces" / "demo"
        for name in ("STATUS.md", "principle.md", "brief.md", "LOG.md",
                     "piece.json", "refs/refcard.md", "source/idea.md",
                     "src/scenes.js"):
            self.assertTrue((piece / name).exists(), name)
        self.assertEqual(json.loads((piece / "piece.json").read_text())["name"], "demo")

        (piece / "STATUS.md").write_text("marker\n", encoding="utf-8")
        proc = self.new_piece("demo", "--input", "an idea about caches")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual((piece / "STATUS.md").read_text(), "marker\n")

    def test_idea_text_starting_with_four_digits_is_not_arxiv(self):
        text = "2023 showed that caches still decide the result."
        proc = self.new_piece("idea-piece", "--input", text)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        piece = self.project / "pieces" / "idea-piece"
        idea = piece / "source" / "idea.md"
        self.assertTrue(idea.exists(), proc.stdout)
        self.assertIn(text, idea.read_text())
        self.assertIn("idea: source/idea.md", (piece / "STATUS.md").read_text())

    def test_arxiv_id_is_kept_as_input(self):
        proc = self.new_piece("arxiv-piece", "--input", "2301.12345")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        piece = self.project / "pieces" / "arxiv-piece"
        self.assertIn("2301.12345", (piece / "STATUS.md").read_text())
        self.assertFalse((piece / "source" / "idea.md").exists())

    def test_file_input_is_copied(self):
        paper = Path(self.tmp) / "paper.txt"
        paper.write_text("fixture paper\n", encoding="utf-8")
        proc = self.new_piece("file-piece", "--input", str(paper))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        piece = self.project / "pieces" / "file-piece"
        self.assertTrue((piece / "source" / "paper.txt").exists())
        self.assertIn("source/paper.txt", (piece / "STATUS.md").read_text())

    def test_requires_initialised_project(self):
        bare = Path(self.tmp) / "bare"
        bare.mkdir()
        proc = run_py(NEW_PIECE, bare, "demo",
                      env={"ANIMATE_DIR": str(self.animate)})
        self.assertNotEqual(proc.returncode, 0, proc.stdout)


if __name__ == "__main__":
    unittest.main()
