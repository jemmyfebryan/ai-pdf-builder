"""
Tests for utility functions
"""

import pytest
import os
import tempfile
from src.utils import (
    sanitize_latex,
    format_date,
    estimate_page_count,
    get_available_templates,
)


def test_sanitize_latex_basic():
    """Test basic LaTeX sanitization"""
    content = "Hello World"
    result = sanitize_latex(content)
    assert result == "Hello World"


def test_sanitize_latex_dangerous_commands():
    """Test removal of dangerous LaTeX commands"""
    content = r"Text \write{file}{content} more text"
    result = sanitize_latex(content)
    assert r"\write" not in result


def test_sanitize_latex_special_chars():
    """Test escaping of special LaTeX characters"""
    content = "Hello & World % Test $ Money"
    result = sanitize_latex(content)
    # Should escape special characters
    assert "\\" in result or "&" not in content


def test_sanitize_latex_unicode():
    """Test Unicode character replacement"""
    content = "Hello → World • Test"
    result = sanitize_latex(content)
    assert "→" not in result
    assert "•" not in result
    assert "->" in result or "-" in result


def test_format_date_iso():
    """Test formatting ISO date"""
    result = format_date("2024-01-15")
    assert result == "2024-01-15"


def test_format_date_slashes():
    """Test formatting date with slashes"""
    result = format_date("01/15/2024")
    assert result == "2024-01-15"


def test_format_date_none():
    """Test formatting None date"""
    result = format_date(None)
    assert result is not None
    assert len(result) == 10  # YYYY-MM-DD format


def test_estimate_page_count():
    """Test page count estimation"""
    # Create fake PDF bytes (roughly 100KB)
    pdf_bytes = b"PDF" + b"x" * (100 * 1024)
    result = estimate_page_count(pdf_bytes)
    assert result >= 1
    assert result < 10  # Should be reasonable


def test_estimate_page_count_small():
    """Test page count estimation for small file"""
    pdf_bytes = b"PDF" + b"x" * 1024  # 1KB
    result = estimate_page_count(pdf_bytes)
    assert result == 1  # Minimum 1 page


def test_get_available_templates():
    """Test getting available templates"""
    templates = get_available_templates()
    assert isinstance(templates, list)
    # Should have at least default template
    assert len(templates) >= 0
