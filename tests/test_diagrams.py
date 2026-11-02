"""Tests for the diagrams module (flow and tree fences)."""
import pytest

import diagrams


class TestFlowDiagram:
    """Tests for flow diagram parsing and rendering."""

    def test_simple_box(self):
        # Flow diagrams use YAML format with box: keys
        src = "- box: Hello World"
        html = diagrams.flow_html(src, lambda x: x)
        assert "Hello World" in html
        assert "vc-flow" in html

    def test_box_with_note(self):
        src = """- box: Main
  note: A description"""
        html = diagrams.flow_html(src, lambda x: x)
        assert "Main" in html
        assert "A description" in html

    def test_sequence_of_boxes(self):
        src = """- box: First
- box: Second
  via: arrow label
- box: Third"""
        html = diagrams.flow_html(src, lambda x: x)
        assert "First" in html
        assert "Second" in html
        assert "Third" in html
        assert "arrow label" in html

    def test_split_branches(self):
        src = """- box: Start
- split:
    - - box: Branch A
    - - box: Branch B"""
        html = diagrams.flow_html(src, lambda x: x)
        assert "Start" in html
        assert "Branch A" in html
        assert "Branch B" in html

    def test_empty_raises_error(self):
        with pytest.raises(diagrams.DiagramError, match="expected a list"):
            diagrams.flow_html("", lambda x: x)

    def test_invalid_yaml_raises_error(self):
        with pytest.raises(diagrams.DiagramError, match="not valid YAML"):
            diagrams.flow_html("- box: [unclosed", lambda x: x)

    def test_unknown_keys_raises_error(self):
        with pytest.raises(diagrams.DiagramError, match="unknown key"):
            diagrams.flow_html("- box: Test\n  badkey: value", lambda x: x)

    def test_markdown_output(self):
        src = "- box: Hello"
        md = diagrams.flow_markdown(src)
        assert "Hello" in md

    def test_with_caption(self):
        src = """flow:
  - box: One
  - box: Two
caption: My diagram"""
        html = diagrams.flow_html(src, lambda x: x)
        assert "One" in html
        assert "Two" in html
        # Caption should be rendered somewhere
        assert "My diagram" in html


class TestTreeDiagram:
    """Tests for tree diagram parsing and rendering."""

    def test_simple_tree(self):
        src = """root/
  file.txt"""
        html = diagrams.tree_html(src)
        assert "root" in html
        assert "file.txt" in html

    def test_nested_tree(self):
        src = """project/
  src/
    main.py
  tests/
    test_main.py"""
        html = diagrams.tree_html(src)
        assert "project" in html
        assert "src" in html
        assert "main.py" in html
        assert "tests" in html

    def test_tree_with_description(self):
        src = """root/
  config.yml  # Configuration file"""
        html = diagrams.tree_html(src)
        assert "config.yml" in html
        assert "Configuration file" in html

    def test_deep_nesting(self):
        src = """a/
  b/
    c/
      d.txt"""
        html = diagrams.tree_html(src)
        assert "a" in html
        assert "b" in html
        assert "c" in html
        assert "d.txt" in html
