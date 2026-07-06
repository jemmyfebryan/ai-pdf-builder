"""
Tests for type definitions
"""

import pytest
from datetime import datetime
from src.types import (
    DocumentMetadata,
    GenerationOptions,
    AIOptions,
    PresetOptions,
    GenerationResult,
    AIContentResult,
)


def test_document_metadata():
    """Test DocumentMetadata creation"""
    metadata = DocumentMetadata(
        title="Test Document",
        author="John Doe",
        date="2024-01-01",
        version="1.0",
        company="Test Company"
    )

    assert metadata.title == "Test Document"
    assert metadata.author == "John Doe"
    assert metadata.date == "2024-01-01"
    assert metadata.version == "1.0"
    assert metadata.company == "Test Company"


def test_document_metadata_defaults():
    """Test DocumentMetadata default values"""
    metadata = DocumentMetadata(title="Test")

    assert metadata.title == "Test"
    assert metadata.author is None
    assert metadata.date is not None  # Should default to today
    assert metadata.version == "1.0"
    assert metadata.company is None


def test_generation_options():
    """Test GenerationOptions creation"""
    metadata = DocumentMetadata(title="Test")
    options = GenerationOptions(
        content="# Test Content",
        metadata=metadata,
        template="memo",
        output_path="test.pdf",
        toc=True,
        numbering=True
    )

    assert options.content == "# Test Content"
    assert options.metadata == metadata
    assert options.template == "memo"
    assert options.output_path == "test.pdf"
    assert options.toc is True
    assert options.numbering is True


def test_ai_options():
    """Test AIOptions creation"""
    options = AIOptions(
        prompt="Generate a whitepaper about AI",
        document_type="whitepaper",
        company_context="Tech Company",
        model="gemini-2.5-flash",
        temperature=0.7
    )

    assert options.prompt == "Generate a whitepaper about AI"
    assert options.document_type == "whitepaper"
    assert options.company_context == "Tech Company"
    assert options.model == "gemini-2.5-flash"
    assert options.temperature == 0.7


def test_preset_options():
    """Test PresetOptions creation"""
    metadata = DocumentMetadata(title="Test Memo")
    options = PresetOptions(
        content="Memo content",
        metadata=metadata,
        template="memo",
        output_path="memo.pdf"
    )

    assert options.content == "Memo content"
    assert options.metadata == metadata
    assert options.template == "memo"
    assert options.output_path == "memo.pdf"


def test_generation_result():
    """Test GenerationResult creation"""
    result = GenerationResult(
        success=True,
        output_path="test.pdf",
        page_count=5,
        file_size=12345,
        generation_time=1.5
    )

    assert result.success is True
    assert result.output_path == "test.pdf"
    assert result.page_count == 5
    assert result.file_size == 12345
    assert result.generation_time == 1.5
    assert result.error is None


def test_generation_result_failure():
    """Test GenerationResult for failure case"""
    result = GenerationResult(
        success=False,
        error="Generation failed",
        generation_time=0.5
    )

    assert result.success is False
    assert result.error == "Generation failed"
    assert result.generation_time == 0.5
    assert result.output_path is None


def test_ai_content_result():
    """Test AIContentResult creation"""
    result = AIContentResult(
        success=True,
        content="# Generated Content",
        model_used="gemini-2.5-flash",
        generation_time=2.0
    )

    assert result.success is True
    assert result.content == "# Generated Content"
    assert result.model_used == "gemini-2.5-flash"
    assert result.generation_time == 2.0
