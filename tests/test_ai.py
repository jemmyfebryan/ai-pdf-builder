"""
Tests for AI module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ai import GeminiAI
from src.types import AIOptions


@pytest.fixture
def mock_client():
    """Create a mock Gemini client"""
    with patch('src.ai.genai.Client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


def test_gemini_ai_init():
    """Test GeminiAI initialization"""
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
        ai = GeminiAI()
        assert ai.api_key == 'test-key'
        assert ai.model == 'gemini-2.5-flash'


def test_gemini_ai_init_custom():
    """Test GeminiAI initialization with custom parameters"""
    ai = GeminiAI(api_key='custom-key', model='gemini-pro')
    assert ai.api_key == 'custom-key'
    assert ai.model == 'gemini-pro'


def test_gemini_ai_init_no_key():
    """Test GeminiAI initialization without API key"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            GeminiAI()


def test_generate_success():
    """Test successful content generation"""
    mock_response = Mock()
    mock_response.text = "# Generated Content\n\nThis is generated text."

    with patch('src.ai.genai.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        ai = GeminiAI(api_key='test-key')
        options = AIOptions(
            prompt="Test prompt",
            document_type="whitepaper"
        )

        result = ai.generate(options)

        assert result.success is True
        assert result.content is not None
        assert "Generated Content" in result.content
        assert result.model_used == "gemini-2.5-flash"


def test_generate_with_company_context():
    """Test generation with company context"""
    mock_response = Mock()
    mock_response.text = "# Company Whitepaper\n\nContent about company."

    with patch('src.ai.genai.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        ai = GeminiAI(api_key='test-key')
        options = AIOptions(
            prompt="AI technology",
            document_type="whitepaper",
            company_context="Tech Corp"
        )

        result = ai.generate(options)

        assert result.success is True
        assert result.content is not None


def test_enhance_success():
    """Test successful content enhancement"""
    mock_response = Mock()
    mock_response.text = "# Enhanced Content\n\nThis is improved text."

    with patch('src.ai.genai.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        ai = GeminiAI(api_key='test-key')

        result = ai.enhance("# Original Content\n\nOriginal text.", "whitepaper")

        assert result.success is True
        assert result.content is not None
        assert "Enhanced" in result.content or "improved" in result.content.lower()


def test_summarize_success():
    """Test successful summarization"""
    mock_response = Mock()
    mock_response.text = "## Executive Summary\n\nThis is the summary."

    with patch('src.ai.genai.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        ai = GeminiAI(api_key='test-key')

        result = ai.summarize("# Long Document\n\nLots of content...")

        assert result.success is True
        assert result.content is not None
        assert "Executive Summary" in result.content or "summary" in result.content.lower()


def test_sanitize_for_latex():
    """Test LaTeX sanitization in AI module"""
    ai = GeminiAI(api_key='test-key')

    content = "Test → Content • More"
    sanitized = ai._sanitize_for_latex(content)

    assert "→" not in sanitized
    assert "•" not in sanitized


def test_generate_error():
    """Test error handling in generation"""
    with patch('src.ai.genai.Client') as mock_client_class:
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        ai = GeminiAI(api_key='test-key')
        options = AIOptions(
            prompt="Test",
            document_type="whitepaper"
        )

        result = ai.generate(options)

        assert result.success is False
        assert result.error is not None


# Import os at module level for pytest fixtures
import os
