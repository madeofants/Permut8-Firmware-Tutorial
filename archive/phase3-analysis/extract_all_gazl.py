#!/usr/bin/env python3
"""
Extract GAZL assembly from all Permut8 firmware .p8bank files
Simple approach: extract Code sections and clean quotes
"""

import os
import re
import sys
from pathlib import Path

def extract_gazl_from_p8bank(p8bank_file, output_dir):
    """Extract GAZL assembly from a single .p8bank file"""
    
    # Read the p8bank file
    with open(p8bank_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find the Code section
    code_match = re.search(r'Code:\s*\{(.*?)\n\s*\}', content, re.DOTALL)
    if not code_match:
        print(f"ERROR: No Code section found in {p8bank_file}")
        return False
    
    code_section = code_match.group(1)
    
    # Extract GAZL lines (remove quotes and clean up)
    gazl_lines = []
    for line in code_section.split('\n'):
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            # Remove surrounding quotes
            gazl_line = line[1:-1]
            gazl_lines.append(gazl_line)
    
    if not gazl_lines:
        print(f"ERROR: No GAZL lines found in {p8bank_file}")
        return False
    
    # Generate output filename
    firmware_name = Path(p8bank_file).stem.replace(' Firmware', '').replace(' ', '_').lower()
    output_file = Path(output_dir) / f"{firmware_name}.gazl"
    
    # Write GAZL file
    with open(output_file, 'w') as f:
        for line in gazl_lines:
            f.write(line + '\n')
    
    print(f"✅ Extracted {len(gazl_lines)} GAZL lines from {Path(p8bank_file).name} → {output_file.name}")
    return True

def main():
    # Configuration
    firmware_dir = "firmware/Official Firm"
    output_dir = "extracted_gazl"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .p8bank files
    p8bank_files = []
    for file in os.listdir(firmware_dir):
        if file.endswith('.p8bank'):
            p8bank_files.append(os.path.join(firmware_dir, file))
    
    if not p8bank_files:
        print("ERROR: No .p8bank files found in", firmware_dir)
        return 1
    
    print(f"🚀 Found {len(p8bank_files)} firmware files to extract")
    print(f"📁 Output directory: {output_dir}")
    print()
    
    # Extract GAZL from each firmware
    success_count = 0
    for p8bank_file in sorted(p8bank_files):
        if extract_gazl_from_p8bank(p8bank_file, output_dir):
            success_count += 1
        else:
            print(f"❌ Failed to extract from {Path(p8bank_file).name}")
    
    print()
    print(f"📊 Extraction Summary:")
    print(f"   Total firmware: {len(p8bank_files)}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {len(p8bank_files) - success_count}")
    
    if success_count == len(p8bank_files):
        print("🎉 All firmware GAZL extracted successfully!")
        return 0
    else:
        print("⚠️  Some extractions failed - check error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())