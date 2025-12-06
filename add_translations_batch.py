#!/usr/bin/env python
"""
Helper script to batch-add translation tags to Django templates.
This script helps identify and wrap English text in {% trans %} tags.
"""

import re
from pathlib import Path

def add_translation_tags_to_file(file_path):
    """Add {% trans %} tags around English text in a template file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Check if {% load i18n %} exists
    if '{% load i18n %}' not in content and "{% load i18n %}" not in content:
        # Add {% load i18n %} after {% extends %} or at the top
        if '{% extends' in content:
            content = re.sub(
                r'({% extends[^%]+%})',
                r'\1\n{% load i18n %}',
                content,
                count=1
            )
        else:
            content = '{% load i18n %}\n' + content
    
    # Patterns for common English text that needs translation
    # This is a helper - manual review is still needed
    
    changes_made = []
    
    # Pattern 1: Text in title tags
    def wrap_title(match):
        text = match.group(1)
        if not text.strip().startswith('{%') and len(text.strip()) > 2:
            changes_made.append(f"Title: {text[:50]}")
            return f'{% trans "{text}" %}'
        return match.group(0)
    
    # Pattern 2: Text in headings (h1-h6)
    def wrap_heading(match):
        tag = match.group(1)
        text = match.group(2)
        attrs = match.group(3) if match.group(3) else ''
        if not text.strip().startswith('{%') and len(text.strip()) > 2:
            # Check if it's not already translated
            if '{% trans' not in text:
                changes_made.append(f"Heading: {text[:50]}")
                return f'<{tag}{attrs}>{% trans "{text}" %}</{tag}>'
        return match.group(0)
    
    # Pattern 3: Text in paragraphs
    def wrap_paragraph(match):
        tag = match.group(1)
        text = match.group(2)
        attrs = match.group(3) if match.group(3) else ''
        if not text.strip().startswith('{%') and len(text.strip()) > 5:
            if '{% trans' not in text and not text.strip().startswith('{{'):
                changes_made.append(f"Paragraph: {text[:50]}")
                return f'<{tag}{attrs}>{% trans "{text}" %}</{tag}>'
        return match.group(0)
    
    # Note: This is a helper script. Manual review and adjustment is required
    # because automatic detection of translatable text is complex.
    
    if changes_made or content != original_content:
        return content, changes_made
    return None, []

if __name__ == '__main__':
    print("This is a helper script for adding translation tags.")
    print("Manual review and adjustment is required for each template.")
    print("\nUsage:")
    print("1. Review each template file")
    print("2. Wrap English text in {% trans \"text\" %} tags")
    print("3. Ensure {% load i18n %} is at the top")
    print("4. Run find_untranslated_strings.py to check for remaining strings")

