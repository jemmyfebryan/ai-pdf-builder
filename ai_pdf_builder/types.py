"""
Type definitions for AI PDF Builder

All data models use Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata for document generation"""
    title: str
    author: Optional[str] = None
    date: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    version: Optional[str] = "1.0"
    company: Optional[str] = None


class GenerationOptions(BaseModel):
    """Options for PDF generation"""
    content: str
    metadata: DocumentMetadata
    template: Optional[str] = "default"
    output_path: Optional[str] = None
    toc: bool = False
    numbering: bool = False
    fontsize: int = 12
    margin: str = "1in"
    custom_colors: Optional[Dict[str, str]] = None  # RGB colors like {"primary": "0,0,255"}


class AIOptions(BaseModel):
    """Options for AI content generation"""
    prompt: str
    document_type: str
    company_context: Optional[str] = None
    model: Optional[str] = "gemini-2.5-flash"
    temperature: float = 0.7
    max_tokens: Optional[int] = 4096


class PresetOptions(BaseModel):
    """Options for preset document generators"""
    content: str
    metadata: DocumentMetadata
    template: Optional[str] = None
    output_path: Optional[str] = None


class GenerationResult(BaseModel):
    """Result from PDF generation"""
    success: bool
    output_path: Optional[str] = None
    pdf_bytes: Optional[bytes] = None
    page_count: Optional[int] = None
    file_size: Optional[int] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None


class AIContentResult(BaseModel):
    """Result from AI content generation"""
    success: bool
    content: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None


class TemplateInfo(BaseModel):
    """Information about a template"""
    name: str
    description: str
    path: str
    supported_types: List[str]


class PDFInfo(BaseModel):
    """Information about a PDF file"""
    path: str
    page_count: int
    file_size: int
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MergeOptions(BaseModel):
    """Options for merging PDFs"""
    input_files: List[str]
    output_path: str
    compress: bool = False


class ExtractOptions(BaseModel):
    """Options for extracting pages from PDF"""
    input_file: str
    pages: str  # e.g., "1-3,5,7-9"
    output_path: str
