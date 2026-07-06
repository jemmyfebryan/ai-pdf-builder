# AI PDF Builder

Python version of AI-powered PDF generator using Google Gemini API and Pandoc + LaTeX.

## Features

- 🤖 **AI Content Generation** - Generate professional documents with Google Gemini
- 📄 **Markdown to PDF** - Convert Markdown to professionally formatted PDFs
- 🎨 **Multiple Templates** - Built-in templates for different document types
- 🔧 **PDF Operations** - Merge, extract, and analyze PDFs
- ✨ **Content Enhancement** - AI-powered content improvement
- 📋 **Executive Summaries** - Generate summaries with AI

## Installation

### Requirements

- Python 3.10+
- Pandoc (https://pandoc.org/installing.html)
- pdflatex (TeX Live or MiKTeX)

### Install Package

```bash
# Clone repository
git clone https://github.com/yourusername/ai-pdf-builder-python
cd ai-pdf-builder-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Set API Key

```bash
# Set Gemini API key
export GEMINI_API_KEY=your-api-key-here

# Or create .env file
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

## Usage

### AI Generation

Generate documents with AI from natural language prompts:

```bash
# Generate whitepaper
ai-pdf-builder ai whitepaper "AI agents for developer productivity" -o whitepaper.pdf

# Generate with company context
ai-pdf-builder ai whitepaper "Market intelligence platform" --company "Acme Inc" -o whitepaper.pdf

# Generate term sheet
ai-pdf-builder ai termsheet "Series Seed, $2M at $8M cap" --company "Acme Inc" -t "Series Seed"

# Generate SAFE agreement
ai-pdf-builder ai safe "$500K investment at $10M cap" --company "TechCo" -o safe.pdf
```

### Markdown to PDF

Convert existing Markdown to PDF:

```bash
ai-pdf-builder generate whitepaper ./content.md -o whitepaper.pdf
ai-pdf-builder generate memo ./memo.md -o memo.pdf --author "John Doe"
```

### Content Enhancement

Enhance existing content with AI:

```bash
ai-pdf-builder enhance whitepaper ./rough-draft.md -o polished.pdf
ai-pdf-builder enhance memo ./memo.md -o enhanced.md --save-md
```

### Executive Summaries

Add AI-generated executive summaries:

```bash
ai-pdf-builder summarize ./long-doc.md -o with-summary.pdf
```

### PDF Operations

```bash
# Merge PDFs
ai-pdf-builder merge file1.pdf file2.pdf -o combined.pdf

# Extract pages
ai-pdf-builder extract document.pdf "1-3,5,7-9" -o extracted.pdf

# Get PDF info
ai-pdf-builder info document.pdf
```

### Check System

Verify system requirements:

```bash
ai-pdf-builder check
```

### List Templates

Show available templates:

```bash
ai-pdf-builder templates
```

## Document Types

- `whitepaper` - Technical documentation, litepapers
- `memo` - Executive summaries, internal memos
- `agreement` - Legal contracts, general agreements
- `termsheet` - Investment term sheets
- `safe` - SAFE agreements
- `nda` - Non-disclosure agreements
- `report` - Business reports, analysis
- `proposal` - Business proposals, pitches

## Python API

Use as a Python library:

```python
from ai_pdf_builder import (
    generate_pdf,
    generate_content,
    enhance_content,
    generate_memo,
    DocumentMetadata,
    GenerationOptions,
    AIOptions,
)

# Generate content with AI
ai_options = AIOptions(
    prompt="AI in healthcare",
    document_type="whitepaper",
    company_context="HealthTech Inc",
)

content = generate_content(ai_options)

# Generate PDF
metadata = DocumentMetadata(
    title="AI in Healthcare",
    author="Jane Doe",
    company="HealthTech Inc",
)

gen_options = GenerationOptions(
    content=content,
    metadata=metadata,
    template="whitepaper",
    output_path="healthcare_ai.pdf",
)

result = generate_pdf(gen_options)

if result.success:
    print(f"Generated {result.output_path}")
    print(f"Pages: {result.page_count}")
    print(f"Size: {result.file_size} bytes")
```

## Templates

Templates are stored in the `templates/` directory as LaTeX files:

- `default.latex` - Clean professional template
- `memo.latex` - Business memo template
- `agreement.latex` - Legal agreement template
- `termsheet.latex` - Investment term sheet template
- `whitepaper.latex` - Technical whitepaper template

### Custom Templates

You can create custom templates by adding `.latex` files to the `templates/` directory or specifying a custom template path.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY` - Google Gemini API key (required for AI features)

### Pandoc Variables

You can customize PDF generation with Pandoc variables:

- `fontsize` - Font size (default: 12pt)
- `margin` - Page margin (default: 1in)
- `papersize` - Paper size (default: letter)
- `toc` - Include table of contents
- `number-sections` - Number sections

## Troubleshooting

### Pandoc not found

Install Pandoc from https://pandoc.org/installing.html

### pdflatex not found

Install TeX Live (Linux/Mac) or MiKTeX (Windows)

### API key errors

Ensure `GEMINI_API_KEY` is set in your environment or `.env` file

Get an API key from https://ai.google.dev/

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Acknowledgments

Based on the JavaScript ai-pdf-builder by Next Frontier Builds

## Support

For issues and questions, please open a GitHub issue.
