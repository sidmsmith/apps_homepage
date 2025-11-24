"""
Script to apply extracted theming data to apps_homepage
Usage: python apply_theming.py theming.json
"""
import json
import sys
import re
import os
from pathlib import Path

def apply_theming(theming_file, output_file=None):
    """Apply theming from JSON file to index.html"""
    
    # Determine output file path
    if output_file is None:
        # If theming_file is in apps_homepage, use that directory
        theming_path = Path(theming_file)
        if 'apps_homepage' in str(theming_path.parent):
            output_file = theming_path.parent / 'index.html'
        else:
            # Try relative to script location
            script_dir = Path(__file__).parent
            output_file = script_dir / 'index.html'
    
    # Ensure paths are Path objects
    theming_file = Path(theming_file)
    output_file = Path(output_file)
    
    # Read theming data
    try:
        with open(theming_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f'ERROR: Could not find theming file: {theming_file}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f'ERROR: Invalid JSON in theming file: {e}')
        sys.exit(1)
    
    # Extract data - handle different possible structures
    theming = data.get('theming', {})
    if not theming and 'css_variables' in data:
        # Alternative structure where theming is at root
        theming = data
    
    suggestions = data.get('suggested_colors', {})
    if not suggestions and 'theming' in data:
        # Try to get from computed_styles if available
        computed = theming.get('computed_styles', {})
        if computed:
            suggestions = {
                'background': computed.get('body_background') or computed.get('html_background'),
                'text': computed.get('body_color')
            }
    
    # Extract key values
    css_vars = theming.get('css_variables', {})
    suggested = suggestions
    
    # Read current index.html
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f'ERROR: Could not find index.html at: {output_file}')
        sys.exit(1)
    
    # Build new CSS variables
    new_vars = {}
    
    # Map extracted variables to our naming convention from suggested_colors
    if suggested.get('primary'):
        new_vars['--primary'] = suggested['primary']
    if suggested.get('background'):
        # Convert rgb() to hex if needed
        bg = suggested['background']
        if bg.startswith('rgb'):
            # Simple conversion (for common cases)
            new_vars['--bg-dark'] = bg
        else:
            new_vars['--bg-dark'] = bg
    if suggested.get('card_bg'):
        new_vars['--card-bg'] = suggested['card_bg']
    elif css_vars.get('--card-bg'):
        new_vars['--card-bg'] = css_vars['--card-bg']
    
    if suggested.get('text'):
        new_vars['--text'] = suggested['text']
    if suggested.get('border'):
        new_vars['--border'] = suggested['border']
    
    # Try to find colors from computed styles if not in suggested_colors
    computed_styles = theming.get('computed_styles', {})
    if not new_vars.get('--bg-dark') and computed_styles.get('body_background'):
        new_vars['--bg-dark'] = computed_styles['body_background']
    if not new_vars.get('--text') and computed_styles.get('body_color'):
        new_vars['--text'] = computed_styles['body_color']
    
    # Also try to use existing CSS variables if they exist (prioritize these)
    priority_keys = ['--bg-dark', '--card-bg', '--input-bg', '--border', '--text', 
                     '--primary', '--success', '--orange', '--purple', '--secondary']
    for key in priority_keys:
        if key in css_vars and not new_vars.get(key):
            new_vars[key] = css_vars[key]
    
    # Look for Manhattan-specific color variables that might be useful
    manh_color_map = {
        '--manh-color-4': '--card-bg',  # Common card background
        '--manh-color-5': '--input-bg',  # Common input background
        '--manh-white-background': '--card-bg',
        '--manh-dark-popover-header-color': '--card-bg',
    }
    
    for manh_key, our_key in manh_color_map.items():
        if manh_key in css_vars and not new_vars.get(our_key):
            new_vars[our_key] = css_vars[manh_key]
    
    # If we still don't have card-bg, derive it from background
    if not new_vars.get('--card-bg') and new_vars.get('--bg-dark'):
        # Make card slightly lighter than background
        new_vars['--card-bg'] = new_vars['--bg-dark']  # Will update manually if needed
    
    # Ensure we have at least basic colors - use defaults if missing
    if not new_vars.get('--bg-dark'):
        print('WARNING: No background color found, using default')
        new_vars['--bg-dark'] = '#121212'
    if not new_vars.get('--card-bg'):
        new_vars['--card-bg'] = '#1e1e1e'
    if not new_vars.get('--text'):
        new_vars['--text'] = '#e0e0e0'
    if not new_vars.get('--primary'):
        new_vars['--primary'] = suggested.get('primary', '#3B82F6') or '#0d6efd'
    if not new_vars.get('--border'):
        new_vars['--border'] = '#333'
    if not new_vars.get('--input-bg'):
        new_vars['--input-bg'] = '#2d2d2d'
    
    # Keep existing useful variables
    existing_vars = ['--success', '--orange', '--purple', '--secondary', '--red-text', '--blue-select', '--shadow']
    for key in existing_vars:
        if key not in new_vars:
            # Try to find equivalent in css_vars or use defaults
            if key == '--success' and '--mawc-global-color-success-600' in css_vars:
                new_vars['--success'] = css_vars['--mawc-global-color-success-600']
            elif key == '--success':
                new_vars['--success'] = '#28a745'
            elif key == '--orange':
                new_vars['--orange'] = '#e67700'
            elif key == '--purple':
                new_vars['--purple'] = '#9c27b0'
            elif key == '--secondary':
                new_vars['--secondary'] = '#6c757d'
            elif key == '--red-text':
                new_vars['--red-text'] = '#ff6b6b'
            elif key == '--blue-select':
                new_vars['--blue-select'] = '#339af0'
            elif key == '--shadow':
                new_vars['--shadow'] = '0 4px 12px rgba(0,0,0,0.3)'
            elif key == '--light-bg':
                new_vars['--light-bg'] = new_vars.get('--input-bg', '#2d2d2d')
    
    # Update CSS variables in :root
    var_block = '\n'.join([f'      {key}: {value};' for key, value in sorted(new_vars.items())])
    
    # Replace :root block - use a more flexible pattern
    pattern = r'(:root\s*\{[^}]*\})'
    
    if re.search(pattern, html_content, re.DOTALL):
        replacement = f':root {{\n{var_block}\n    }}'
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    else:
        # Insert after <style> tag
        html_content = html_content.replace('<style>', f'<style>\n    :root {{\n{var_block}\n    }}\n\n')
    
    # Write updated HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f'SUCCESS: Theming applied to {output_file}')
    print(f'Applied {len(new_vars)} CSS variables')
    print('\nApplied variables:')
    for key, value in sorted(new_vars.items()):
        print(f'  {key}: {value}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python apply_theming.py <theming.json>")
        print("\nFirst, extract theming using the browser script:")
        print("  1. Open the page in Chrome")
        print("  2. Open DevTools (F12) > Console")
        print("  3. Paste the contents of extract_theming_from_browser.js")
        print("  4. Save the output to theming.json")
        print("\nThen run this script to apply it.")
        sys.exit(1)
    
    theming_file = sys.argv[1]
    apply_theming(theming_file)

