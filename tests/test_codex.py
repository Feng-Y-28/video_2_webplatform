"""Codex installation and dependency discovery, using isolated local fixtures."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _helpers import ORCH, REPO, run_py  # noqa: E402
from test_scaffold import make_animate  # noqa: E402


class CodexInstallTest(unittest.TestCase):
    def test_project_links_whole_bundle_and_runs_through_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "video project"
            proc = run_py(ORCH / "init_project.py", project, "--no-git")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            installed = project / ".agents" / "skills"
            skills = sorted((REPO / "skills").glob("v2w-*/SKILL.md"))
            self.assertEqual(len(skills), 9)
            for skill in skills:
                link = installed / skill.parent.name
                self.assertTrue(link.is_symlink())
                self.assertEqual((link / "SKILL.md").read_bytes(), skill.read_bytes())
                shared = link / ".." / "shared" / "claims-and-sources.md"
                self.assertTrue(shared.is_file(), str(shared))
            self.assertTrue((installed / "shared").is_symlink())
            self.assertTrue((project / "AGENTS.md").is_file())
            self.assertFalse((project / ".claude").exists())
            animate = make_animate(installed)
            proc = run_py(installed / "v2w-orchestra/scripts/new_piece.py",
                          project, "demo", "--input", "How caches work")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertTrue((project / "pieces/demo/src/scenes.js").is_file())
            proc = run_py(installed / "v2w-orchestra/scripts/check_env.py",
                          "--project", project, env={"PATH": ""})
            self.assertIn(str(animate), proc.stdout)
            self.assertNotIn("Traceback", proc.stderr)

    def test_rerun_preserves_user_files_and_existing_real_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            real = project / ".agents/skills/v2w-distill"
            real.mkdir(parents=True)
            (real / "SKILL.md").write_text("custom skill\n")
            legacy = project / ".claude/skills/custom"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy skill\n")
            (project / "AGENTS.md").write_text("custom instructions\n")
            (project / "v2w.config.json").write_text('{"max_retries": 5}\n')
            stale = real.parent / "v2w-review"
            stale.symlink_to(Path(tmp) / "missing")
            for _ in range(2):
                proc = run_py(ORCH / "init_project.py", project, "--no-git")
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((real / "SKILL.md").read_text(), "custom skill\n")
            self.assertEqual((legacy / "SKILL.md").read_text(), "legacy skill\n")
            self.assertEqual((project / "AGENTS.md").read_text(), "custom instructions\n")
            self.assertEqual((project / "v2w.config.json").read_text(), '{"max_retries": 5}\n')
            self.assertEqual(stale.resolve(), REPO / "skills/v2w-review")

    def test_setup_global_default_and_explicit_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp) / "home"
            env = {"HOME": str(fake_home), "PATH": os.environ["PATH"]}
            custom = Path(tmp) / "custom skills"
            for args, target in ((["--global"], fake_home / ".agents/skills"),
                                 (["--global", str(custom)], custom)):
                proc = subprocess.run(["bash", str(REPO / "setup.sh"), *args],
                                      env=env, text=True, capture_output=True, timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertTrue((target / "v2w-orchestra/SKILL.md").is_file())
                self.assertTrue((target / "shared/pitfalls.md").is_file())
            self.assertFalse((fake_home / ".claude").exists())

    def test_setup_forwards_flags_and_rejects_unknown_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            proc = subprocess.run(["bash", str(REPO / "setup.sh"), str(project),
                                   "--no-git", "--no-link"],
                                  text=True, capture_output=True, timeout=30)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse((project / ".git").exists())
            self.assertFalse((project / ".agents").exists())
            proc = subprocess.run(["bash", str(REPO / "setup.sh"), "--typo"],
                                  cwd=tmp, text=True, capture_output=True, timeout=30)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse((Path(tmp) / "--typo").exists())


class AnimateDiscoveryTest(unittest.TestCase):
    def test_precedence_shared_by_piece_creation_and_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, fake_home = root / "project", root / "home"
            custom_codex = root / "codex-profile"
            proc = run_py(ORCH / "init_project.py", project, "--no-git", "--no-link")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            env = {"HOME": str(fake_home), "CODEX_HOME": str(custom_codex), "PATH": ""}
            # Add successively higher-priority installs; both consumers must agree.
            parents = [fake_home / ".claude/skills", project / ".claude/skills",
                       custom_codex / "skills", fake_home / ".agents/skills",
                       project / ".agents/skills"]
            for n, parent in enumerate(parents):
                animate = make_animate(parent)
                proc = run_py(ORCH / "new_piece.py", project, f"demo-{n}", env=env)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(str(animate), proc.stdout)
                proc = run_py(ORCH / "check_env.py", "--project", project, env=env)
                display = str(animate).replace(str(fake_home), "~")
                self.assertIn(display, proc.stdout)
            env_animate = make_animate(root / "env")
            explicit = make_animate(root / "explicit")
            env["ANIMATE_DIR"] = str(env_animate)
            for n, args, expected in ((0, [], env_animate),
                                      (1, ["--animate-dir", explicit], explicit)):
                proc = run_py(ORCH / "new_piece.py", project, f"override-{n}", *args, env=env)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn(str(expected), proc.stdout)
                proc = run_py(ORCH / "check_env.py", "--project", project, *args, env=env)
                self.assertIn(str(expected), proc.stdout)
            missing = root / "missing"
            proc = run_py(ORCH / "new_piece.py", project, "missing-override",
                          "--animate-dir", missing, env=env)
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn(str(missing), proc.stdout)
            self.assertFalse((project / "pieces/missing-override/piece.json").exists())


if __name__ == "__main__":
    unittest.main()
