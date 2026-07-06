#!/usr/bin/env python3
"""
AI PDF Builder CLI

Generate professional PDFs from the command line with AI support.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from . import __version__
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
from .utils import validate_environment, check_pandoc_installed, check_latex_installed, get_available_templates
from .pdfutils import merge_pdfs, extract_pages, get_pdf_info
from .templates import get_available_templates as list_templates

app = typer.Typer(
    name="ai-pdf-builder",
    help="Generate professional PDFs from Markdown — now with AI!",
    add_completion=False,
)
console = Console()

# Document type constants
DOCUMENT_TYPES = [
    "whitepaper",
    "memo",
    "agreement",
    "termsheet",
    "safe",
    "nda",
    "report",
    "proposal",
]


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"ai-pdf-builder v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True),
):
    """AI PDF Builder - Generate professional PDFs from Markdown with AI support."""
    pass


@app.command("ai")
def ai_command(
    document_type: str = typer.Argument(..., help="Document type", autocompletion=lambda: DOCUMENT_TYPES),
    prompt: str = typer.Argument(..., help="Content description/prompt"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Document title"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
    company: Optional[str] = typer.Option(None, "--company", help="Company name (for AI context)"),
    context: Optional[str] = typer.Option(None, "--context", help="Additional context for AI"),
    model: Optional[str] = typer.Option(None, "--model", help="AI model to use"),
    save_md: bool = typer.Option(False, "--save-md", help="Save generated markdown"),
):
    """
    🤖 Generate document with AI.

    Example:
        ai-pdf-builder ai whitepaper "AI agents for developer productivity" -o whitepaper.pdf
    """
    if document_type not in DOCUMENT_TYPES:
        console.print(f"[red]Invalid document type: {document_type}[/red]")
        console.print(f"Available types: {', '.join(DOCUMENT_TYPES)}")
        raise typer.Exit(1)

    try:
        # Generate content with AI
        with console.status("[bold cyan]Generating content with AI...[/bold cyan]"):
            ai_options = AIOptions(
                prompt=prompt,
                document_type=document_type,
                company_context=company or context,
                model=model,
            )

            content = generate_content(ai_options)

        console.print("[green]✓ Content generated[/green]")

        # Save markdown if requested
        if save_md:
            md_path = (output or f"{document_type}.pdf").replace(".pdf", ".md")
            with open(md_path, "w") as f:
                f.write(content)
            console.print(f"[green]✓ Saved markdown to {md_path}[/green]")

        # Generate PDF
        with console.status("[bold cyan]Generating PDF...[/bold cyan]"):
            metadata = DocumentMetadata(
                title=title or prompt[:50],
                author=author,
                company=company,
            )

            gen_options = GenerationOptions(
                content=content,
                metadata=metadata,
                template=document_type,
                output_path=output or f"{document_type}.pdf",
            )

            result = generate_pdf(gen_options)

        if result.success:
            console.print(f"[green]✓ Generated {document_type} PDF[/green]")
            if result.output_path:
                console.print(f"  [blue]→ {result.output_path}[/blue]")
            if result.page_count:
                console.print(f"  [blue]→ {result.page_count} pages[/blue]")
            if result.file_size:
                size_kb = result.file_size / 1024
                console.print(f"  [blue]→ {size_kb:.1f} KB[/blue]")
        else:
            console.print(f"[red]✗ PDF generation failed: {result.error}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("generate")
def generate_command(
    document_type: str = typer.Argument(..., help="Document type"),
    input_file: str = typer.Argument(..., help="Input markdown file", exists=True),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Document title"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
    toc: bool = typer.Option(True, "--toc/--no-toc", help="Include table of contents"),
    numbering: bool = typer.Option(True, "--numbering/--no-numbering", help="Number sections"),
):
    """
    Generate PDF from markdown file.

    Example:
        ai-pdf-builder generate whitepaper ./content.md -o whitepaper.pdf
    """
    try:
        # Read input file
        with open(input_file, "r") as f:
            content = f.read()

        # Generate PDF
        with console.status("[bold cyan]Generating PDF...[/bold cyan]"):
            metadata = DocumentMetadata(
                title=title or Path(input_file).stem,
                author=author,
            )

            gen_options = GenerationOptions(
                content=content,
                metadata=metadata,
                template=document_type,
                output_path=output or f"{document_type}.pdf",
                toc=toc,
                numbering=numbering,
            )

            result = generate_pdf(gen_options)

        if result.success:
            console.print(f"[green]✓ Generated {document_type} PDF[/green]")
            if result.output_path:
                console.print(f"  [blue]→ {result.output_path}[/blue]")
        else:
            console.print(f"[red]✗ PDF generation failed: {result.error}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("enhance")
def enhance_command(
    document_type: str = typer.Argument(..., help="Document type"),
    input_file: str = typer.Argument(..., help="Input markdown file", exists=True),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    save_md: bool = typer.Option(False, "--save-md", help="Save enhanced markdown"),
):
    """
    🤖 Enhance content with AI then generate PDF.

    Example:
        ai-pdf-builder enhance whitepaper ./rough-draft.md -o polished.pdf
    """
    try:
        # Read input file
        with open(input_file, "r") as f:
            content = f.read()

        # Enhance with AI
        with console.status("[bold cyan]Enhancing content with AI...[/bold cyan]"):
            enhanced = enhance_content(content, document_type)

        console.print("[green]✓ Content enhanced[/green]")

        # Save markdown if requested
        if save_md:
            md_path = (output or input_file).replace(".pdf", ".md").replace(".md", "_enhanced.md")
            with open(md_path, "w") as f:
                f.write(enhanced)
            console.print(f"[green]✓ Saved enhanced markdown to {md_path}[/green]")

        # Generate PDF
        with console.status("[bold cyan]Generating PDF...[/bold cyan]"):
            metadata = DocumentMetadata(title=Path(input_file).stem)
            gen_options = GenerationOptions(
                content=enhanced,
                metadata=metadata,
                template=document_type,
                output_path=output or f"{document_type}_enhanced.pdf",
            )

            result = generate_pdf(gen_options)

        if result.success:
            console.print(f"[green]✓ Generated enhanced PDF[/green]")
            if result.output_path:
                console.print(f"  [blue]→ {result.output_path}[/blue]")
        else:
            console.print(f"[red]✗ PDF generation failed: {result.error}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("summarize")
def summarize_command(
    input_file: str = typer.Argument(..., help="Input markdown file", exists=True),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    save_md: bool = typer.Option(False, "--save-md", help="Save with summary"),
):
    """
    🤖 Add AI-generated executive summary to document.

    Example:
        ai-pdf-builder summarize ./long-doc.md -o with-summary.pdf
    """
    try:
        # Read input file
        with open(input_file, "r") as f:
            content = f.read()

        # Generate summary
        with console.status("[bold cyan]Generating executive summary...[/bold cyan]"):
            summary = generate_summary(content)

        console.print("[green]✓ Summary generated[/green]")

        # Prepend summary to content
        enhanced = f"{summary}\n\n{content}"

        # Save markdown if requested
        if save_md:
            md_path = (output or input_file).replace(".pdf", ".md").replace(".md", "_with_summary.md")
            with open(md_path, "w") as f:
                f.write(enhanced)
            console.print(f"[green]✓ Saved markdown to {md_path}[/green]")

        # Generate PDF
        with console.status("[bold cyan]Generating PDF...[/bold cyan]"):
            metadata = DocumentMetadata(title=Path(input_file).stem)
            gen_options = GenerationOptions(
                content=enhanced,
                metadata=metadata,
                template="report",
                output_path=output or f"{Path(input_file).stem}_summary.pdf",
            )

            result = generate_pdf(gen_options)

        if result.success:
            console.print(f"[green]✓ Generated PDF with summary[/green]")
            if result.output_path:
                console.print(f"  [blue]→ {result.output_path}[/blue]")
        else:
            console.print(f"[red]✗ PDF generation failed: {result.error}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("merge")
def merge_command(
    files: List[str] = typer.Argument(..., help="PDF files to merge", exists=True),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
):
    """
    📎 Merge multiple PDFs into one.

    Example:
        ai-pdf-builder merge file1.pdf file2.pdf -o combined.pdf
    """
    try:
        with console.status("[bold cyan]Merging PDFs...[/bold cyan]"):
            result = merge_pdfs(files, output)

        if result["success"]:
            console.print(f"[green]✓ Merged {result['input_files']} PDFs[/green]")
            console.print(f"  [blue]→ {output}[/blue]")
            console.print(f"  [blue]→ {result['total_pages']} total pages[/blue]")
        else:
            console.print(f"[red]✗ Merge failed: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("extract")
def extract_command(
    input_file: str = typer.Argument(..., help="Input PDF file", exists=True),
    pages: str = typer.Argument(..., help="Pages to extract (e.g., '1-5' or '1,3,5')"),
    output: str = typer.Option(..., "--output", "-o", help="Output file path"),
):
    """
    ✂️  Extract pages from PDF.

    Example:
        ai-pdf-builder extract document.pdf "1-3,5,7-9" -o extracted.pdf
    """
    try:
        with console.status("[bold cyan]Extracting pages...[/bold cyan]"):
            result = extract_pages(input_file, pages, output)

        if result["success"]:
            console.print(f"[green]✓ Extracted {result['extracted_pages']} pages[/green]")
            console.print(f"  [blue]→ {output}[/blue]")
        else:
            console.print(f"[red]✗ Extraction failed: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("info")
def info_command(
    file: str = typer.Argument(..., help="PDF file", exists=True),
):
    """
    📋 Show PDF metadata and page count.

    Example:
        ai-pdf-builder info document.pdf
    """
    try:
        result = get_pdf_info(file)

        if result["success"]:
            table = Table(title=f"PDF Info: {Path(file).name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Path", result["path"])
            table.add_row("Size", f"{result['file_size'] / 1024:.1f} KB")
            table.add_row("Pages", str(result["page_count"]))

            if result.get("title"):
                table.add_row("Title", result["title"])
            if result.get("author"):
                table.add_row("Author", result["author"])

            console.print(table)
        else:
            console.print(f"[red]✗ Failed to get info: {result.get('error', 'Unknown error')}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command("check")
def check_command():
    """
    Check system requirements.

    Example:
        ai-pdf-builder check
    """
    console.print("[bold]Checking system requirements...[/bold]\n")

    # Check Pandoc
    pandoc_ok, pandoc_version = check_pandoc_installed()
    if pandoc_ok:
        console.print(f"[green]✓ Pandoc[/green] {pandoc_version}")
    else:
        console.print("[red]✗ Pandoc[/red] not installed")

    # Check LaTeX
    latex_ok, latex_version = check_latex_installed()
    if latex_ok:
        console.print(f"[green]✓ pdflatex[/green] {latex_version}")
    else:
        console.print("[red]✗ pdflatex[/red] not installed")

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        console.print(f"[green]✓ GEMINI_API_KEY[/green] set ({api_key[:10]}...{api_key[-4:]})")
    else:
        console.print("[yellow]⚠ GEMINI_API_KEY[/yellow] not set (required for AI features)")

    # Overall status
    if pandoc_ok and latex_ok:
        console.print("\n[green]✓ System ready for PDF generation[/green]")
        if not api_key:
            console.print("[yellow]⚠ API key missing - AI features unavailable[/yellow]")
    else:
        console.print("\n[red]✗ System not ready - install missing components[/red]")
        console.print("  Install Pandoc: https://pandoc.org/installing.html")
        console.print("  Install LaTeX: https://www.latex-project.org/get/")


@app.command("templates")
def templates_command():
    """
    List available templates.

    Example:
        ai-pdf-builder templates
    """
    templates = list_templates()

    table = Table(title="Available Templates")
    table.add_column("Template", style="cyan")
    table.add_column("Path", style="green")

    for template in templates:
        from .templates import get_template_path
        path = get_template_path(template)
        table.add_row(template, path or "Not found")

    console.print(table)


if __name__ == "__main__":
    app()
