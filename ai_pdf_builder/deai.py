"""
De-AI-ification Module

Removes AI-generated text patterns to make content feel more natural.
"""

import re
from typing import List


def deaiify(content: str) -> str:
    """
    Remove AI-generated text patterns from content.

    Args:
        content: Content to process

    Returns:
        Content with AI patterns reduced/removed
    """
    # Apply various transformations
    result = content

    # 1. Remove overused transition words
    result = _remove_overused_transitions(result)

    # 2. Vary sentence structure
    result = _vary_sentence_structure(result)

    # 3. Remove repetitive patterns
    result = _remove_repetitive_patterns(result)

    # 4. Simplify verbose phrases
    result = _simplify_verbose_phrases(result)

    return result


def _remove_overused_transitions(content: str) -> str:
    """Remove or replace overused AI transition words."""
    transitions = [
        (r'\bFurthermore,\s', ''),
        (r'\bMoreover,\s', ''),
        (r'\bAdditionally,\s', ''),
        (r'\bIn addition,\s', ''),
        (r'\bAdditionally,?\s', ''),
        (r'\bIt is important to note\s', 'Notably'),
        (r'\bIt should be noted\s', 'Notably'),
        (r'\bIt is worth noting\s', 'Notably'),
        (r'\bIt\'s worth noting\s', 'Notably'),
    ]

    result = content
    for pattern, replacement in transitions:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def _vary_sentence_structure(content: str) -> str:
    """Vary sentence structure to reduce AI patterns."""
    # Remove repetitive sentence starts
    result = content

    # Fix "The X is..." pattern repetition
    # Replace some instances with different structures
    the_is_count = len(re.findall(r'\bThe \w+ is', result, re.IGNORECASE))

    if the_is_count > 3:
        # Replace some instances with "X represents" or "X constitutes"
        sentences = result.split('. ')
        new_sentences = []

        for i, sentence in enumerate(sentences):
            if i % 3 == 0 and re.match(r'^The \w+ is', sentence.strip(), re.IGNORECASE):
                # Replace "The X is" with "X represents"
                sentence = re.sub(
                    r'^The (\w+) is',
                    r'\1 represents',
                    sentence.strip(),
                    flags=re.IGNORECASE
                )
            new_sentences.append(sentence)

        result = '. '.join(new_sentences)

    return result


def _remove_repetitive_patterns(content: str) -> str:
    """Remove repetitive text patterns."""
    result = content

    # Remove repeated bullet point formatting
    result = re.sub(r'(\* .+\n){3,}', lambda m: _deduplicate_bullets(m.group()), result)

    # Fix consecutive identical sentences
    sentences = result.split('. ')
    filtered = []

    for sentence in sentences:
        if sentence.strip() and (not filtered or sentence.strip() != filtered[-1].strip()):
            filtered.append(sentence)

    result = '. '.join(filtered)

    return result


def _deduplicate_bullets(bullet_block: str) -> str:
    """Remove duplicate bullet points."""
    bullets = bullet_block.split('\n')
    seen = set()
    unique = []

    for bullet in bullets:
        bullet_text = bullet.strip()
        if bullet_text and bullet_text not in seen:
            seen.add(bullet_text)
            unique.append(bullet)

    return '\n'.join(unique)


def _simplify_verbose_phrases(content: str) -> str:
    """Simplify verbose AI-generated phrases."""
    simplifications = [
        (r'\bin order to\b', 'to'),
        (r'\bfor the purpose of\b', 'for'),
        (r'\bon the basis of\b', 'based on'),
        (r'\bwith regard to\b', 'regarding'),
        (r'\bin the event that\b', 'if'),
        (r'\bdespite the fact that\b', 'although'),
        (r'\bdue to the fact that\b', 'because'),
        (r'\bat this point in time\b', 'now'),
        (r'\bin the majority of cases\b', 'usually'),
        (r'\b\belimination of unnecessary words')
    ]

    result = content
    for pattern, replacement in simplifications:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def check_ai_patterns(content: str) -> List[str]:
    """
    Check content for common AI-generated patterns.

    Args:
        content: Content to check

    Returns:
        List of detected patterns
    """
    patterns = []

    # Check for overused transitions
    transition_count = 0
    for transition in ['Furthermore', 'Moreover', 'Additionally', 'In addition']:
        if re.search(r'\b' + transition + r',', content, re.IGNORECASE):
            transition_count += 1

    if transition_count > 3:
        patterns.append(f"Overused transitions ({transition_count} instances)")

    # Check for verbose phrases
    verbose_count = 0
    for phrase in ['in order to', 'for the purpose of', 'on the basis of']:
        if re.search(r'\b' + phrase, content, re.IGNORECASE):
            verbose_count += 1

    if verbose_count > 2:
        patterns.append(f"Verbose phrases ({verbose_count} instances)")

    # Check for repetitive structure
    sentences = content.split('. ')
    if len(sentences) > 10:
        the_is_count = sum(1 for s in sentences if re.match(r'^The \w+ is', s.strip(), re.IGNORECASE))
        if the_is_count > len(sentences) * 0.4:
            patterns.append("Repetitive sentence structure (overuse of 'The X is')")

    return patterns
