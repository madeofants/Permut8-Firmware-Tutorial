#!/usr/bin/env python3

import re
import os

def extract_firmware_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract firmware name from Firmware section
        firmware_name_match = re.search(r'Firmware:\s*\{\s*Name:\s*"([^"]+)"', content)
        firmware_name = firmware_name_match.group(1) if firmware_name_match else 'Unknown'
        
        # Extract all preset names
        preset_pattern = r'([ABC][0-9]):\s*\{\s*(?:Name:\s*"([^"]*)"|Modified:\s*false)'
        presets = re.findall(preset_pattern, content)
        
        # Count non-empty presets
        named_presets = []
        empty_presets = []
        
        for preset_id, preset_name in presets:
            if preset_name and preset_name.strip():
                named_presets.append((preset_id, preset_name))
            else:
                empty_presets.append(preset_id)
        
        # Look for operators
        operator_pattern = r'Operator[12]:\s*"([0-9]+)"'
        operators = re.findall(operator_pattern, content)
        non_zero_ops = [op for op in operators if op != '0']
        
        # Extract about section
        about_match = re.search(r'About:\s*\{([^}]+)\}', content, re.DOTALL)
        about_text = about_match.group(1).strip() if about_match else None
        
        # Extract panel text more comprehensively
        panel_text_section = re.search(r'panelTextRows:.*?DATA[^}]+', content, re.DOTALL)
        panel_texts = []
        if panel_text_section:
            panel_matches = re.findall(r'DATA[^"]*"([^"]+)"', panel_text_section.group(0))
            panel_texts = [text for text in panel_matches if len(text) > 5]  # Filter out short strings
        
        # Get operator usage details
        operator_usage = {}
        for preset_id, _ in presets:
            preset_section = re.search(rf'{preset_id}:\s*\{{([^}}]+)\}}', content, re.DOTALL)
            if preset_section:
                op1_match = re.search(r'Operator1:\s*"([0-9]+)"', preset_section.group(1))
                op2_match = re.search(r'Operator2:\s*"([0-9]+)"', preset_section.group(1))
                op1 = op1_match.group(1) if op1_match else '0'
                op2 = op2_match.group(1) if op2_match else '0'
                operator_usage[preset_id] = (op1, op2)
        
        return {
            'firmware_name': firmware_name,
            'total_presets': len(presets),
            'named_presets': len(named_presets),
            'empty_presets': len(empty_presets),
            'preset_details': named_presets,
            'empty_preset_ids': empty_presets,
            'has_operators': len(non_zero_ops) > 0,
            'operator_count': len(non_zero_ops),
            'about': about_text,
            'panel_texts': panel_texts,
            'operator_usage': operator_usage
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    # Process all firmware files
    firmware_dir = '/mnt/c/Users/Danie/src/Claude Code/Permut8 Firmware Code/firmware/Official Firm'
    results = {}

    for filename in sorted(os.listdir(firmware_dir)):
        if filename.endswith('.p8bank'):
            file_path = os.path.join(firmware_dir, filename)
            print(f"Processing {filename}...")
            results[filename] = extract_firmware_info(file_path)

    # Output results
    print("\n" + "="*80)
    print("FIRMWARE ANALYSIS REPORT")
    print("="*80)
    
    for filename, info in results.items():
        if 'error' not in info:
            print(f"\n=== {filename} ===")
            print(f"Firmware Name: {info['firmware_name']}")
            print(f"Total Presets: {info['total_presets']}")
            print(f"Named Presets: {info['named_presets']}")
            print(f"Empty Presets: {info['empty_presets']}")
            print(f"Has Operators: {info['has_operators']} ({info['operator_count']} non-zero)")
            
            if info['preset_details']:
                print("Sample Named Presets:")
                for i, (pid, pname) in enumerate(info['preset_details'][:5]):
                    print(f"  {pid}: {pname}")
                if len(info['preset_details']) > 5:
                    print(f"  ... and {len(info['preset_details'])-5} more")
            
            if info['panel_texts']:
                print(f"Interface Text: {info['panel_texts'][0]}")
            
            if info['about']:
                about_excerpt = info['about'][:200].replace('\n', ' ').strip()
                print(f"About: {about_excerpt}...")
                
        else:
            print(f"\nERROR processing {filename}: {info['error']}")
    
    # Summary analysis
    print("\n" + "="*80)
    print("SUMMARY ANALYSIS")
    print("="*80)
    
    full_patch_count = 0
    mod_patch_count = 0
    
    for filename, info in results.items():
        if 'error' not in info:
            if info['named_presets'] >= 25:
                full_patch_count += 1
            else:
                mod_patch_count += 1
    
    print(f"Total Firmware: 13")
    print(f"Full Patch Firmware (25+ presets): {full_patch_count}")
    print(f"Mod Patch Firmware (<25 presets): {mod_patch_count}")
    print()
    
    # Complexity analysis
    print("COMPLEXITY RANKING (by operator usage and preset count):")
    complexity_scores = []
    for filename, info in results.items():
        if 'error' not in info:
            score = info['operator_count'] + (info['named_presets'] * 2)
            complexity_scores.append((score, filename, info))
    
    complexity_scores.sort(reverse=True)
    for i, (score, filename, info) in enumerate(complexity_scores):
        complexity = "High" if score > 80 else "Medium" if score > 40 else "Low"
        print(f"{i+1:2}. {info['firmware_name']:15} ({filename:25}) - {complexity:6} (Score: {score})")
    print()
    
    # Operator usage patterns
    print("FIRMWARE TYPE CLASSIFICATION:")
    for filename, info in results.items():
        if 'error' not in info:
            if info['operator_count'] == 0:
                fw_type = "Buffer/Delay Effect"
            elif info['operator_count'] < 20:
                fw_type = "Simple Effect"
            elif info['operator_count'] < 40:
                fw_type = "Complex Effect" 
            else:
                fw_type = "Full Synthesizer/Processor"
            
            print(f"{info['firmware_name']:15} - {fw_type:25} ({info['operator_count']} ops, {info['named_presets']} presets)")

if __name__ == "__main__":
    main()