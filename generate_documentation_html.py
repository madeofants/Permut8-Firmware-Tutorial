#!/usr/bin/env python3
"""
Simple HTML Documentation Generator for Permut8 Firmware
Combines all markdown files into a single HTML document with navigation
"""

import os
import re
from pathlib import Path
from datetime import datetime

def markdown_to_html(content):
    """Convert basic markdown to HTML"""
    # Headers
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Code blocks
    content = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', content, flags=re.DOTALL)
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    
    # Bold and italic
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    
    # Links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    
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

def get_file_order():
    """Define the reading order for documentation files"""
    return [
        # Foundation
        "Documentation Project/active/content/user-guides/QUICKSTART.md",
        "Documentation Project/active/content/user-guides/cookbook/fundamentals/how-dsp-affects-sound.md",
        "Documentation Project/active/content/user-guides/tutorials/getting-audio-in-and-out.md",
        "Documentation Project/active/content/user-guides/cookbook/fundamentals/simplest-distortion.md",
        
        # Language Reference
        "Documentation Project/active/content/language/core_language_reference.md",
        "Documentation Project/active/content/language/language-syntax-reference.md",
        "Documentation Project/active/content/language/standard-library-reference.md",
        "Documentation Project/active/content/language/types-and-operators.md",
        "Documentation Project/active/content/language/core-functions.md",
        
        # Architecture
        "Documentation Project/active/content/architecture/memory-layout.md",
        "Documentation Project/active/content/architecture/memory-model.md", 
        "Documentation Project/active/content/architecture/processing-order.md",
        "Documentation Project/active/content/architecture/state-management.md",
        "Documentation Project/active/content/architecture/p8bank-format.md",
        
        # Tutorials
        "Documentation Project/active/content/user-guides/tutorials/creating-firmware-banks.md",
        "Documentation Project/active/content/user-guides/tutorials/compiler-troubleshooting-guide.md",
        "Documentation Project/active/content/user-guides/tutorials/complete-development-workflow.md",
        "Documentation Project/active/content/user-guides/tutorials/debug-your-plugin.md",
        "Documentation Project/active/content/user-guides/tutorials/mod-vs-full-architecture-guide.md",
        
        # Cookbook - Fundamentals
        "Documentation Project/active/content/user-guides/cookbook/fundamentals/basic-filter.md",
        "Documentation Project/active/content/user-guides/cookbook/fundamentals/control-flow-patterns.md",
        "Documentation Project/active/content/user-guides/cookbook/fundamentals/simplest-distortion.md",
        
        # Cookbook - Audio Effects
        "Documentation Project/active/content/user-guides/cookbook/audio-effects/bitcrusher.md",
        "Documentation Project/active/content/user-guides/cookbook/audio-effects/make-a-delay.md",
        "Documentation Project/active/content/user-guides/cookbook/audio-effects/ring-modulation.md",
        
        # Cookbook - Parameters
        "Documentation Project/active/content/user-guides/cookbook/parameters/parameter-smoothing.md",
        "Documentation Project/active/content/user-guides/cookbook/parameters/knob-to-frequency.md",
        
        # Cookbook - Visual Feedback
        "Documentation Project/active/content/user-guides/cookbook/visual-feedback/control-leds.md",
        "Documentation Project/active/content/user-guides/cookbook/visual-feedback/display-patterns.md",
        
        # Cookbook - Timing
        "Documentation Project/active/content/user-guides/cookbook/timing/sync-to-tempo.md",
        
        # Assembly and Advanced
        "Documentation Project/active/content/assembly/gazl-assembly-guide.md",
        "Documentation Project/active/content/assembly/gazl-instruction-reference.md",
    ]

def generate_html():
    """Generate the HTML documentation"""
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permut8 Firmware Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 40px; }
        h3 { color: #7f8c8d; margin-top: 30px; }
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
        pre {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }
        pre code {
            background: none;
            padding: 0;
        }
        .nav-toc {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .nav-toc h2 {
            margin-top: 0;
            color: #2c3e50;
        }
        .nav-toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .nav-toc li {
            margin: 5px 0;
        }
        .nav-toc a {
            color: #3498db;
            text-decoration: none;
            padding: 2px 0;
        }
        .nav-toc a:hover {
            text-decoration: underline;
        }
        .file-section {
            margin: 40px 0;
            padding: 20px 0;
            border-top: 1px solid #ecf0f1;
        }
        .file-title {
            background: #3498db;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-weight: bold;
        }
        blockquote {
            border-left: 4px solid #f39c12;
            background: #fef9e7;
            margin: 0;
            padding: 10px 20px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .generation-info {
            background: #e8f6f3;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            border-left: 4px solid #27ae60;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎛️ Permut8 Firmware Tutorial</h1>
        
        <div class="generation-info">
            <strong>📖 Complete Tutorial</strong><br>
            Generated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """<br>
            Complete firmware tutorial and reference combined into a single HTML document for offline use.
        </div>

        <div class="nav-toc">
            <h2>📋 Table of Contents</h2>
            <ul>
"""

    # Build navigation and content
    file_order = get_file_order()
    toc_items = []
    sections = []
    
    for file_path in file_order:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create anchor ID from filename
                filename = os.path.basename(file_path).replace('.md', '')
                anchor_id = filename.lower().replace(' ', '-').replace('_', '-')
                
                # Add to TOC
                display_name = filename.replace('-', ' ').replace('_', ' ').title()
                toc_items.append(f'<li><a href="#{anchor_id}">{display_name}</a></li>')
                
                # Convert content to HTML
                html_content_section = markdown_to_html(content)
                
                # Add section
                sections.append(f'''
<div class="file-section" id="{anchor_id}">
    <div class="file-title">📄 {display_name}</div>
    {html_content_section}
</div>
''')
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
    # Complete the HTML
    html_content += '\n'.join(toc_items)
    html_content += """
            </ul>
        </div>
"""
    
    html_content += '\n'.join(sections)
    
    html_content += """
        <div style="margin-top: 60px; padding-top: 20px; border-top: 2px solid #ecf0f1; text-align: center; color: #7f8c8d;">
            <p><strong>Permut8 Firmware Tutorial</strong></p>
            <p>Generated on """ + datetime.now().strftime("%B %d, %Y") + """ | Complete offline reference</p>
        </div>
    </div>
</body>
</html>"""

    return html_content

def main():
    """Main function to generate HTML documentation"""
    print("🚀 Generating Permut8 Documentation HTML...")
    
    try:
        html_content = generate_html()
        
        # Write to main directory
        output_file = "Permut8-Firmware-Tutorial.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML documentation generated: {output_file}")
        print(f"📄 File size: {len(html_content):,} characters")
        print(f"📍 Location: {os.path.abspath(output_file)}")
        print("\n🌐 Open the HTML file in any web browser for offline reading!")
        
    except Exception as e:
        print(f"❌ Error generating HTML: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()