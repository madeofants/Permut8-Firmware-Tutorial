#!/usr/bin/env python3
"""
Simple HTML Documentation Generator - Just Works
Combines all markdown files into a single HTML document with working navigation
"""

import os
import re
from datetime import datetime

def simple_markdown_to_html(content):
    """Convert markdown to HTML - basic but reliable"""
    # Headers
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Code blocks - escape HTML inside
    def escape_html_in_code(match):
        code_content = match.group(1)
        # Escape HTML tags inside code blocks
        code_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code>{code_content}</code></pre>'
    
    content = re.sub(r'```[\w]*\n(.*?)\n```', escape_html_in_code, content, flags=re.DOTALL)
    
    # Inline code - also escape HTML
    def escape_html_in_inline_code(match):
        code_content = match.group(1)
        code_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
        return f'<code>{code_content}</code>'
    
    content = re.sub(r'`([^`]+)`', escape_html_in_inline_code, content)
    
    # Bold and italic
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    
    # Remove internal links - they just cause problems
    content = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', content)
    
    # Lists
    content = re.sub(r'^- (.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', content, flags=re.DOTALL)
    content = re.sub(r'</ul>\s*<ul>', '', content)
    
    # Paragraphs
    paragraphs = content.split('\n\n')
    html_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p>{p}</p>'
        html_paragraphs.append(p)
    
    return '\n'.join(html_paragraphs)

def collect_all_files():
    """Get all markdown files"""
    files = []
    for root, dirs, filenames in os.walk("content"):
        for filename in sorted(filenames):
            if filename.endswith('.md'):
                full_path = os.path.join(root, filename)
                # Create simple anchor ID
                anchor_id = filename.replace('.md', '').replace('-', '_').replace(' ', '_').lower()
                display_name = filename.replace('.md', '').replace('-', ' ').replace('_', ' ').title()
                files.append({
                    'path': full_path,
                    'anchor': anchor_id,
                    'name': display_name
                })
    return files

def generate_simple_html():
    """Generate simple, working HTML"""
    files = collect_all_files()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permut8 Firmware Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }}
        
        .container {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .nav {{
            width: 300px;
            background: white;
            padding: 20px;
            height: 100vh;
            overflow-y: auto;
            position: fixed;
            border-right: 1px solid #ddd;
        }}
        
        .content {{
            margin-left: 320px;
            padding: 20px;
            background: white;
            min-height: 100vh;
        }}
        
        .nav h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        
        .nav a {{
            display: block;
            padding: 8px 12px;
            color: #666;
            text-decoration: none;
            border-radius: 4px;
            margin: 2px 0;
            font-size: 14px;
        }}
        
        .nav a:hover {{
            background: #f0f8ff;
            color: #007bff;
        }}
        
        .section {{
            margin: 40px 0;
            padding: 30px;
            border: 1px solid #eee;
            border-radius: 8px;
            background: white;
        }}
        
        .section-title {{
            background: #007bff;
            color: white;
            padding: 15px 20px;
            margin: -30px -30px 20px -30px;
            border-radius: 8px 8px 0 0;
            font-size: 18px;
            font-weight: bold;
        }}
        
        .content h1 {{ color: #2c3e50; margin-top: 0; }}
        .content h2 {{ color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; }}
        .content h3 {{ color: #7f8c8d; }}
        
        .content pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #007bff;
        }}
        
        .content code {{
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        
        .content ul, .content ol {{ margin: 15px 0; padding-left: 30px; }}
        .content li {{ margin: 8px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <h2>📚 Documentation</h2>
"""

    # Generate navigation
    for file_info in files:
        html += f'            <a href="#{file_info["anchor"]}">{file_info["name"]}</a>\n'
    
    html += """        </nav>
        
        <main class="content">
            <h1>🎛️ Permut8 Firmware Tutorial</h1>
            <div style="background: #e8f6f3; padding: 15px; border-radius: 5px; margin-bottom: 30px; border-left: 4px solid #27ae60;">
                <strong>📖 Complete Offline Documentation</strong><br>
                Generated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """<br>
                Simple navigation - click any item in the sidebar to jump to that section.
            </div>
"""

    # Generate content sections
    for file_info in files:
        try:
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            html_content = simple_markdown_to_html(content)
            
            html += f'''
            <div class="section" id="{file_info['anchor']}">
                <div class="section-title">📄 {file_info['name']}</div>
                {html_content}
            </div>
'''
        except Exception as e:
            print(f"Error processing {file_info['path']}: {e}")

    html += """        </main>
    </div>
    
    <script>
        // Simple smooth scrolling with error handling
        document.querySelectorAll('.nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    console.log('Navigated to:', href);
                } else {
                    console.error('Target not found for:', href);
                    // Fallback: try to find by partial match
                    const id = href.replace('#', '');
                    const fallback = document.getElementById(id);
                    if (fallback) {
                        fallback.scrollIntoView({ behavior: 'smooth' });
                        console.log('Fallback navigation to:', id);
                    } else {
                        console.error('No fallback found for:', id);
                    }
                }
            });
        });
        
        // Debug: Log all section IDs on page load
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('.section[id]');
            console.log('Available sections:', Array.from(sections).map(s => s.id));
        });
    </script>
</body>
</html>"""

    return html

def main():
    print("🚀 Generating Simple HTML Documentation...")
    
    try:
        html_content = generate_simple_html()
        
        output_file = "Permut8-Simple-Documentation.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML documentation generated: {output_file}")
        print(f"📄 File size: {len(html_content):,} characters")
        print(f"📍 Location: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())