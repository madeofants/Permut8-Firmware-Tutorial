#!/usr/bin/env python3
"""
Enhanced HTML Documentation Generator for Permut8 Firmware
Combines all markdown files into a single HTML document with organized navigation
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

def organize_content():
    """Organize all documentation files into logical groups for navigation"""
    base_path = "content"
    
    # Simple, clear content groups
    content_groups = {
        'start': {
            'title': '🎯 Start Here',
            'files': [],
            'expanded': True,
            'patterns': ['QUICKSTART', 'how-to-use-this-documentation']
        },
        'language': {
            'title': '📖 Language Reference',
            'files': [],
            'expanded': False,
            'paths': ['language/']
        },
        'tutorials': {
            'title': '🎓 Tutorials',
            'files': [],
            'expanded': False,
            'paths': ['user-guides/tutorials/']
        },
        'cookbook_fundamentals': {
            'title': '🍳 Cookbook - Fundamentals',
            'files': [],
            'expanded': False,
            'paths': ['user-guides/cookbook/fundamentals/']
        },
        'cookbook_effects': {
            'title': '🎵 Cookbook - Audio Effects',
            'files': [],
            'expanded': False,
            'paths': ['user-guides/cookbook/audio-effects/']
        },
        'cookbook_timing': {
            'title': '⏱️ Cookbook - Timing & Utilities',
            'files': [],
            'expanded': False,
            'paths': ['user-guides/cookbook/timing/', 'user-guides/cookbook/utilities/', 'user-guides/cookbook/visual-feedback/']
        },
        'cookbook_advanced': {
            'title': '🌊 Cookbook - Advanced',
            'files': [],
            'expanded': False,
            'paths': ['user-guides/cookbook/spectral-processing/', 'user-guides/cookbook/advanced/']
        },
        'reference': {
            'title': '📚 Reference Docs',
            'files': [],
            'expanded': False,
            'paths': ['reference/']
        },
        'architecture': {
            'title': '🏗️ Architecture',
            'files': [],
            'expanded': False,
            'paths': ['architecture/']
        },
        'performance': {
            'title': '⚡ Performance',
            'files': [],
            'expanded': False,
            'paths': ['performance/']
        },
        'integration': {
            'title': '🔗 Integration',
            'files': [],
            'expanded': False,
            'paths': ['integration/']
        },
        'assembly': {
            'title': '⚙️ Assembly',
            'files': [],
            'expanded': False,
            'paths': ['assembly/']
        },
        'advanced': {
            'title': '🔬 Advanced Topics',
            'files': [],
            'expanded': False,
            'paths': ['fundamentals/', 'index/']
        }
    }
    
    # Collect all markdown files
    all_files = []
    for root, dirs, filenames in os.walk(base_path):
        for filename in sorted(filenames):
            if filename.endswith('.md'):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, base_path)
                all_files.append({
                    'full_path': full_path,
                    'rel_path': rel_path,
                    'filename': filename,
                    'display_name': filename.replace('.md', '').replace('-', ' ').replace('_', ' ').title()
                })
    
    # Categorize files into groups
    for file_info in all_files:
        categorized = False
        
        # Check start patterns first
        if 'patterns' in content_groups['start']:
            for pattern in content_groups['start']['patterns']:
                if pattern.lower() in file_info['filename'].lower():
                    content_groups['start']['files'].append(file_info)
                    categorized = True
                    break
        
        if not categorized:
            # Check other groups by path
            for group_name, group_info in content_groups.items():
                if group_name == 'start':
                    continue
                if 'paths' in group_info:
                    for path in group_info['paths']:
                        if path in file_info['rel_path']:
                            group_info['files'].append(file_info)
                            categorized = True
                            break
                if categorized:
                    break
        
        # Default to advanced if not categorized
        if not categorized:
            content_groups['advanced']['files'].append(file_info)
    
    return content_groups

def generate_navigation_html(content_groups):
    """Generate the sidebar navigation HTML"""
    nav_html = '''
    <nav class="sidebar">
        <div class="sidebar-header">
            <h2>📋 Navigation</h2>
        </div>
'''
    
    for group_name, group_info in content_groups.items():
        if not group_info['files']:
            continue
            
        expanded_class = ''
        nav_html += f'''
        <div class="nav-section {expanded_class}" id="nav-{group_name}">
            <div class="nav-section-header">
                {group_info['title']} <span class="file-count">({len(group_info['files'])})</span>
            </div>
            <div class="nav-section-content">
'''
        
        for file_info in group_info['files']:
            anchor_id = create_anchor_id(file_info['filename'])
            nav_html += f'                <a href="#{anchor_id}" class="nav-link">{file_info["display_name"]}</a>\n'
        
        nav_html += '            </div>\n        </div>\n'
    
    nav_html += '    </nav>\n'
    return nav_html

def create_anchor_id(filename):
    """Create consistent anchor ID from filename"""
    return filename.replace('.md', '').lower().replace(' ', '-').replace('_', '-')

def generate_html():
    """Generate the HTML documentation with organized navigation"""
    
    # Organize content into groups
    content_groups = organize_content()
    
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
            margin: 0;
            padding: 0;
            background-color: #fafafa;
        }
        
        .documentation-container {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .sidebar {
            position: sticky;
            top: 20px;
            height: calc(100vh - 40px);
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .sidebar-header h2 {
            margin: 0 0 20px 0;
            color: #495057;
            font-size: 18px;
        }
        
        .nav-section {
            margin-bottom: 15px;
        }
        
        .nav-section-header {
            cursor: pointer;
            padding: 8px 12px;
            background: #e9ecef;
            border-radius: 6px;
            font-weight: 600;
            color: #495057;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .nav-section-header:hover {
            background: #dee2e6;
        }
        
        .file-count {
            font-size: 12px;
            color: #868e96;
            font-weight: 400;
        }
        
        .nav-section-content {
            display: block;
        }
        
        .nav-link {
            display: block;
            padding: 6px 16px;
            color: #6c757d;
            text-decoration: none;
            font-size: 14px;
            border-radius: 4px;
            margin: 2px 0;
        }
        
        .nav-link:hover {
            background: #dee2e6;
            color: #495057;
        }
        
        .nav-link.active {
            background: #007bff;
            color: white;
            font-weight: 600;
        }
        
        .content {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: calc(100vh - 40px);
        }
        
        .content h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .content h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 40px; }
        .content h3 { color: #7f8c8d; margin-top: 30px; }
        
        .content pre { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto;
            border-left: 4px solid #17a2b8;
        }
        
        .content code { 
            background: #f8f9fa; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        .content ul, .content ol { margin: 15px 0; padding-left: 30px; }
        .content li { margin: 8px 0; }
        
        .content a { 
            color: #3498db; 
            text-decoration: none; 
        }
        
        .content a:hover { 
            color: #2980b9; 
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
        
        .generation-info {
            background: #e8f6f3;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
            border-left: 4px solid #27ae60;
        }
        
        @media (max-width: 768px) {
            .documentation-container {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                position: relative;
                height: auto;
                margin-bottom: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="documentation-container">
""" + generate_navigation_html(content_groups) + """
        <main class="content">
            <h1>🎛️ Permut8 Firmware Tutorial</h1>
            <div class="generation-info">
                <strong>📖 Complete Offline Documentation</strong><br>
                Generated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """<br>
                This documentation contains all Permut8 firmware resources organized for easy navigation.
            </div>
"""

    # Generate content sections
    used_ids = set()
    
    for group_name, group_info in content_groups.items():
        for file_info in group_info['files']:
            try:
                with open(file_info['full_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create unique anchor ID
                base_anchor_id = create_anchor_id(file_info['filename'])
                anchor_id = base_anchor_id
                counter = 1
                while anchor_id in used_ids:
                    anchor_id = f"{base_anchor_id}-{counter}"
                    counter += 1
                used_ids.add(anchor_id)
                
                # Convert content to HTML
                html_content_section = markdown_to_html(content)
                
                # Add section
                html_content += f'''
<div class="file-section" id="{anchor_id}">
    <div class="file-title">📄 {file_info["display_name"]}</div>
    {html_content_section}
</div>
'''
                
            except Exception as e:
                print(f"Error processing {file_info['full_path']}: {e}")

    html_content += """
        </main>
    </div>
    
    <script>
        function updateActiveSection() {
            const sections = document.querySelectorAll('.file-section');
            const navLinks = document.querySelectorAll('.nav-link');
            
            sections.forEach((section) => {
                const rect = section.getBoundingClientRect();
                if (rect.top <= 100 && rect.bottom >= 100) {
                    navLinks.forEach(link => link.classList.remove('active'));
                    const activeLink = document.querySelector(`[href="#${section.id}"]`);
                    if (activeLink) activeLink.classList.add('active');
                }
            });
        }
        
        // Initialize everything when DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {
            // Set up nav link clicks for smooth scrolling
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const target = document.querySelector(link.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            });
        });
        
        window.addEventListener('scroll', updateActiveSection);
        window.addEventListener('load', updateActiveSection);
    </script>
</body>
</html>"""

    return html_content

def main():
    """Main function to generate HTML documentation"""
    print("🚀 Generating Permut8 Documentation HTML with organized navigation...")
    
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
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())