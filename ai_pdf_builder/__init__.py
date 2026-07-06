"""
AI PDF Builder - Python version with Gemini API

This package provides AI-powered PDF generation using Google Gemini API
and Pandoc + LaTeX for professional document formatting.
"""

__version__ = "0.1.0"

from .types import (
    DocumentMetadata,
    GenerationOptions,
    AIOptions,
    PresetOptions,
)

from .generator import generate_pdf
from .ai import generate_content, enhance_content, generate_summary
from .presets import (
    generate_memo,
    generate_agreement,
    generate_termsheet,
    generate_whitepaper,
    generate_safe,
    generate_nda,
    generate_report,
    generate_proposal,
)

__all__ = [
    # Version
    "__version__",
    # Types
    "DocumentMetadata",
    "GenerationOptions",
    "AIOptions",
    "PresetOptions",
    # Core functions
    "generate_pdf",
    "generate_content",
    "enhance_content",
    "generate_summary",
    # Presets
    "generate_memo",
    "generate_agreement",
    "generate_termsheet",
    "generate_whitepaper",
    "generate_safe",
    "generate_nda",
    "generate_report",
    "generate_proposal",
]
