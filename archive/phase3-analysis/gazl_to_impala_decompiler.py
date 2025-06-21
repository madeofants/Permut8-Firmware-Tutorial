#!/usr/bin/env python3
"""
GAZL to Impala Decompiler
Converts GAZL assembly back to Impala source code for analysis
"""

import re
import sys
from typing import List, Dict, Tuple, Optional

class GazlDecompiler:
    def __init__(self):
        self.constants = {}
        self.globals = {}
        self.functions = {}
        self.data_sections = {}
        self.current_function = None
        self.function_locals = {}
        self.function_params = {}
        self.impala_code = []
        
    def parse_gazl_file(self, filename: str) -> str:
        """Parse GAZL file and return decompiled Impala code"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Parse in phases
        self.parse_constants_and_globals(lines)
        self.parse_functions(lines)
        self.generate_impala_code()
        
        return '\n'.join(self.impala_code)
    
    def parse_constants_and_globals(self, lines: List[str]):
        """Parse constants and global variables"""
        for line in lines:
            line = line.strip()
            if not line or line.startswith('.'):
                continue
                
            # Parse constants
            if ': ! DEF' in line:
                name, definition = line.split(': ! DEF', 1)
                if 'i #' in definition:
                    value = definition.split('#')[1].strip()
                    self.constants[name] = f"const int {name} = {value}"
                elif 'f #' in definition:
                    value = definition.split('#')[1].strip()
                    self.constants[name] = f"const float {name} = {value}"
            
            # Parse global arrays
            elif ': GLOB *' in line:
                name, size_def = line.split(': GLOB *', 1)
                size = size_def.strip()
                self.globals[name] = f"global array {name}[{size}]"
            
            # Parse global variables
            elif ': DATi #' in line:
                name, value_def = line.split(': DATi #', 1)
                value = value_def.strip()
                self.globals[name] = f"global int {name} = {value}"
    
    def parse_functions(self, lines: List[str]):
        """Parse function definitions"""
        current_func = None
        func_lines = []
        in_function = False
        
        for line in lines:
            line = line.strip()
            
            # Start of function
            if line.endswith(': FUNC'):
                if current_func:
                    self.process_function(current_func, func_lines)
                current_func = line[:-6]  # Remove ': FUNC'
                func_lines = []
                in_function = True
                continue
            
            # End of function
            elif line == 'RETU' and in_function:
                func_lines.append(line)
                self.process_function(current_func, func_lines)
                current_func = None
                func_lines = []
                in_function = False
                continue
            
            if in_function:
                func_lines.append(line)
    
    def process_function(self, func_name: str, lines: List[str]):
        """Process individual function"""
        params = []
        locals_vars = []
        body_lines = []
        
        # Parse function signature and locals
        for line in lines:
            if line.startswith('$') and ': INP' in line:
                param_name = line.split(':')[0][1:]  # Remove $
                param_type = 'int' if 'INPi' in line else 'pointer' if 'INPp' in line else 'float'
                params.append(f"{param_type} {param_name}")
            elif line.startswith('$') and ': LOC' in line:
                local_name = line.split(':')[0][1:]  # Remove $
                local_type = 'int' if 'LOCi' in line else 'pointer' if 'LOCp' in line else 'float'
                locals_vars.append(f"{local_type} {local_name}")
            elif line.startswith('$') and ': OUT' in line:
                # Output parameters - handle as return type
                continue
            else:
                body_lines.append(line)
        
        self.functions[func_name] = {
            'params': params,
            'locals': locals_vars,
            'body': body_lines
        }
    
    def convert_gazl_instruction_to_impala(self, line: str) -> str:
        """Convert single GAZL instruction to Impala"""
        line = line.strip()
        
        # Handle loops
        if line.startswith('.l') and line.endswith(':'):
            return "loop {"
        elif line == 'GOTO @.l0' or 'GOTO @.l' in line:
            return "// continue loop"
        elif line.startswith('.e') and line.endswith(':'):
            return "}"
        
        # Handle conditionals
        elif 'EQUi %0 #0 @.' in line:
            return "if (condition == 0) {"
        elif line.startswith('GEQi') or line.startswith('LEQi'):
            return "if (condition) {"
        
        # Handle assignments
        elif line.startswith('MOVi'):
            parts = line.split()
            if len(parts) >= 3:
                dest = parts[1].replace('$', '')
                src = parts[2].replace('#', '').replace('$', '')
                return f"{dest} = {src};"
        
        # Handle PEEK (global variable access)
        elif line.startswith('PEEK'):
            parts = line.split()
            if len(parts) >= 3:
                return f"// Read from {parts[2]}"
        
        # Handle POKE (global variable write)
        elif line.startswith('POKE'):
            parts = line.split()
            if len(parts) >= 3:
                return f"// Write to {parts[1]}"
        
        # Handle function calls
        elif line.startswith('CALL'):
            func_name = line.split()[1].replace('^', '').replace('&', '')
            return f"{func_name}();"
        
        # Handle yield
        elif line == 'CALL ^yield %0 *1':
            return "yield();"
        
        # Default - comment out unknown instructions
        return f"// {line}"
    
    def generate_impala_code(self):
        """Generate final Impala code"""
        self.impala_code = []
        
        # Add header
        self.impala_code.append("/*")
        self.impala_code.append(" * Decompiled from GAZL assembly")
        self.impala_code.append(" * Generated by gazl_to_impala_decompiler.py")
        self.impala_code.append(" */")
        self.impala_code.append("")
        
        # Add constants
        for name, definition in self.constants.items():
            self.impala_code.append(definition)
        self.impala_code.append("")
        
        # Add globals
        for name, definition in self.globals.items():
            self.impala_code.append(definition)
        self.impala_code.append("")
        
        # Add functions
        for func_name, func_data in self.functions.items():
            self.impala_code.append(f"function {func_name}()")
            
            # Add locals declaration
            if func_data['locals']:
                locals_str = "locals " + ", ".join(func_data['locals'])
                self.impala_code.append(locals_str)
            
            self.impala_code.append("{")
            
            # Convert function body
            for line in func_data['body']:
                converted = self.convert_gazl_instruction_to_impala(line)
                if converted.strip():
                    self.impala_code.append(f"    {converted}")
            
            self.impala_code.append("}")
            self.impala_code.append("")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 gazl_to_impala_decompiler.py <gazl_file>")
        sys.exit(1)
    
    gazl_file = sys.argv[1]
    output_file = gazl_file.replace('.gazl', '_decompiled.impala')
    
    decompiler = GazlDecompiler()
    impala_code = decompiler.parse_gazl_file(gazl_file)
    
    with open(output_file, 'w') as f:
        f.write(impala_code)
    
    print(f"Decompiled GAZL to: {output_file}")
    print(f"Found {len(decompiler.constants)} constants")
    print(f"Found {len(decompiler.globals)} globals") 
    print(f"Found {len(decompiler.functions)} functions")

if __name__ == "__main__":
    main()