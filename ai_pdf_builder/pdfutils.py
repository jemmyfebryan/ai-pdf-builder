"""
PDF Utilities Module

Provides PDF manipulation operations: merge, extract, info.
"""

import os
from typing import List, Dict, Optional
from pypdf import PdfReader, PdfWriter


def merge_pdfs(input_files: List[str], output_path: str) -> Dict:
    """
    Merge multiple PDF files into one.

    Args:
        input_files: List of input PDF file paths
        output_path: Output PDF file path

    Returns:
        Dict with success status and info
    """
    try:
        writer = PdfWriter()
        total_pages = 0

        for input_file in input_files:
            if not os.path.exists(input_file):
                return {
                    "success": False,
                    "error": f"File not found: {input_file}"
                }

            reader = PdfReader(input_file)
            total_pages += len(reader.pages)

            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        return {
            "success": True,
            "output_path": output_path,
            "input_files": len(input_files),
            "total_pages": total_pages,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_pages(input_file: str, pages: str, output_path: str) -> Dict:
    """
    Extract specific pages from a PDF.

    Args:
        input_file: Input PDF file path
        pages: Pages to extract (e.g., "1-3,5,7-9")
        output_path: Output PDF file path

    Returns:
        Dict with success status and info
    """
    try:
        if not os.path.exists(input_file):
            return {
                "success": False,
                "error": f"File not found: {input_file}"
            }

        reader = PdfReader(input_file)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Parse page specification
        page_indices = _parse_page_spec(pages, total_pages)

        # Convert to 0-based indices and add pages
        for page_num in page_indices:
            if 1 <= page_num <= total_pages:
                writer.add_page(reader.pages[page_num - 1])

        with open(output_path, "wb") as f:
            writer.write(f)

        return {
            "success": True,
            "output_path": output_path,
            "extracted_pages": len(page_indices),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_pdf_info(file_path: str) -> Dict:
    """
    Get information about a PDF file.

    Args:
        file_path: PDF file path

    Returns:
        Dict with PDF information
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        reader = PdfReader(file_path)
        metadata = reader.metadata

        info = {
            "success": True,
            "path": file_path,
            "page_count": len(reader.pages),
            "file_size": os.path.getsize(file_path),
            "title": metadata.get("/Title", None) if metadata else None,
            "author": metadata.get("/Author", None) if metadata else None,
            "creator": metadata.get("/Creator", None) if metadata else None,
            "producer": metadata.get("/Producer", None) if metadata else None,
            "creation_date": metadata.get("/CreationDate", None) if metadata else None,
        }

        return info

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _parse_page_spec(spec: str, total_pages: int) -> List[int]:
    """
    Parse page specification string into list of page numbers.

    Args:
        spec: Page specification (e.g., "1-3,5,7-9")
        total_pages: Total number of pages in document

    Returns:
        List of page numbers (1-based)
    """
    pages = []
    parts = spec.split(",")

    for part in parts:
        part = part.strip()

        if "-" in part:
            # Range (e.g., "1-3")
            start, end = part.split("-")
            start = int(start.strip())
            end = int(end.strip())

            for page in range(start, end + 1):
                if 1 <= page <= total_pages:
                    pages.append(page)

        else:
            # Single page
            page = int(part)
            if 1 <= page <= total_pages:
                pages.append(page)

    return sorted(set(pages))  # Remove duplicates and sort
