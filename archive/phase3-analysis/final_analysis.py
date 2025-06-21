#!/usr/bin/env python3

import re
import os

def extract_interface_text(content):
    """Extract interface text from panelTextRows section"""
    panel_text_section = re.search(r'panelTextRows:.*?DATA[^}]+', content, re.DOTALL)
    if panel_text_section:
        # Extract all DATA lines with meaningful text
        panel_matches = re.findall(r'DATA[^"]*"([^"]+)"', panel_text_section.group(0))
        # Filter out short strings and format properly
        meaningful_texts = []
        for text in panel_matches:
            if len(text) > 8 and not text.isspace():
                # Clean up the text
                clean_text = text.replace('\\', '').strip()
                if clean_text and len(clean_text) > 8:
                    meaningful_texts.append(clean_text)
        return meaningful_texts
    return []

def classify_preset_complexity(preset_names):
    """Classify preset complexity based on naming patterns"""
    categories = {
        'musical': 0,
        'technical': 0, 
        'creative': 0,
        'basic': 0
    }
    
    musical_words = ['organ', 'reverb', 'pad', 'sine', 'arp', 'chord', 'bass', 'lead', 'rhythm']
    technical_words = ['filter', 'delay', 'mod', 'feedback', 'frequency', 'sync', 'gate']
    creative_words = ['crazy', 'weird', 'evil', 'magic', 'strange', 'alien', 'robot']
    basic_words = ['basic', 'simple', 'clean', 'original', 'standard']
    
    for _, name in preset_names:
        name_lower = name.lower()
        if any(word in name_lower for word in musical_words):
            categories['musical'] += 1
        elif any(word in name_lower for word in technical_words):
            categories['technical'] += 1
        elif any(word in name_lower for word in creative_words):
            categories['creative'] += 1
        elif any(word in name_lower for word in basic_words):
            categories['basic'] += 1
        else:
            categories['creative'] += 1  # Default to creative for unique names
    
    return categories

def main():
    firmware_dir = '/mnt/c/Users/Danie/src/Claude Code/Permut8 Firmware Code/firmware/Official Firm'
    
    print("="*100)
    print("COMPREHENSIVE PERMUT8 FIRMWARE ANALYSIS REPORT")
    print("="*100)
    print()
    
    all_results = []
    
    for filename in sorted(os.listdir(firmware_dir)):
        if filename.endswith('.p8bank'):
            file_path = os.path.join(firmware_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract firmware name
            firmware_name_match = re.search(r'Firmware:\s*\{\s*Name:\s*"([^"]+)"', content)
            firmware_name = firmware_name_match.group(1) if firmware_name_match else 'Unknown'
            
            # Extract presets
            preset_pattern = r'([ABC][0-9]):\s*\{\s*(?:Name:\s*"([^"]*)"|Modified:\s*false)'
            presets = re.findall(preset_pattern, content)
            
            named_presets = [(pid, name) for pid, name in presets if name and name.strip()]
            empty_presets = [pid for pid, name in presets if not name or not name.strip()]
            
            # Extract operators
            operator_pattern = r'Operator[12]:\s*"([0-9]+)"'
            operators = re.findall(operator_pattern, content)
            non_zero_ops = [op for op in operators if op != '0']
            
            # Extract interface text
            interface_texts = extract_interface_text(content)
            
            # Extract about text
            about_match = re.search(r'About:\s*\{([^}]+)\}', content, re.DOTALL)
            about_text = about_match.group(1).strip() if about_match else ""
            
            # Classify preset complexity
            preset_categories = classify_preset_complexity(named_presets)
            
            # Determine firmware type
            if len(non_zero_ops) == 0:
                fw_type = "Buffer/Delay Effect"
            elif len(non_zero_ops) < 20:
                fw_type = "Simple Effect"
            elif len(non_zero_ops) < 40:
                fw_type = "Complex Effect"
            else:
                fw_type = "Full Synthesizer/Processor"
            
            # Determine complexity level
            complexity_score = len(non_zero_ops) + (len(named_presets) * 2)
            if complexity_score > 80:
                complexity = "High"
            elif complexity_score > 40:
                complexity = "Medium" 
            else:
                complexity = "Low"
            
            result = {
                'filename': filename,
                'firmware_name': firmware_name,
                'fw_type': fw_type,
                'complexity': complexity,
                'complexity_score': complexity_score,
                'total_presets': len(presets),
                'named_presets': len(named_presets),
                'empty_presets': len(empty_presets),
                'preset_list': named_presets,
                'operator_count': len(non_zero_ops),
                'interface_texts': interface_texts,
                'about': about_text,
                'preset_categories': preset_categories
            }
            
            all_results.append(result)
    
    # Sort by complexity score
    all_results.sort(key=lambda x: x['complexity_score'], reverse=True)
    
    # Print detailed analysis for each firmware
    for i, result in enumerate(all_results, 1):
        print(f"{i:2}. {result['firmware_name'].upper()}")
        print(f"    File: {result['filename']}")
        print(f"    Type: {result['fw_type']}")
        print(f"    Complexity: {result['complexity']} (Score: {result['complexity_score']})")
        print(f"    Presets: {result['named_presets']}/{result['total_presets']} named")
        print(f"    Operators: {result['operator_count']} non-zero")
        
        if result['interface_texts']:
            print(f"    Interface: {result['interface_texts'][0][:60]}...")
        
        # Show preset examples
        if result['preset_list']:
            print(f"    Sample Presets:")
            for j, (pid, name) in enumerate(result['preset_list'][:3]):
                print(f"      {pid}: {name}")
            if len(result['preset_list']) > 3:
                print(f"      ... and {len(result['preset_list'])-3} more")
        
        # Show preset categorization
        cats = result['preset_categories']
        if any(cats.values()):
            cat_summary = []
            for cat, count in cats.items():
                if count > 0:
                    cat_summary.append(f"{cat}:{count}")
            print(f"    Preset Types: {', '.join(cat_summary)}")
        
        # Show about excerpt
        if result['about']:
            about_lines = [line.strip().strip('"') for line in result['about'].split('\n') if line.strip() and line.strip() != '""']
            if about_lines:
                first_line = about_lines[0]
                if len(first_line) > 80:
                    first_line = first_line[:77] + "..."
                print(f"    Description: {first_line}")
        
        print()
    
    # Summary statistics
    print("="*100)
    print("SUMMARY STATISTICS")
    print("="*100)
    
    total_firmware = len(all_results)
    full_patch = len([r for r in all_results if r['named_presets'] >= 25])
    mod_patch = total_firmware - full_patch
    
    high_complexity = len([r for r in all_results if r['complexity'] == 'High'])
    medium_complexity = len([r for r in all_results if r['complexity'] == 'Medium'])
    low_complexity = len([r for r in all_results if r['complexity'] == 'Low'])
    
    print(f"Total Official Firmware: {total_firmware}")
    print(f"Full Patch Firmware (25+ presets): {full_patch}")
    print(f"Mod Patch Firmware (<25 presets): {mod_patch}")
    print()
    print(f"High Complexity: {high_complexity}")
    print(f"Medium Complexity: {medium_complexity}")
    print(f"Low Complexity: {low_complexity}")
    print()
    
    # Type distribution
    type_counts = {}
    for result in all_results:
        fw_type = result['fw_type']
        type_counts[fw_type] = type_counts.get(fw_type, 0) + 1
    
    print("Firmware Type Distribution:")
    for fw_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {fw_type}: {count}")
    print()
    
    # Total presets
    total_named_presets = sum(r['named_presets'] for r in all_results)
    total_possible_presets = sum(r['total_presets'] for r in all_results)
    
    print(f"Total Named Presets: {total_named_presets}")
    print(f"Total Possible Presets: {total_possible_presets}")
    print(f"Coverage: {total_named_presets/total_possible_presets*100:.1f}%")

if __name__ == "__main__":
    main()