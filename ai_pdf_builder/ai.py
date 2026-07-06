"""
AI Content Generation Module

Uses Google Gemini API to generate professional document content.
"""

import os
import time
from typing import Optional, Dict
from dotenv import load_dotenv
from google import genai
from .types import AIOptions, AIContentResult

# Load environment variables from .env file
load_dotenv()


class GeminiAI:
    """Google Gemini AI client for content generation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini AI client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model name (defaults to GEMINI_MODEL_NAME env var or gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found.\n\n"
                "To use AI features:\n"
                "  1. Get an API key at https://ai.google.dev/\n"
                "  2. Set it: export GEMINI_API_KEY=your-api-key\n\n"
                "Or use the non-AI generate command with your own markdown file."
            )

        self.client = genai.Client(api_key=self.api_key)

    def _sanitize_for_latex(self, content: str) -> str:
        """
        Sanitize content for LaTeX compatibility.
        Removes/replaces Unicode characters that break pdflatex.

        Args:
            content: The content to sanitize

        Returns:
            Sanitized content safe for LaTeX processing
        """
        # First, escape LaTeX special characters EXCEPT in markdown contexts
        # This must be done BEFORE Unicode replacement
        import re

        # Don't escape # in headings (lines starting with #)
        lines = content.split('\n')
        escaped_lines = []

        for line in lines:
            # Check if this is a markdown heading
            if line.strip().startswith('#'):
                # It's a heading, don't escape # but escape other specials
                # Only escape the # if it's not at the start
                heading_match = re.match(r'^(#+)\s*(.*)', line)
                if heading_match:
                    hashes, rest = heading_match.groups()
                    # Escape special chars in the rest of the line
                    rest = self._escape_latex_specials(rest)
                    escaped_lines.append(hashes + ' ' + rest)
                else:
                    escaped_lines.append(line)
            else:
                # Not a heading, escape all special chars
                escaped_lines.append(self._escape_latex_specials(line))

        content = '\n'.join(escaped_lines)

        # Then replace Unicode characters
        replacements = {
            '→': '->',
            '←': '<-',
            '↔': '<->',
            '•': '-',
            '·': '-',
            '…': '...',
            '–': '-',
            '—': '---',
            '\u201c': '"',
            '\u201d': '"',
            '\u2018': "'",
            '\u2019': "'",
            '©': '(c)',
            '®': '(R)',
            '™': '(TM)',
            '°': ' degrees',
            '±': '+/-',
            '×': 'x',
            '÷': '/',
            '≤': '<=',
            '≥': '>=',
            '≠': '!=',
            '∞': 'infinity',
        }

        for old, new in replacements.items():
            content = content.replace(old, new)

        # Remove remaining problematic characters (outside basic ASCII)
        sanitized = ""
        for char in content:
            code = ord(char)
            # Keep printable ASCII, newlines, tabs, and common accented chars
            if (32 <= code <= 126) or code in [9, 10, 13] or (192 <= code <= 255):
                sanitized += char
            # Remove other non-ASCII
            elif code < 32:
                sanitized += char  # Keep control characters

        # Clean up multiple spaces/newlines from removals
        sanitized = '  '.join(sanitized.split('  '))
        sanitized = '\n\n'.join(sanitized.split('\n\n\n+'))

        return sanitized

    def _escape_latex_specials(self, text: str) -> str:
        """Escape LaTeX special characters in text."""
        import re
        latex_special_chars = {
            '\\': r'\\textbackslash{}',  # Must be first
            '&': r'\\&',
            '%': r'\\%',
            '$': r'\\$',  # Critical for currency amounts
            '#': r'\\#',
            '_': r'\\_',
            '{': r'\\{',
            '}': r'\\}',
            '~': r'\\textasciitilde{}',
            '^': r'\\^{}',
        }

        for char, escaped in latex_special_chars.items():
            if char == '\\':
                text = re.sub(r'(?<!\\)\\', escaped, text)
            else:
                text = re.sub(r'(?<!\\)' + re.escape(char), escaped, text)

        return text

    def _remove_latex_code(self, content: str) -> str:
        """
        Remove any LaTeX code from content, keeping only markdown.
        This is used to clean up AI-generated content that incorrectly includes LaTeX.

        Strategy: Find where actual markdown content starts (first # heading) and ends,
        and extract only that section.
        """
        lines = content.split('\n')

        # Find the first line that looks like markdown content (heading)
        first_markdown_line = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('##') or stripped.startswith('# '):
                first_markdown_line = i
                break

        # Find the last line before end document
        last_markdown_line = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if '\\end{document}' in lines[i]:
                last_markdown_line = i
                break

        # Extract markdown content between these boundaries
        if first_markdown_line > 0:
            markdown_lines = lines[first_markdown_line:last_markdown_line]

            # Filter out any remaining LaTeX commands from the markdown
            filtered = []
            for line in markdown_lines:
                # Skip lines that are purely LaTeX commands
                stripped = line.strip()
                if stripped.startswith('\\usepackage') or \
                   stripped.startswith('\\documentclass') or \
                   stripped.startswith('\\begin{') and not stripped.startswith('\\begin{document}') or \
                   stripped.startswith('\\end{') and not stripped.startswith('\\end{document}') or \
                   stripped.startswith('\\definecolor') or \
                   stripped.startswith('\\renewcommand') or \
                   stripped.startswith('\\usetikzlibrary') or \
                   (stripped.startswith('%') and 'ai-pdf-builder' in stripped):
                    continue
                filtered.append(line)

            return '\n'.join(filtered).strip()

        # If no markdown found, return as is
        return content

    def generate(self, options: AIOptions) -> AIContentResult:
        """
        Generate document content using AI.

        Args:
            options: AIOptions with prompt, document_type, etc.

        Returns:
            AIContentResult with generated content or error
        """
        start_time = time.time()

        try:
            system_prompt = self._get_system_prompt(options.document_type)

            # Build context-aware prompt
            user_prompt = f"Create a {options.document_type} about: {options.prompt}\n\n"

            # Add company context if provided
            if options.company_context:
                user_prompt += f"Company: {options.company_context}\n"

            user_prompt += (
                "\nGenerate the complete document in markdown format. "
                "Start with a title using # heading. Do not use placeholder text or brackets."
            )

            # Generate content
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{system_prompt}\n\n{user_prompt}",
            )

            generation_time = time.time() - start_time
            content = self._sanitize_for_latex(response.text)

            return AIContentResult(
                success=True,
                content=content,
                model_used=self.model,
                generation_time=generation_time,
            )

        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = self._handle_error(e)

            return AIContentResult(
                success=False,
                error=error_msg,
                generation_time=generation_time,
            )

    def enhance(self, content: str, doc_type: str) -> AIContentResult:
        """
        Enhance existing content using AI.

        Args:
            content: Existing markdown content
            doc_type: Document type (memo, whitepaper, etc.)

        Returns:
            AIContentResult with enhanced content or error
        """
        start_time = time.time()

        try:
            system_prompt = f"""You are a professional editor improving {doc_type} documents.

CRITICAL RULES:
- Return ONLY markdown format - NO LaTeX code, \\documentclass, or \\begin{{document}}
- Do NOT add placeholder text or brackets
- Do NOT use ASCII art or box-drawing characters
- Preserve all real names, numbers, and specific details
- Keep all content as plain markdown
- Primary markdown heading should start with Heading 1 (#)

Enhance the document by:
- Improving clarity and readability
- Fixing grammar and style issues
- Strengthening arguments and flow

Formatting & Flow:
- After primary Heading 1 should contains the abstract paragraph of the whole file if it's not provided yet
- When content has structured data (key-value pairs, comparisons, related metrics), format as markdown tables
- Below every table must contains plain paragraph of the table content description if its not provided yet
- Final part of the marksdown should contains conclusion of the whole fie if it's not provided yet
"""

            user_prompt = f"Enhance this {doc_type} document:\n\n{content}\n\nReturn the improved version in markdown format."

            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{system_prompt}\n\n{user_prompt}",
            )

            generation_time = time.time() - start_time
            # First strip any LaTeX code the AI incorrectly generated
            cleaned_content = self._remove_latex_code(response.text)
            # Then sanitize for LaTeX compatibility
            enhanced_content = self._sanitize_for_latex(cleaned_content)

            return AIContentResult(
                success=True,
                content=enhanced_content,
                model_used=self.model,
                generation_time=generation_time,
            )

        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = self._handle_error(e)

            return AIContentResult(
                success=False,
                error=error_msg,
                generation_time=generation_time,
            )

    def summarize(self, content: str) -> AIContentResult:
        """
        Generate executive summary from content.

        Args:
            content: Document content to summarize

        Returns:
            AIContentResult with summary or error
        """
        start_time = time.time()

        try:
            system_prompt = """You are an executive assistant creating concise summaries.

IMPORTANT:
- Extract only facts present in the document
- Do NOT invent statistics or claims
- Keep it to 3-5 focused paragraphs
- Use clear, executive-friendly language"""

            user_prompt = f"Create an executive summary for this document:\n\n{content}\n\nReturn just the summary in markdown, starting with '## Executive Summary'."

            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{system_prompt}\n\n{user_prompt}",
            )

            generation_time = time.time() - start_time
            summary = self._sanitize_for_latex(response.text)

            return AIContentResult(
                success=True,
                content=summary,
                model_used=self.model,
                generation_time=generation_time,
            )

        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = self._handle_error(e)

            return AIContentResult(
                success=False,
                error=error_msg,
                generation_time=generation_time,
            )

    def _get_system_prompt(self, doc_type: str) -> str:
        """Get system prompt for document type"""
        prompts = {
            "whitepaper": """You are a technical writer creating professional whitepapers.

IMPORTANT RULES:
- Do NOT use placeholder text like "[Company Name]" or "[Your Name]"
- Do NOT use ASCII art, box diagrams, or Unicode box-drawing characters
- Do NOT invent fake statistics or metrics
- Use real, general industry insights when specific data isn't provided
- Keep diagrams as simple bullet lists or tables, not ASCII art

Write clear, authoritative content with:
- Executive summary (2-3 paragraphs)
- Problem statement
- Solution overview
- Key benefits
- Implementation approach
- Conclusion

Use markdown formatting with ## for sections. Be specific and substantive.""",

            "memo": """You are a business writer creating executive memos.

IMPORTANT RULES:
- Do NOT use placeholder text like "[Recipient]" or "[Date]"
- Do NOT invent fake names, emails, or contact info
- If company/author info is provided, use it. Otherwise, omit those fields.
- Keep it professional and actionable

Write concise content with:
- Clear purpose statement
- Key points (3-5 bullets)
- Recommendations
- Next steps

Use markdown formatting. Be direct and brief.""",

            "termsheet": """You are a financial/legal writer creating investment term sheets.

IMPORTANT RULES:
- Do NOT use placeholder brackets like "[Amount]" - use the actual values provided
- If specific numbers aren't given, use realistic example figures
- Do NOT invent company names - use what's provided or say "the Company"
- Keep language precise and professional

Include standard sections:
- Investment overview (amount, type, valuation)
- Key terms table
- Investor rights
- Governance provisions
- Conditions and timeline

Use markdown with tables where appropriate.""",

            "safe": """You are a legal writer creating SAFE agreements.

IMPORTANT RULES:
- Use actual investment amounts and terms provided
- Do NOT use placeholder brackets
- Follow standard Y Combinator SAFE conventions
- If company name not provided, use "the Company"

Include:
- Investment amount and type
- Valuation cap (if applicable)
- Discount rate (if applicable)
- Pro-rata rights
- Standard SAFE provisions

Use markdown formatting with clear section headers.""",

            "nda": """You are a legal writer creating Non-Disclosure Agreements.

IMPORTANT RULES:
- Do NOT use placeholder brackets for party names
- Use "Disclosing Party" and "Receiving Party" if names not provided
- Keep language clear and enforceable
- Include standard NDA provisions

Include:
- Definition of confidential information
- Obligations of receiving party
- Exclusions from confidentiality
- Term (suggest 2-3 years if not specified)
- Return/destruction of materials

Use markdown formatting.""",

            "agreement": """You are a legal writer creating professional agreements.

IMPORTANT RULES:
- Do NOT use placeholder brackets
- Use clear party designations if names not provided
- Keep language professional and enforceable

Include appropriate sections:
- Parties and purpose
- Terms and conditions
- Rights and obligations
- Term and termination
- General provisions

Use markdown formatting.""",

            "report": """You are a business analyst creating professional reports.

IMPORTANT RULES:
- Do NOT invent fake statistics or metrics
- Use qualitative insights when specific data isn't provided
- Do NOT use ASCII art or box diagrams
- Keep analysis substantive and actionable

Include:
- Executive summary
- Key findings (use bullet points)
- Analysis and insights
- Recommendations
- Next steps

Use markdown with tables for data where appropriate.""",

            "proposal": """You are a business development writer creating compelling proposals.

IMPORTANT RULES:
- Do NOT use placeholder brackets
- If company/pricing not provided, focus on value and approach
- Be persuasive but realistic
- No fake testimonials or statistics

Include:
- Executive summary
- Understanding of the opportunity
- Proposed approach
- Key deliverables
- Timeline
- Investment/next steps

Use markdown formatting. Be confident and professional.""",

            "research": """You are improving research content.

IMPORTANT RULES:
- Return ONLY markdown format - NO LaTeX code, \\documentclass, or \\begin{{document}}
- Do NOT use placeholder brackets
- Do NOT invent fake data
- Preserve all real information from the input

**FORMATTING:**
- Try to use markdown tables
- Let the content dictate the structure - don't add/remove sections
- Improve writing quality, clarity, and flow
- Use markdown: ## for sections, ** for emphasis, | for tables""",
        }

        return prompts.get(doc_type, prompts["whitepaper"])

    def _handle_error(self, error: Exception) -> str:
        """Handle API errors with user-friendly messages"""
        error_str = str(error).lower()

        if "401" in error_str or "unauthorized" in error_str or "authentication" in error_str:
            return "Invalid API key. Please check your GEMINI_API_KEY.\nGet a valid key at https://ai.google.dev/"

        if "429" in error_str or "quota" in error_str or "rate" in error_str:
            return "Rate limited or quota exceeded. Please wait and try again.\nCheck your usage at https://ai.google.dev/"

        if "500" in error_str or "503" in error_str or "unavailable" in error_str:
            return "AI service temporarily unavailable. Please try again in a few moments."

        return f"Error generating content: {str(error)}"


# Convenience functions for backward compatibility
def generate_content(options: AIOptions, config: Optional[Dict] = None) -> str:
    """
    Generate document content using AI.

    Args:
        options: AIOptions with generation parameters
        config: Optional config dict (model, api_key)

    Returns:
        Generated markdown content

    Raises:
        ValueError: If API key is missing
        Exception: If generation fails
    """
    config = config or {}
    ai = GeminiAI(
        api_key=config.get("api_key"),
        model=config.get("model", options.model)
    )

    result = ai.generate(options)

    if not result.success:
        raise Exception(result.error or "Generation failed")

    return result.content or ""


def enhance_content(content: str, doc_type: str, config: Optional[Dict] = None) -> str:
    """
    Enhance existing content using AI.

    Args:
        content: Existing markdown content
        doc_type: Document type
        config: Optional config dict

    Returns:
        Enhanced markdown content

    Raises:
        Exception: If enhancement fails
    """
    config = config or {}
    ai = GeminiAI(
        api_key=config.get("api_key"),
        model=config.get("model")
    )

    result = ai.enhance(content, doc_type)

    if not result.success:
        raise Exception(result.error or "Enhancement failed")

    return result.content or ""


def generate_summary(content: str, config: Optional[Dict] = None) -> str:
    """
    Generate executive summary from content.

    Args:
        content: Document content
        config: Optional config dict

    Returns:
        Generated summary

    Raises:
        Exception: If summarization fails
    """
    config = config or {}
    ai = GeminiAI(
        api_key=config.get("api_key"),
        model=config.get("model")
    )

    result = ai.summarize(content)

    if not result.success:
        raise Exception(result.error or "Summarization failed")

    return result.content or ""
