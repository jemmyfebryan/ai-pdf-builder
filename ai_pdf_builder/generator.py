"""
PDF Generator Module

Core PDF generation logic using Pandoc and LaTeX.
"""

import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple

from .types import GenerationOptions, GenerationResult
from .utils import (
    check_pandoc_installed,
    check_latex_installed,
    sanitize_latex,
    estimate_page_count,
    create_temp_directory,
    get_template_path,
)


def generate_pdf(options: GenerationOptions) -> GenerationResult:
    """
    Generate a PDF from Markdown content.

    Args:
        options: GenerationOptions with content, metadata, template, etc.

    Returns:
        GenerationResult with PDF bytes or file path

    Example:
        ```python
        result = generate_pdf(
            GenerationOptions(
                content="# Hello World\\n\\nThis is my document.",
                metadata=DocumentMetadata(title="My Document", author="John Doe"),
                template="default"
            )
        )

        if result.success:
            if result.pdf_bytes:
                with open("output.pdf", "wb") as f:
                    f.write(result.pdf_bytes)
        ```
    """
    start_time = time.time()

    # Check system requirements
    pandoc_ok, _ = check_pandoc_installed()
    latex_ok, _ = check_latex_installed()

    if not pandoc_ok or not latex_ok:
        return GenerationResult(
            success=False,
            error="System requirements not met: Pandoc and pdflatex must be installed",
            generation_time=time.time() - start_time,
        )

    # Validate content
    if not options.content or not options.content.strip():
        return GenerationResult(
            success=False,
            error="Content is required",
            generation_time=time.time() - start_time,
        )

    temp_dir = None

    try:
        # Create temporary working directory
        temp_dir = create_temp_directory()

        # Don't re-sanitize - AI module already handles LaTeX sanitization
        sanitized_content = options.content

        # Build full markdown with YAML front matter
        full_markdown = _build_markdown_document(sanitized_content, options)

        # Write markdown to temp file
        input_path = os.path.join(temp_dir.name, "input.md")
        with open(input_path, "w", encoding="utf-8") as f:
            f.write(full_markdown)

        # Get and customize template
        template_path = _prepare_template(temp_dir.name, options)

        # Determine output path
        output_path = options.output_path or os.path.join(temp_dir.name, "output.pdf")

        # Build pandoc command
        pandoc_cmd = _build_pandoc_command(
            input_path=input_path,
            output_path=output_path,
            template_path=template_path,
            options=options,
        )

        # Execute pandoc
        success, error = _execute_pandoc(pandoc_cmd)

        if not success:
            return GenerationResult(
                success=False,
                error=error or "PDF generation failed",
                generation_time=time.time() - start_time,
            )

        # Read result
        if not os.path.exists(output_path):
            return GenerationResult(
                success=False,
                error="PDF generation failed - output file not created",
                generation_time=time.time() - start_time,
            )

        with open(output_path, "rb") as f:
            pdf_bytes = f.read()

        file_size = len(pdf_bytes)
        page_count = estimate_page_count(pdf_bytes)
        generation_time = time.time() - start_time

        # Return result
        return GenerationResult(
            success=True,
            pdf_bytes=None if options.output_path else pdf_bytes,
            output_path=options.output_path,
            page_count=page_count,
            file_size=file_size,
            generation_time=generation_time,
        )

    except Exception as e:
        return GenerationResult(
            success=False,
            error=f"PDF generation failed: {str(e)}",
            generation_time=time.time() - start_time,
        )

    finally:
        # Clean up temp directory if we created it and no output path was specified
        if temp_dir and not options.output_path:
            temp_dir.cleanup()


def _build_markdown_document(content: str, options: GenerationOptions) -> str:
    """
    Build the full markdown document with YAML front matter.

    Args:
        content: Sanitized markdown content
        options: Generation options

    Returns:
        Complete markdown document with front matter
    """
    parts = []

    # Add YAML front matter if metadata provided
    if options.metadata:
        front_matter = _generate_yaml_front_matter(
            options.metadata,
            margin=options.margin,
            fontsize=options.fontsize,
        )
        parts.append(front_matter)
        parts.append("")

    # Add content
    parts.append(content)

    return "\n".join(parts)


def _generate_yaml_front_matter(metadata, margin: str = "1in", fontsize: int = 12) -> str:
    """
    Generate YAML front matter for Pandoc.

    Args:
        metadata: DocumentMetadata instance
        margin: Page margin
        fontsize: Font size in points

    Returns:
        YAML front matter string
    """
    lines = ["---"]

    if metadata.title:
        lines.append(f'title: "{metadata.title}"')

    if metadata.author:
        lines.append(f'author: "{metadata.author}"')

    if metadata.date:
        lines.append(f'date: "{metadata.date}"')

    if metadata.version:
        lines.append(f'version: "{metadata.version}"')

    if metadata.company:
        lines.append(f'company: "{metadata.company}"')

    # Add Pandoc variables
    lines.append(f'geometry: margin={margin}')
    lines.append(f'fontsize: {fontsize}pt')
    lines.append("papersize: letter")
    lines.append("documentclass: article")

    lines.append("---")

    return "\n".join(lines)


def _prepare_template(temp_dir: str, options: GenerationOptions) -> str:
    """
    Prepare the LaTeX template with customizations.

    Args:
        temp_dir: Temporary directory path
        options: Generation options

    Returns:
        Path to prepared template file
    """
    # Get base template
    template_name = options.template or "default"
    template_file = get_template_path(template_name)

    if not template_file:
        # Fall back to default
        template_file = get_template_path("default")
        if not template_file:
            raise ValueError(f"Template not found: {template_name}")

    # Read template content
    with open(template_file, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Apply color customizations
    if options.custom_colors:
        template_content = _apply_color_customizations(template_content, options.custom_colors)

    # Write customized template to temp directory
    custom_template_path = os.path.join(temp_dir, "template.latex")
    with open(custom_template_path, "w", encoding="utf-8") as f:
        f.write(template_content)

    return custom_template_path


def _apply_color_customizations(template: str, colors: dict) -> str:
    """
    Apply color customizations to template.

    Args:
        template: Template content
        colors: Dict with primary, secondary, accent colors

    Returns:
        Customized template
    """
    result = template

    if "primary" in colors:
        rgb = colors["primary"]  # Should be "r,g,b" format
        result = result.replace(
            r'\definecolor{primaryBlue}{RGB}{[^}]+}',
            f'\\definecolor{{primaryColor}}{{RGB}}{{{rgb}}}'
        )
        result = result.replace(
            r'\definecolor{primaryColor}{RGB}{[^}]+}',
            f'\\definecolor{{primaryColor}}{{RGB}}{{{rgb}}}'
        )

    if "secondary" in colors:
        rgb = colors["secondary"]
        result = result.replace(
            r'\definecolor{primaryGray}{RGB}{[^}]+}',
            f'\\definecolor{{secondaryColor}}{{RGB}}{{{rgb}}}'
        )
        result = result.replace(
            r'\definecolor{secondaryColor}{RGB}{[^}]+}',
            f'\\definecolor{{secondaryColor}}{{RGB}}{{{rgb}}}'
        )

    if "accent" in colors:
        rgb = colors["accent"]
        result = result.replace(
            r'\definecolor{primaryDark}{RGB}{[^}]+}',
            f'\\definecolor{{accentColor}}{{RGB}}{{{rgb}}}'
        )
        result = result.replace(
            r'\definecolor{accentColor}{RGB}{[^}]+}',
            f'\\definecolor{{accentColor}}{{RGB}}{{{rgb}}}'
        )

    return result


def _build_pandoc_command(
    input_path: str,
    output_path: str,
    template_path: str,
    options: GenerationOptions,
) -> list:
    """
    Build Pandoc command line arguments.

    Args:
        input_path: Input markdown file path
        output_path: Output PDF file path
        template_path: Template file path
        options: Generation options

    Returns:
        List of command line arguments
    """
    cmd = [
        "pandoc",
        input_path,
        "-o", output_path,
        "--pdf-engine=pdflatex",
        f"--template={template_path}",
        "--columns=100",  # Wider columns for better table width calculations
        "-V", f"geometry:margin={options.margin}",
        "-V", f"fontsize={options.fontsize}pt",
        "-V", "papersize=letter",
        "-V", "documentclass=article",
        "-V", "colorlinks=true",
        "-V", "linkcolor=blue",
        "-V", "urlcolor=blue",
    ]

    if options.toc:
        cmd.append("--toc")

    if options.numbering:
        cmd.append("--number-sections")

    return cmd


def _execute_pandoc(cmd: list, timeout: int = 60) -> Tuple[bool, Optional[str]]:
    """
    Execute Pandoc command.

    Args:
        cmd: Command line arguments
        timeout: Timeout in seconds

    Returns:
        Tuple of (success, error_message)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Pandoc failed"
            return False, error_msg

        return True, None

    except subprocess.TimeoutExpired:
        return False, f"Pandoc timed out after {timeout} seconds"

    except Exception as e:
        return False, str(e)
