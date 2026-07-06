"""
Tests for PDF generator
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from src.generator import generate_pdf
from src.types import GenerationOptions, DocumentMetadata


def test_generate_pdf_missing_system():
    """Test PDF generation with missing system requirements"""
    with patch('src.generator.check_pandoc_installed', return_value=(False, None)):
        metadata = DocumentMetadata(title="Test")
        options = GenerationOptions(
            content="# Test",
            metadata=metadata
        )

        result = generate_pdf(options)

        assert result.success is False
        assert "System requirements not met" in result.error


def test_generate_pdf_empty_content():
    """Test PDF generation with empty content"""
    metadata = DocumentMetadata(title="Test")
    options = GenerationOptions(
        content="",
        metadata=metadata
    )

    with patch('src.generator.check_pandoc_installed', return_value=(True, "3.0")):
        with patch('src.generator.check_latex_installed', return_value=(True, "2020")):
            result = generate_pdf(options)

            assert result.success is False
            assert "Content is required" in result.error


def test_build_markdown_document():
    """Test building markdown document with front matter"""
    from src.generator import _build_markdown_document

    metadata = DocumentMetadata(
        title="Test Doc",
        author="John Doe",
        date="2024-01-01"
    )
    options = GenerationOptions(
        content="# Content",
        metadata=metadata,
        margin="1in",
        fontsize=12
    )

    result = _build_markdown_document("# Content", options)

    assert "---" in result
    assert "title:" in result
    assert "Test Doc" in result
    assert "# Content" in result


def test_generate_yaml_front_matter():
    """Test YAML front matter generation"""
    from src.generator import _generate_yaml_front_matter

    metadata = DocumentMetadata(
        title="Test",
        author="Author",
        date="2024-01-01",
        version="1.0"
    )

    result = _generate_yaml_front_matter(metadata, margin="1in", fontsize=12)

    assert result.startswith("---")
    assert result.endswith("---")
    assert "title: \"Test\"" in result
    assert "author: \"Author\"" in result
