"""
Document Presets Module

Pre-configured document generators for common document types.
"""

from .types import DocumentMetadata, GenerationResult, PresetOptions
from .generator import generate_pdf


def generate_memo(options: PresetOptions) -> GenerationResult:
    """
    Generate a business memo PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "memo",
        output_path=options.output_path,
        toc=False,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_agreement(options: PresetOptions) -> GenerationResult:
    """
    Generate a legal agreement PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "agreement",
        output_path=options.output_path,
        toc=False,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_termsheet(options: PresetOptions) -> GenerationResult:
    """
    Generate an investment term sheet PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "default",  # Use default template for better table compatibility
        output_path=options.output_path,
        toc=False,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_whitepaper(options: PresetOptions) -> GenerationResult:
    """
    Generate a technical whitepaper PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "whitepaper",
        output_path=options.output_path,
        toc=True,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_safe(options: PresetOptions) -> GenerationResult:
    """
    Generate a SAFE (Simple Agreement for Future Equity) PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "default",  # SAFE uses default template
        output_path=options.output_path,
        toc=False,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_nda(options: PresetOptions) -> GenerationResult:
    """
    Generate a Non-Disclosure Agreement PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "agreement",  # NDA uses agreement template
        output_path=options.output_path,
        toc=False,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_report(options: PresetOptions) -> GenerationResult:
    """
    Generate a business report PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "default",
        output_path=options.output_path,
        toc=True,
        numbering=True,
    )

    return generate_pdf(gen_options)


def generate_proposal(options: PresetOptions) -> GenerationResult:
    """
    Generate a business proposal PDF.

    Args:
        options: PresetOptions with content and metadata

    Returns:
        GenerationResult
    """
    gen_options = GenerationOptions(
        content=options.content,
        metadata=options.metadata,
        template=options.template or "default",
        output_path=options.output_path,
        toc=True,
        numbering=True,
    )

    return generate_pdf(gen_options)
