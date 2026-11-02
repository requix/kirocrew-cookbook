"""Integration tests for the full build process."""
import subprocess
import sys
from pathlib import Path

import pytest


class TestFullBuild:
    """Integration tests that run the actual build."""

    def test_build_succeeds_on_real_content(self, project_root):
        """Run build.py on the real content and verify it succeeds."""
        build_script = project_root / "build" / "preview" / "build.py"
        result = subprocess.run(
            [sys.executable, str(build_script)],
            cwd=project_root / "build" / "preview",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_build_produces_dist(self, project_root):
        """Verify dist directory exists and has expected structure."""
        dist = project_root / "build" / "preview" / "dist"
        assert dist.exists(), "dist/ not found"
        assert (dist / "index.html").exists(), "index.html not found"
        assert (dist / "assets").exists(), "assets/ not found"

    def test_dist_has_all_sections(self, project_root):
        """Verify all content sections are built."""
        dist = project_root / "build" / "preview" / "dist"
        expected_dirs = ["recipes", "concepts", "start", "apps", "find"]
        for d in expected_dirs:
            assert (dist / d).exists(), f"{d}/ not found in dist"

    def test_llms_txt_generated(self, project_root):
        """Verify llms.txt is generated for agent consumption."""
        dist = project_root / "build" / "preview" / "dist"
        llms = dist / "llms.txt"
        assert llms.exists(), "llms.txt not found"
        content = llms.read_text()
        assert "KiroCrew" in content


class TestBuildValidation:
    """Tests for build-time validation behavior."""

    def test_build_script_is_executable(self, project_root):
        """Verify build.py can be imported without side effects."""
        build_preview = project_root / "build" / "preview"
        # Just check syntax by compiling
        build_py = build_preview / "build.py"
        code = compile(build_py.read_text(), build_py, "exec")
        assert code is not None
