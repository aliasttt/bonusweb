#!/usr/bin/env python
"""
Script to find untranslated English strings in Django templates.
This script searches for English text that should be wrapped in {% trans %} tags.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Common English words that indicate English text (not comprehensive, but helpful)
ENGLISH_INDICATORS = [
    r'\bthe\b', r'\ba\b', r'\ban\b', r'\bis\b', r'\bare\b', r'\bwas\b', r'\bwere\b',
    r'\bthis\b', r'\bthat\b', r'\bthese\b', r'\bthose\b', r'\bwith\b', r'\bfrom\b',
    r'\bfor\b', r'\band\b', r'\bor\b', r'\bnot\b', r'\bcan\b', r'\bcould\b', r'\bshould\b',
    r'\bwill\b', r'\bwould\b', r'\bmay\b', r'\bmight\b', r'\bmust\b', r'\bshall\b',
    r'\byou\b', r'\byour\b', r'\bwe\b', r'\bour\b', r'\bthey\b', r'\btheir\b',
    r'\bwhat\b', r'\bwhen\b', r'\bwhere\b', r'\bwhy\b', r'\bhow\b', r'\bwho\b',
]

# Patterns to identify English text in HTML
ENGLISH_PATTERNS = [
    r'[A-Z][a-z]+ [A-Z][a-z]+',  # Title Case words
    r'\b[A-Z][a-z]+\b',  # Capitalized words
]

# Common HTML tags that might contain translatable text
TEXT_CONTAINING_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'button', 'label',
    'title', 'li', 'td', 'th', 'div', 'strong', 'em', 'b', 'i'
]

# Patterns to skip (already translated or not translatable)
SKIP_PATTERNS = [
    r'{%\s*trans\s+',  # Already has trans tag
    r'{%\s*block\s+',  # Block tags
    r'{%\s*extends\s+',  # Extends
    r'{%\s*load\s+',  # Load tags
    r'{%\s*if\s+',  # If statements
    r'{%\s*for\s+',  # For loops
    r'{{.*?}}',  # Django variables
    r'data-lucide=',  # Icon names
    r'href=',  # URLs
    r'src=',  # Image sources
    r'class=',  # CSS classes
    r'id=',  # IDs
    r'style=',  # Inline styles
    r'<!--.*?-->',  # HTML comments
    r'<script.*?</script>',  # Script tags
    r'<style.*?</style>',  # Style tags
    r'^\s*$',  # Empty lines
    r'^\s*#',  # Comments
    r'^\s*//',  # JS comments
]

def is_skip_pattern(text):
    """Check if text matches skip patterns."""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return True
    return False

def extract_text_from_html(html_content):
    """Extract text content from HTML that might need translation."""
    # Remove script and style tags
    html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Extract text from common tags
    text_matches = []
    
    # Find text in tags like <h1>Text</h1>, <p>Text</p>, etc.
    tag_pattern = r'<(?:h[1-6]|p|span|a|button|label|li|td|th|div|strong|em|b|i|title)[^>]*>([^<]+)</(?:h[1-6]|p|span|a|button|label|li|td|th|div|strong|em|b|i|title)>'
    matches = re.finditer(tag_pattern, html_content, re.IGNORECASE)
    
    for match in matches:
        text = match.group(1).strip()
        if text and len(text) > 2 and not is_skip_pattern(text):
            # Check if it looks like English
            if any(re.search(indicator, text, re.IGNORECASE) for indicator in ENGLISH_INDICATORS):
                text_matches.append({
                    'text': text,
                    'line': html_content[:match.start()].count('\n') + 1,
                    'context': html_content[max(0, match.start()-50):match.end()+50]
                })
    
    # Also find standalone text nodes (text not in tags but between tags)
    standalone_pattern = r'>([A-Z][^<]{3,})<'
    matches = re.finditer(standalone_pattern, html_content)
    
    for match in matches:
        text = match.group(1).strip()
        if text and len(text) > 2 and not is_skip_pattern(text):
            if any(re.search(indicator, text, re.IGNORECASE) for indicator in ENGLISH_INDICATORS):
                text_matches.append({
                    'text': text,
                    'line': html_content[:match.start()].count('\n') + 1,
                    'context': html_content[max(0, match.start()-50):match.end()+50]
                })
    
    return text_matches

def find_untranslated_in_template(template_path):
    """Find untranslated strings in a template file."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {template_path}: {e}")
        return []
    
    # Check if template has {% load i18n %}
    has_i18n = '{% load i18n %}' in content or "{% load i18n %}" in content
    
    # Find all text that might need translation
    potential_texts = extract_text_from_html(content)
    
    # Filter out texts that are already in {% trans %} tags
    untranslated = []
    for item in potential_texts:
        text = item['text']
        # Check if this text is already wrapped in {% trans %}
        # Look for {% trans "text" %} or {% trans 'text' %} patterns
        escaped_text = re.escape(text)
        trans_pattern = r'{%\s*trans\s+["\']' + escaped_text + r'["\']\s*%}'
        if not re.search(trans_pattern, content, re.IGNORECASE):
            # Also check for blocktrans
            blocktrans_pattern = r'{%\s*blocktrans\s+.*?' + escaped_text + r'.*?{%\s*endblocktrans\s*%}'
            if not re.search(blocktrans_pattern, content, re.DOTALL | re.IGNORECASE):
                untranslated.append({
                    'text': text,
                    'line': item['line'],
                    'has_i18n': has_i18n
                })
    
    return untranslated

def scan_templates(templates_dir='templates'):
    """Scan all templates for untranslated strings."""
    templates_path = Path(templates_dir)
    if not templates_path.exists():
        print(f"Templates directory not found: {templates_dir}")
        return
    
    results = defaultdict(list)
    total_untranslated = 0
    
    # Find all HTML template files
    for template_file in templates_path.rglob('*.html'):
        relative_path = template_file.relative_to(templates_path)
        untranslated = find_untranslated_in_template(template_file)
        
        if untranslated:
            results[str(relative_path)] = untranslated
            total_untranslated += len(untranslated)
    
    # Print results
    print("=" * 80)
    print("UNTRANSLATED STRINGS REPORT")
    print("=" * 80)
    print(f"\nTotal templates scanned: {len(list(templates_path.rglob('*.html')))}")
    print(f"Templates with untranslated strings: {len(results)}")
    print(f"Total untranslated strings found: {total_untranslated}\n")
    
    for template_path, strings in sorted(results.items()):
        print(f"\n{'='*80}")
        print(f"File: {template_path}")
        print(f"{'='*80}")
        
        for i, item in enumerate(strings, 1):
            print(f"\n{i}. Line {item['line']}")
            print(f"   Text: {item['text'][:100]}")
            if not item['has_i18n']:
                print(f"   ⚠️  Missing: {{% load i18n %}}")
            print(f"   Suggested: {{% trans \"{item['text']}\" %}}")
    
    # Save to file
    output_file = 'untranslated_strings_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("UNTRANSLATED STRINGS REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total templates with untranslated strings: {len(results)}\n")
        f.write(f"Total untranslated strings: {total_untranslated}\n\n")
        
        for template_path, strings in sorted(results.items()):
            f.write(f"\n{'='*80}\n")
            f.write(f"File: {template_path}\n")
            f.write(f"{'='*80}\n\n")
            
            for i, item in enumerate(strings, 1):
                f.write(f"{i}. Line {item['line']}\n")
                f.write(f"   Text: {item['text']}\n")
                if not item['has_i18n']:
                    f.write(f"   ⚠️  Missing: {{% load i18n %}}\n")
                f.write(f"   Suggested: {{% trans \"{item['text']}\" %}}\n\n")
    
    print(f"\n\nReport saved to: {output_file}")
    return results

if __name__ == '__main__':
    scan_templates()

