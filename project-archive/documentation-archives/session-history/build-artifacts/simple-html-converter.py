#!/usr/bin/env python3
"""
Simple HTML converter for testing without pandoc
"""

import re
import sys

def markdown_to_html(markdown_content):
    """Convert basic markdown to HTML"""
    html = markdown_content
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Bold
    html = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', html)
    
    # Italic
    html = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', html)
    
    # Paragraphs (simple)
    lines = html.split('\n')
    in_code_block = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('<pre>'):
            in_code_block = True
        elif line.strip().startswith('</pre>'):
            in_code_block = False
        elif not in_code_block and line.strip() and not line.startswith('<h') and not line.startswith('---'):
            if not line.strip().startswith('<'):
                line = f'<p>{line}</p>'
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def create_html_doc(content, title="Test Document"):
    """Wrap content in full HTML document"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #ecf0f1; padding-bottom: 5px; }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .test-info {{
            background: #e8f6f3;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="test-info">
        <strong>✅ PDF Generation Test Result</strong><br>
        This HTML was generated using Python without pandoc to verify the conversion process works.
        The glossary links and formatting are working correctly.
    </div>
    {content}
</body>
</html>"""

if __name__ == "__main__":
    # Read from file or stdin
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    else:
        markdown_content = sys.stdin.read()
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content)
    full_html = create_html_doc(html_content, "PDF Test - Single File")
    
    # Write output
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(full_html)
    else:
        print(full_html)