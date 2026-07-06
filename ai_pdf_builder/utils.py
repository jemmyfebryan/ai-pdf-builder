"""
Utility functions for AI PDF Builder

Includes system checks, sanitization, and helper functions.
"""

import subprocess
import os
import re
import shutil
import tempfile
from typing import Optional, Tuple
from datetime import datetime
import pathlib


def check_pandoc_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if Pandoc is installed and available.

    Returns:
        Tuple of (is_installed, version_string)
    """
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            version = version_line.replace('pandoc', '').strip()
            return True, version
        return False, None
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, None


def check_latex_installed() -> Tuple[bool, Optional[str]]:
    """
    Check if pdflatex is installed and available.

    Returns:
        Tuple of (is_installed, version_string)
    """
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            version = version_line.split(' ')[1] if ' ' in version_line else "unknown"
            return True, version
        return False, None
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, None


def sanitize_latex(content: str) -> str:
    """
    Sanitize content for safe LaTeX rendering.

    Removes or escapes potentially dangerous LaTeX commands.

    Args:
        content: The content to sanitize

    Returns:
        Sanitized content safe for LaTeX processing
    """
    # Dangerous LaTeX commands that could be used for injection
    dangerous_commands = [
        r'\\write',
        r'\\input',
        r'\\include',
        r'\\catcode',
        r'\\def',
        r'\\let',
        r'\\newcommand',
        r'\\renewcommand',
        r'\\read',
        r'\\openout',
        r'\\closeout',
        r'\\immediate',
        r'\\shipout',
        r'\\openin',
        r'\\closein',
    ]

    # Remove dangerous commands
    sanitized = content
    for cmd in dangerous_commands:
        # Remove the command and any arguments
        sanitized = re.sub(re.escape(cmd) + r'\[.*?\]', '', sanitized)
        sanitized = re.sub(re.escape(cmd) + r'\s.*', '', sanitized)

    # Escape special LaTeX characters that aren't part of commands
    # Process in order to avoid double-escaping
    latex_special_chars = [
        ('\\', r'\\textbackslash{}'),  # Must be first
        ('&', r'\\&'),
        ('%', r'\\%'),
        ('$', r'\\$'),  # Dollar signs for currency
        ('#', r'\\#'),
        ('_', r'\\_'),
        ('{', r'\\{'),
        ('}', r'\\}'),
        ('~', r'\\textasciitilde{}'),
        ('^', r'\\^{}'),
    ]

    for char, escaped in latex_special_chars:
        # Only escape if not already preceded by backslash
        # Look for the character that's not already escaped
        if char == '\\':
            # Handle backslashes specially
            pattern = r'(?<!\\)\\'
        else:
            pattern = r'(?<!\\)' + re.escape(char)
        sanitized = re.sub(pattern, escaped, sanitized)

    return sanitized


def estimate_page_count(pdf_bytes: bytes) -> int:
    """
    Estimate page count from PDF bytes.

    This is a rough estimation based on file size.
    For accurate count, use the info command.

    Args:
        pdf_bytes: PDF file content

    Returns:
        Estimated page count
    """
    # Rough estimation: average PDF page is ~50KB
    # This is very approximate, just for progress feedback
    size_kb = len(pdf_bytes) / 1024
    estimated = int(size_kb / 50)
    return max(1, estimated)  # At least 1 page


def format_date(date_str: Optional[str]) -> str:
    """
    Format date string to standardized format.

    Args:
        date_str: Date string in various formats

    Returns:
        Formatted date string (YYYY-MM-DD)
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    # Try common date formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If no format matches, return as-is
    return date_str


def create_temp_directory() -> tempfile.TemporaryDirectory:
    """
    Create a temporary directory for PDF generation.

    Returns:
        TemporaryDirectory object
    """
    return tempfile.TemporaryDirectory(prefix='ai_pdf_builder_')


def get_template_path(template_name: str) -> Optional[str]:
    """
    Get the full path to a template file.

    Args:
        template_name: Name of the template (without .latex extension)

    Returns:
        Full path to template file, or None if not found
    """
    # Check in package templates directory
    package_dir = pathlib.Path(__file__).parent
    template_path = package_dir / 'templates' / f'{template_name}.latex'

    if template_path.exists():
        return str(template_path)

    # Check in current directory
    local_path = pathlib.Path(f'templates/{template_name}.latex')
    if local_path.exists():
        return str(local_path)

    return None


def get_available_templates() -> list:
    """
    Get list of available template names.

    Returns:
        List of template names (without .latex extension)
    """
    templates = []
    package_dir = pathlib.Path(__file__).parent
    template_dir = package_dir / 'templates'

    if template_dir.exists():
        for file in template_dir.glob('*.latex'):
            templates.append(file.stem)

    return sorted(templates)


def run_pandoc(
    input_file: str,
    output_file: str,
    template: str,
    toc: bool = False,
    numbering: bool = False,
    fontsize: int = 12,
    margin: str = "1in",
) -> Tuple[bool, Optional[str]]:
    """
    Run Pandoc to convert Markdown to PDF.

    Args:
        input_file: Path to input Markdown file
        output_file: Path to output PDF file
        template: Path to LaTeX template
        toc: Include table of contents
        numbering: Number sections
        fontsize: Font size in points
        margin: Page margin (e.g., "1in")

    Returns:
        Tuple of (success, error_message)
    """
    cmd = [
        "pandoc",
        input_file,
        "--pdf-engine=pdflatex",
        f"--template={template}",
        f"-V", f"fontsize={fontsize}pt",
        f"-V", f"margin={margin}",
        "-o", output_file,
    ]

    if toc:
        cmd.append("--toc")

    if numbering:
        cmd.append("--number-sections")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        if result.returncode != 0:
            return False, result.stderr or result.stdout

        return True, None

    except subprocess.TimeoutExpired:
        return False, "Pandoc execution timed out"
    except Exception as e:
        return False, str(e)


def validate_environment() -> Tuple[bool, list]:
    """
    Validate that required tools and environment are configured.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check Pandoc
    pandoc_ok, pandoc_version = check_pandoc_installed()
    if not pandoc_ok:
        issues.append("Pandoc is not installed or not in PATH")

    # Check LaTeX
    latex_ok, latex_version = check_latex_installed()
    if not latex_ok:
        issues.append("pdflatex is not installed or not in PATH")

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        issues.append("GEMINI_API_KEY environment variable not set")

    return len(issues) == 0, issues
