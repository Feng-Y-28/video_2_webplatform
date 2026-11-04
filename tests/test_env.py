"""check_env.py smoke tests, using only temp stubs (no real toolchain)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import ORCH, run_py  # noqa: E402

CHECK_ENV = ORCH / "check_env.py"


def make_stub(path, body):
    path.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
    path.chmod(0o755)


class CheckEnvTest(unittest.TestCase):
    def test_help_lists_the_required_set(self):
        proc = run_py(CHECK_ENV, "--help")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = proc.stdout.lower()
        self.assertIn("animate", out)
        self.assertIn("fail", out)

    def test_missing_animate_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_bin = Path(tmp) / "bin"
            empty_bin.mkdir()
            empty_animate = Path(tmp) / "animate"
            empty_animate.mkdir()
            proc = run_py(CHECK_ENV, "--animate-dir", empty_animate,
                          env={"PATH": str(empty_bin)})
            out = (proc.stdout + proc.stderr).lower()
            self.assertNotEqual(proc.returncode, 0, out)
            self.assertIn("animate", out)
            self.assertNotIn("traceback", out)

    def test_old_node_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            make_stub(bin_dir / "ffmpeg", "echo ' drawtext V->V fixture filter'")
            make_stub(bin_dir / "node", "echo v16.0.0")
            animate = Path(tmp) / "animate"
            animate.mkdir()
            proc = run_py(CHECK_ENV, "--animate-dir", animate,
                          env={"PATH": f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"})
            out = proc.stdout + proc.stderr
            self.assertNotEqual(proc.returncode, 0, out)
            self.assertIn("older than 18", out)

    def test_stubbed_environment_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir()
            make_stub(bin_dir / "ffmpeg", "echo ' ffmpeg version fixture'; "
                      "echo ' drawtext            V->V       fixture filter'")
            make_stub(bin_dir / "node", "echo v18.0.0")
            make_stub(bin_dir / "npm", f"echo {Path(tmp) / 'npm-global'}")
            animate = Path(tmp) / "animate"
            animate.mkdir()
            (animate / "SKILL.md").write_text("# animate fixture\n", encoding="utf-8")
            proc = run_py(CHECK_ENV, "--animate-dir", animate,
                          env={"PATH": f"{bin_dir}{os.pathsep}/usr/bin{os.pathsep}/bin"})
            out = proc.stdout + proc.stderr
            self.assertNotIn("Traceback", out)
            self.assertIn("animate", out.lower())


if __name__ == "__main__":
    unittest.main()
