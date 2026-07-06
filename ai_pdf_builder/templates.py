"""
Template Management Module

Handles loading and customization of LaTeX templates.
"""

import os
from pathlib import Path
from typing import Optional, Dict

# Template cache
_template_cache: Dict[str, str] = {}


def get_template(template_name: str) -> Optional[str]:
    """
    Get template content by name.

    Args:
        template_name: Name of the template (without .latex extension)

    Returns:
        Template content or None if not found
    """
    # Check cache first
    if template_name in _template_cache:
        return _template_cache[template_name]

    # Get template path
    template_path = get_template_path(template_name)

    if not template_path:
        return None

    # Read template content
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Cache the content
        _template_cache[template_name] = content

        return content

    except Exception:
        return None


def get_template_path(template_name: str) -> Optional[str]:
    """
    Get the full path to a template file.

    Args:
        template_name: Name of the template (without .latex extension)

    Returns:
        Full path to template file, or None if not found
    """
    # Add .latex extension if not present
    if not template_name.endswith('.latex'):
        template_name = f'{template_name}.latex'

    # Check in package templates directory
    package_dir = Path(__file__).parent
    template_path = package_dir / 'templates' / template_name

    if template_path.exists():
        return str(template_path)

    # Check in current directory
    local_path = Path(f'templates/{template_name}')
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
    package_dir = Path(__file__).parent
    template_dir = package_dir / 'templates'

    if template_dir.exists():
        for file in template_dir.glob('*.latex'):
            templates.append(file.stem)

    return sorted(templates)


def register_template(name: str, content: str) -> None:
    """
    Register a custom template.

    Args:
        name: Template name
        content: Template content
    """
    _template_cache[name] = content


def clear_cache() -> None:
    """Clear the template cache."""
    global _template_cache
    _template_cache = {}


def get_template_info(template_name: str) -> Optional[Dict]:
    """
    Get information about a template.

    Args:
        template_name: Name of the template

    Returns:
        Dict with template info or None
    """
    template_path = get_template_path(template_name)

    if not template_path:
        return None

    return {
        "name": template_name,
        "path": template_path,
        "exists": True,
    }
