"""Tests for content validation in build.py."""
from pathlib import Path

import pytest
import yaml

import build


def parse_frontmatter(content: str) -> dict:
    """Extract frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}
    _, fm, body = content.split("---", 2)
    return yaml.safe_load(fm)


def make_page(meta: dict, src_name: str = "test.md") -> dict:
    """Create a minimal page dict for validation.
    
    Uses a path inside the project so validate() can compute relative paths.
    """
    # Use a path inside the actual project content directory
    src = build.CONTENT / src_name
    return {"meta": meta, "src": src, "body": "# Test"}


class TestValidate:
    """Tests for the validate() function."""

    def test_valid_page_passes(self, valid_page_md):
        meta = parse_frontmatter(valid_page_md)
        page = make_page(meta)
        errs = build.validate(page)
        assert errs == []

    def test_missing_required_fields(self):
        page = make_page({"title": "Test"})
        errs = build.validate(page)
        # Should catch missing: description, category, difficulty, time, surfaces, tags, updated
        assert len(errs) >= 1
        assert any("missing" in e for e in errs)

    def test_title_too_long(self):
        meta = {
            "title": "X" * 61,  # Over 60 chars
            "description": "Short",
            "category": "test",
            "difficulty": "beginner",
            "time": "5 min",
            "surfaces": ["dashboard"],
            "tags": ["test"],
            "updated": "2026-01-01",
        }
        page = make_page(meta)
        errs = build.validate(page)
        assert any("title longer than 60" in e for e in errs)

    def test_description_too_long(self):
        meta = {
            "title": "Test",
            "description": "X" * 141,  # Over 140 chars
            "category": "test",
            "difficulty": "beginner",
            "time": "5 min",
            "surfaces": ["dashboard"],
            "tags": ["test"],
            "updated": "2026-01-01",
        }
        page = make_page(meta)
        errs = build.validate(page)
        assert any("description longer than 140" in e for e in errs)

    def test_invalid_difficulty(self):
        meta = {
            "title": "Test",
            "description": "Short",
            "category": "test",
            "difficulty": "expert",  # Not in allowed list
            "time": "5 min",
            "surfaces": ["dashboard"],
            "tags": ["test"],
            "updated": "2026-01-01",
        }
        page = make_page(meta)
        errs = build.validate(page)
        assert any("difficulty must be one of" in e for e in errs)

    def test_invalid_surface(self):
        meta = {
            "title": "Test",
            "description": "Short",
            "category": "test",
            "difficulty": "beginner",
            "time": "5 min",
            "surfaces": ["dashboard", "mobile"],  # mobile not valid
            "tags": ["test"],
            "updated": "2026-01-01",
        }
        page = make_page(meta)
        errs = build.validate(page)
        assert any("unknown surfaces" in e for e in errs)


class TestSlugify:
    """Tests for the slugify() function."""

    def test_basic_slugify(self):
        seen = set()
        assert build.slugify("Hello World", seen) == "hello-world"

    def test_removes_special_chars(self):
        seen = set()
        assert build.slugify("What's this?", seen) == "whats-this"

    def test_handles_duplicates(self):
        seen = set()
        first = build.slugify("Test", seen)
        second = build.slugify("Test", seen)
        third = build.slugify("Test", seen)
        assert first == "test"
        assert second == "test-2"  # Starts at 2, not 1
        assert third == "test-3"
        assert "test" in seen
        assert "test-2" in seen
        assert "test-3" in seen


class TestBrandName:
    """The product is 'Kiro Crew' (two words). 'KiroCrew' in prose is a build error."""

    BASE_META = {
        "title": "Test page",
        "description": "Short",
        "category": "test",
        "difficulty": "beginner",
        "time": "5 min",
        "surfaces": ["dashboard"],
        "tags": ["test"],
        "updated": "2026-01-01",
    }

    def test_wrong_brand_in_frontmatter_title(self):
        meta = {**self.BASE_META, "title": "Build your own KiroCrew app"}
        page = make_page(meta)
        errs = build.validate(page)
        assert any("KiroCrew" in e and "Kiro Crew" in e for e in errs)

    def test_wrong_brand_in_frontmatter_prerequisites(self):
        meta = {**self.BASE_META, "prerequisites": ["KiroCrew running"]}
        page = make_page(meta)
        errs = build.validate(page)
        assert any("KiroCrew" in e for e in errs)

    def test_wrong_brand_in_prose(self):
        page = make_page(self.BASE_META)
        page["body"] = "KiroCrew is a great tool."
        errs = build.validate(page)
        assert any("KiroCrew" in e for e in errs)

    def test_brand_in_code_fence_is_exempt(self):
        """Identifiers inside code blocks must not be flagged."""
        page = make_page(self.BASE_META)
        page["body"] = "Run this:\n\n```python\nclass KiroCrewConfig:\n    pass\n```\n"
        errs = build.validate(page)
        brand_errs = [e for e in errs if "Kiro Crew" in e or "KiroCrew" in e]
        assert brand_errs == []

    def test_brand_in_inline_code_is_exempt(self):
        """Identifiers in backtick spans must not be flagged."""
        page = make_page(self.BASE_META)
        page["body"] = "Use `KiroCrew.app` to launch."
        errs = build.validate(page)
        brand_errs = [e for e in errs if "Kiro Crew" in e or "KiroCrew" in e]
        assert brand_errs == []

    def test_brand_in_url_is_exempt(self):
        """GitHub repo URL contains KiroCrew but must not be flagged."""
        page = make_page(self.BASE_META)
        page["body"] = "See the [guide](https://github.com/kirodotdev/KiroCrew/blob/main/docs/guide.md)."
        errs = build.validate(page)
        brand_errs = [e for e in errs if "Kiro Crew" in e or "KiroCrew" in e]
        assert brand_errs == []

    def test_correct_brand_passes(self):
        page = make_page(self.BASE_META)
        page["body"] = "Kiro Crew is a great tool."
        errs = build.validate(page)
        brand_errs = [e for e in errs if "Kiro Crew" in e or "KiroCrew" in e]
        assert brand_errs == []
