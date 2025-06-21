#!/usr/bin/env python3
"""
Batch decompile all GAZL files to Impala
Simple approach: run decompiler on all extracted GAZL files
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    gazl_dir = "extracted_gazl"
    
    # Find all .gazl files
    gazl_files = []
    for file in os.listdir(gazl_dir):
        if file.endswith('.gazl'):
            gazl_files.append(os.path.join(gazl_dir, file))
    
    if not gazl_files:
        print("ERROR: No .gazl files found in", gazl_dir)
        return 1
    
    print(f"🚀 Found {len(gazl_files)} GAZL files to decompile")
    print()
    
    # Decompile each GAZL file
    success_count = 0
    for gazl_file in sorted(gazl_files):
        firmware_name = Path(gazl_file).stem
        print(f"🔄 Decompiling {firmware_name}...")
        
        try:
            # Run the decompiler
            result = subprocess.run([
                sys.executable, 'gazl_to_impala_decompiler.py', gazl_file
            ], capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                print(f"✅ {firmware_name}: {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"❌ {firmware_name}: FAILED")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                    
        except Exception as e:
            print(f"❌ {firmware_name}: Exception - {e}")
    
    print()
    print(f"📊 Decompilation Summary:")
    print(f"   Total GAZL files: {len(gazl_files)}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {len(gazl_files) - success_count}")
    
    if success_count == len(gazl_files):
        print("🎉 All GAZL files decompiled successfully!")
        return 0
    else:
        print("⚠️  Some decompilations failed - check error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())