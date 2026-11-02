"""Pytest fixtures for cookbook tests."""
from pathlib import Path
import shutil
import tempfile

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_page_md():
    """Return content of a valid recipe page."""
    return (FIXTURES / "valid_page.md").read_text()


@pytest.fixture
def invalid_page_md():
    """Return content of an invalid page (missing required fields)."""
    return (FIXTURES / "invalid_page.md").read_text()


@pytest.fixture
def temp_content(tmp_path):
    """Create a minimal content structure for integration tests."""
    content = tmp_path / "content"
    content.mkdir()
    
    # Root meta.json
    (content / "meta.json").write_text('{"title": "Test", "pages": ["index", "recipes"]}')
    
    # Index page
    (content / "index.md").write_text("""---
title: Test Cookbook
description: A test cookbook
---

# Welcome
""")
    
    # Recipes section
    recipes = content / "recipes"
    recipes.mkdir()
    (recipes / "meta.json").write_text('{"title": "Recipes", "pages": ["test-recipe"]}')
    (recipes / "test-recipe.md").write_text("""---
title: Test Recipe
description: A test recipe for testing
category: testing
difficulty: beginner
time: 5 min
surfaces: [dashboard]
tags: [test]
updated: 2026-01-01
---

# Test Recipe

This is a test.
""")
    
    return tmp_path


@pytest.fixture
def project_root():
    """Return the real project root for tests that need actual content."""
    return Path(__file__).parent.parent
