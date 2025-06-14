# Custom Build Tools Reference

## Overview

The Permut8 firmware development ecosystem supports sophisticated build automation, custom tooling, and development workflows. This reference covers the complete toolchain for creating professional development environments, automating build processes, and implementing custom tools that enhance productivity and code quality.

From simple build scripts to complete CI/CD pipelines, this guide provides the foundation for scaling Permut8 development from individual projects to team-based professional workflows.

## Build System Architecture

### Core Build Components

The Permut8 build system consists of several interconnected components that transform Impala source code into executable firmware.

```bash
# Build system overview
Source Code (*.impala)
    ↓ Preprocessor
Preprocessed Code
    ↓ Impala Compiler
GAZL Assembly (*.gazl)
    ↓ GAZL Assembler
Machine Code
    ↓ Linker
Firmware Binary (*.bin)
    ↓ Upload Tool
Permut8 Device
```

### Build Configuration Files

**project.config** - Main project configuration:
```ini
# Permut8 Project Configuration
[project]
name = "MyEffect"
version = "1.2.0"
author = "Developer Name"
description = "Custom audio effect"
target = "permut8_v2"

[build]
source_dir = "src"
output_dir = "build"
optimization = "release"
debug_symbols = true
warnings_as_errors = false

[dependencies]
core_lib = "1.4.2"
dsp_lib = "2.1.0"
math_lib = "1.0.5"

[resources]
memory_size = 32768
stack_size = 2048
heap_size = 4096
```

**Makefile** - GNU Make build automation:
```makefile
# Permut8 Custom Build System
PROJECT_NAME := $(shell grep "name" project.config | cut -d'"' -f2)
VERSION := $(shell grep "version" project.config | cut -d'"' -f2)
TARGET := $(shell grep "target" project.config | cut -d'"' -f2)

# Directories
SRC_DIR := src
BUILD_DIR := build
TOOLS_DIR := tools
LIB_DIR := lib

# Compiler settings
IMPALA_CC := impala-compiler
GAZL_AS := gazl-assembler
LINKER := permut8-linker
UPLOADER := permut8-upload

# Compiler flags
CFLAGS := -O2 -Wall -Wextra
DEBUG_FLAGS := -g -DDEBUG
RELEASE_FLAGS := -DNDEBUG -fomit-frame-pointer

# Source files
SOURCES := $(wildcard $(SRC_DIR)/*.impala)
OBJECTS := $(SOURCES:$(SRC_DIR)/%.impala=$(BUILD_DIR)/%.o)
DEPENDENCIES := $(OBJECTS:.o=.d)

# Build targets
.PHONY: all clean debug release test upload backup

all: release

# Release build
release: CFLAGS += $(RELEASE_FLAGS)
release: $(BUILD_DIR)/$(PROJECT_NAME).bin

# Debug build
debug: CFLAGS += $(DEBUG_FLAGS)
debug: $(BUILD_DIR)/$(PROJECT_NAME)_debug.bin

# Object file compilation
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.impala | $(BUILD_DIR)
	$(IMPALA_CC) $(CFLAGS) -MMD -MP -c $< -o $@

# Linking
$(BUILD_DIR)/$(PROJECT_NAME).bin: $(OBJECTS)
	$(LINKER) $(OBJECTS) -o $@ -L$(LIB_DIR) -lpermut8core

# Directory creation
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Cleanup
clean:
	rm -rf $(BUILD_DIR)

# Upload to device
upload: $(BUILD_DIR)/$(PROJECT_NAME).bin
	$(UPLOADER) --device $(TARGET) --firmware $<

# Include dependencies
-include $(DEPENDENCIES)
```

## Advanced Build Automation

### CMake Integration

**CMakeLists.txt** - Modern build system configuration:
```cmake
cmake_minimum_required(VERSION 3.16)
project(Permut8Firmware VERSION 1.0.0 LANGUAGES C)

# Project configuration
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Build types
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler-specific options
if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    add_compile_options(-Wall -Wextra -Wpedantic)
    add_compile_options($<$<CONFIG:Debug>:-g -O0 -DDEBUG>)
    add_compile_options($<$<CONFIG:Release>:-O3 -DNDEBUG -flto>)
endif()

# Find Permut8 SDK
find_package(Permut8SDK REQUIRED)

# Source files
file(GLOB_RECURSE SOURCES "src/*.impala" "src/*.c")
file(GLOB_RECURSE HEADERS "src/*.h" "include/*.h")

# Main firmware target
add_executable(firmware ${SOURCES})
target_include_directories(firmware PRIVATE 
    src 
    include 
    ${Permut8SDK_INCLUDE_DIRS}
)
target_link_libraries(firmware ${Permut8SDK_LIBRARIES})

# Custom build rules for Impala compilation
foreach(IMPALA_SOURCE ${IMPALA_SOURCES})
    get_filename_component(BASENAME ${IMPALA_SOURCE} NAME_WE)
    set(GAZL_OUTPUT ${CMAKE_BINARY_DIR}/${BASENAME}.gazl)
    
    add_custom_command(
        OUTPUT ${GAZL_OUTPUT}
        COMMAND impala-compiler ${IMPALA_SOURCE} -o ${GAZL_OUTPUT}
        DEPENDS ${IMPALA_SOURCE}
        COMMENT "Compiling Impala: ${IMPALA_SOURCE}"
    )
    
    list(APPEND GAZL_OUTPUTS ${GAZL_OUTPUT})
endforeach()

# Firmware binary generation
add_custom_target(firmware_binary ALL
    DEPENDS firmware ${GAZL_OUTPUTS}
    COMMAND permut8-linker $<TARGET_FILE:firmware> ${GAZL_OUTPUTS} 
            -o ${CMAKE_BINARY_DIR}/firmware.bin
    COMMENT "Generating firmware binary"
)

# Upload target
add_custom_target(upload
    DEPENDS firmware_binary
    COMMAND permut8-upload --firmware ${CMAKE_BINARY_DIR}/firmware.bin
    COMMENT "Uploading firmware to device"
)

# Testing
enable_testing()
add_subdirectory(tests)
```

### Build Script Automation

**build.py** - Python build automation:
```python
#!/usr/bin/env python3
"""
Permut8 Firmware Build System
Advanced build automation with dependency management and optimization
"""

import os
import sys
import json
import argparse
import subprocess
import configparser
from pathlib import Path
from datetime import datetime

class Permut8Builder:
    def __init__(self, config_file="project.config"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.project_name = self.config.get('project', 'name', fallback='firmware')
        self.version = self.config.get('project', 'version', fallback='1.0.0')
        self.build_dir = Path(self.config.get('build', 'output_dir', fallback='build'))
        self.src_dir = Path(self.config.get('build', 'source_dir', fallback='src'))
        
    def create_build_environment(self):
        """Set up build directory structure"""
        dirs = [
            self.build_dir,
            self.build_dir / 'objects',
            self.build_dir / 'dependencies',
            self.build_dir / 'generated',
            self.build_dir / 'logs'
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"✓ Build environment created in {self.build_dir}")
    
    def check_dependencies(self):
        """Verify all build dependencies are available"""
        required_tools = [
            'impala-compiler',
            'gazl-assembler', 
            'permut8-linker',
            'permut8-upload'
        ]
        
        missing_tools = []
        for tool in required_tools:
            if not self.command_exists(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"✗ Missing tools: {', '.join(missing_tools)}")
            return False
        
        print("✓ All build dependencies available")
        return True
    
    def command_exists(self, command):
        """Check if command exists in PATH"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def compile_impala_sources(self, optimization_level='release'):
        """Compile all Impala source files to GAZL assembly"""
        impala_files = list(self.src_dir.glob('**/*.impala'))
        
        if not impala_files:
            print("✗ No Impala source files found")
            return False
        
        optimization_flags = {
            'debug': ['-g', '-O0', '-DDEBUG'],
            'release': ['-O3', '-DNDEBUG', '-fomit-frame-pointer'],
            'size': ['-Os', '-DNDEBUG', '-ffunction-sections'],
            'speed': ['-Ofast', '-DNDEBUG', '-funroll-loops']
        }
        
        flags = optimization_flags.get(optimization_level, optimization_flags['release'])
        
        compiled_objects = []
        for impala_file in impala_files:
            object_file = self.build_dir / 'objects' / f"{impala_file.stem}.o"
            gazl_file = self.build_dir / 'generated' / f"{impala_file.stem}.gazl"
            
            # Compile Impala to GAZL
            impala_cmd = [
                'impala-compiler',
                str(impala_file),
                '-o', str(gazl_file)
            ] + flags
            
            print(f"Compiling {impala_file.name}...")
            result = subprocess.run(impala_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"✗ Compilation failed: {impala_file}")
                print(result.stderr)
                return False
            
            # Assemble GAZL to object code
            gazl_cmd = [
                'gazl-assembler',
                str(gazl_file),
                '-o', str(object_file)
            ]
            
            result = subprocess.run(gazl_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"✗ Assembly failed: {gazl_file}")
                print(result.stderr)
                return False
            
            compiled_objects.append(object_file)
        
        print(f"✓ Compiled {len(compiled_objects)} source files")
        return compiled_objects
    
    def link_firmware(self, object_files, output_name=None):
        """Link object files into final firmware binary"""
        if not output_name:
            output_name = f"{self.project_name}.bin"
        
        output_path = self.build_dir / output_name
        
        link_cmd = [
            'permut8-linker',
            '--output', str(output_path),
            '--map-file', str(self.build_dir / f"{self.project_name}.map"),
            '--memory-layout', 'permut8_v2'
        ] + [str(obj) for obj in object_files]
        
        print("Linking firmware binary...")
        result = subprocess.run(link_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Linking failed")
            print(result.stderr)
            return None
        
        # Generate build info
        build_info = {
            'project': self.project_name,
            'version': self.version,
            'build_time': datetime.now().isoformat(),
            'optimization': 'release',
            'size_bytes': output_path.stat().st_size,
            'object_files': [str(obj) for obj in object_files]
        }
        
        with open(self.build_dir / 'build_info.json', 'w') as f:
            json.dump(build_info, f, indent=2)
        
        print(f"✓ Firmware binary created: {output_path}")
        print(f"  Size: {output_path.stat().st_size} bytes")
        return output_path
    
    def run_tests(self):
        """Execute firmware test suite"""
        test_dir = Path('tests')
        if not test_dir.exists():
            print("No tests directory found, skipping tests")
            return True
        
        test_files = list(test_dir.glob('test_*.impala'))
        if not test_files:
            print("No test files found, skipping tests")
            return True
        
        print(f"Running {len(test_files)} test files...")
        
        for test_file in test_files:
            print(f"  Testing {test_file.name}...")
            
            # Compile and run test
            test_cmd = [
                'impala-test-runner',
                str(test_file),
                '--firmware', str(self.build_dir / f"{self.project_name}.bin")
            ]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"✗ Test failed: {test_file.name}")
                print(result.stdout)
                return False
        
        print("✓ All tests passed")
        return True
    
    def upload_firmware(self, firmware_path, device_target=None):
        """Upload firmware to Permut8 device"""
        if not device_target:
            device_target = self.config.get('project', 'target', fallback='permut8_v2')
        
        upload_cmd = [
            'permut8-upload',
            '--device', device_target,
            '--firmware', str(firmware_path),
            '--verify'
        ]
        
        print(f"Uploading firmware to {device_target}...")
        result = subprocess.run(upload_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Upload failed")
            print(result.stderr)
            return False
        
        print("✓ Firmware uploaded successfully")
        return True
    
    def build_all(self, optimization='release', run_tests=True, upload=False):
        """Complete build pipeline"""
        print(f"Starting build: {self.project_name} v{self.version}")
        
        # Setup
        self.create_build_environment()
        if not self.check_dependencies():
            return False
        
        # Compile
        object_files = self.compile_impala_sources(optimization)
        if not object_files:
            return False
        
        # Link
        firmware_path = self.link_firmware(object_files)
        if not firmware_path:
            return False
        
        # Test
        if run_tests and not self.run_tests():
            return False
        
        # Upload
        if upload and not self.upload_firmware(firmware_path):
            return False
        
        print(f"✓ Build complete: {firmware_path}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Permut8 Firmware Build System')
    parser.add_argument('--config', default='project.config', 
                       help='Project configuration file')
    parser.add_argument('--optimization', choices=['debug', 'release', 'size', 'speed'],
                       default='release', help='Optimization level')
    parser.add_argument('--no-tests', action='store_true', 
                       help='Skip running tests')
    parser.add_argument('--upload', action='store_true',
                       help='Upload firmware after build')
    parser.add_argument('--clean', action='store_true',
                       help='Clean build directory before building')
    
    args = parser.parse_args()
    
    builder = Permut8Builder(args.config)
    
    if args.clean:
        import shutil
        if builder.build_dir.exists():
            shutil.rmtree(builder.build_dir)
            print(f"✓ Cleaned {builder.build_dir}")
    
    success = builder.build_all(
        optimization=args.optimization,
        run_tests=not args.no_tests,
        upload=args.upload
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

## Code Generation Tools

### Template-Based Code Generation

**template_generator.py** - Automated code generation from templates:
```python
#!/usr/bin/env python3
"""
Permut8 Code Template Generator
Generates boilerplate code from templates with parameter substitution
"""

import os
import re
import json
import argparse
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

class CodeGenerator:
    def __init__(self, template_dir="templates"):
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
    def generate_effect_template(self, effect_name, effect_type, parameters):
        """Generate a complete effect from template"""
        template_file = f"{effect_type}_template.impala"
        
        if not (self.template_dir / template_file).exists():
            available = list(self.template_dir.glob("*_template.impala"))
            print(f"Template {template_file} not found")
            print(f"Available templates: {[t.name for t in available]}")
            return None
        
        template = self.env.get_template(template_file)
        
        # Generate parameter structure
        param_declarations = []
        param_reads = []
        param_descriptions = []
        
        for i, param in enumerate(parameters):
            param_declarations.append(f"static float {param['name']} = 0.0;")
            
            scaling = param.get('scaling', 'linear')
            min_val = param.get('min', 0.0)
            max_val = param.get('max', 1.0)
            
            if scaling == 'linear':
                param_reads.append(
                    f"{param['name']} = params[{i}] * {max_val - min_val} + {min_val};"
                )
            elif scaling == 'exponential':
                param_reads.append(
                    f"{param['name']} = {min_val} * pow({max_val/min_val}, params[{i}]);"
                )
            elif scaling == 'logarithmic':
                param_reads.append(
                    f"{param['name']} = {min_val} + ({max_val - min_val}) * "
                    f"log(1.0 + params[{i}] * 9.0) / log(10.0);"
                )
            
            param_descriptions.append(f"// Parameter {i}: {param['description']}")
        
        # Template variables
        template_vars = {
            'effect_name': effect_name,
            'effect_name_upper': effect_name.upper(),
            'effect_description': f"Custom {effect_type} effect: {effect_name}",
            'param_count': len(parameters),
            'param_declarations': '\n    '.join(param_declarations),
            'param_reads': '\n        '.join(param_reads),
            'param_descriptions': '\n    '.join(param_descriptions),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        generated_code = template.render(**template_vars)
        return generated_code
    
    def create_project_structure(self, project_name, project_type='effect'):
        """Generate complete project directory structure"""
        project_dir = Path(project_name)
        
        # Directory structure
        directories = [
            project_dir / 'src',
            project_dir / 'include',
            project_dir / 'tests',
            project_dir / 'docs',
            project_dir / 'tools',
            project_dir / 'build'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Generate main source file
        main_template = self.env.get_template('main_template.impala')
        main_code = main_template.render(
            project_name=project_name,
            project_type=project_type
        )
        
        with open(project_dir / 'src' / 'main.impala', 'w') as f:
            f.write(main_code)
        
        # Generate configuration files
        config_template = self.env.get_template('project_config_template.ini')
        config_content = config_template.render(
            project_name=project_name,
            project_type=project_type
        )
        
        with open(project_dir / 'project.config', 'w') as f:
            f.write(config_content)
        
        # Generate Makefile
        makefile_template = self.env.get_template('Makefile_template')
        makefile_content = makefile_template.render(project_name=project_name)
        
        with open(project_dir / 'Makefile', 'w') as f:
            f.write(makefile_content)
        
        # Generate README
        readme_template = self.env.get_template('README_template.md')
        readme_content = readme_template.render(
            project_name=project_name,
            project_type=project_type
        )
        
        with open(project_dir / 'README.md', 'w') as f:
            f.write(readme_content)
        
        print(f"✓ Project structure created: {project_dir}")
        return project_dir

# DSP Algorithm Generator
class DSPGenerator:
    """Generate optimized DSP algorithms from mathematical descriptions"""
    
    def __init__(self):
        self.optimization_passes = [
            self.constant_folding,
            self.common_subexpression_elimination,
            self.strength_reduction,
            self.loop_unrolling
        ]
    
    def generate_biquad_filter(self, filter_type, sample_rate=44100):
        """Generate optimized biquad filter implementation"""
        
        filter_templates = {
            'lowpass': {
                'description': 'Second-order Butterworth lowpass filter',
                'coefficients': '''
                float w = 2.0 * PI * cutoff / sample_rate;
                float cosw = cos(w);
                float sinw = sin(w);
                float alpha = sinw / (2.0 * Q);
                
                float b0 = (1.0 - cosw) / 2.0;
                float b1 = 1.0 - cosw;
                float b2 = (1.0 - cosw) / 2.0;
                float a0 = 1.0 + alpha;
                float a1 = -2.0 * cosw;
                float a2 = 1.0 - alpha;
                ''',
                'normalization': '''
                b0 /= a0; b1 /= a0; b2 /= a0;
                a1 /= a0; a2 /= a0;
                '''
            },
            'highpass': {
                'description': 'Second-order Butterworth highpass filter',
                'coefficients': '''
                float w = 2.0 * PI * cutoff / sample_rate;
                float cosw = cos(w);
                float sinw = sin(w);
                float alpha = sinw / (2.0 * Q);
                
                float b0 = (1.0 + cosw) / 2.0;
                float b1 = -(1.0 + cosw);
                float b2 = (1.0 + cosw) / 2.0;
                float a0 = 1.0 + alpha;
                float a1 = -2.0 * cosw;
                float a2 = 1.0 - alpha;
                ''',
                'normalization': '''
                b0 /= a0; b1 /= a0; b2 /= a0;
                a1 /= a0; a2 /= a0;
                '''
            },
            'bandpass': {
                'description': 'Second-order bandpass filter',
                'coefficients': '''
                float w = 2.0 * PI * cutoff / sample_rate;
                float cosw = cos(w);
                float sinw = sin(w);
                float alpha = sinw / (2.0 * Q);
                
                float b0 = alpha;
                float b1 = 0.0;
                float b2 = -alpha;
                float a0 = 1.0 + alpha;
                float a1 = -2.0 * cosw;
                float a2 = 1.0 - alpha;
                ''',
                'normalization': '''
                b0 /= a0; b1 /= a0; b2 /= a0;
                a1 /= a0; a2 /= a0;
                '''
            }
        }
        
        template = filter_templates.get(filter_type)
        if not template:
            return None
        
        code = f'''
// {template['description']}
// Auto-generated optimized implementation

typedef struct {{
    float x1, x2;  // Input delay line
    float y1, y2;  // Output delay line
    float b0, b1, b2;  // Feedforward coefficients
    float a1, a2;      // Feedback coefficients
}} BiquadFilter;

static BiquadFilter filter = {{0}};

void update_filter_coefficients(float cutoff, float Q) {{
    // Coefficient calculation
    {template['coefficients']}
    
    // Normalize coefficients
    {template['normalization']}
    
    // Store in filter structure
    filter.b0 = b0; filter.b1 = b1; filter.b2 = b2;
    filter.a1 = a1; filter.a2 = a2;
}}

float process_biquad(float input) {{
    // Direct Form II implementation (optimized)
    float w = input - filter.a1 * filter.y1 - filter.a2 * filter.y2;
    float output = filter.b0 * w + filter.b1 * filter.y1 + filter.b2 * filter.y2;
    
    // Update delay line
    filter.y2 = filter.y1;
    filter.y1 = output;
    
    return output;
}}
'''
        return code
    
    def generate_oscillator(self, osc_type, optimization='speed'):
        """Generate optimized oscillator implementations"""
        
        oscillators = {
            'sine': {
                'wavetable': self.generate_sine_wavetable(1024),
                'description': 'Wavetable sine oscillator with linear interpolation'
            },
            'sawtooth': {
                'algorithm': 'bandlimited_sawtooth',
                'description': 'Band-limited sawtooth oscillator using BLEP'
            },
            'square': {
                'algorithm': 'bandlimited_square', 
                'description': 'Band-limited square wave using BLIP'
            }
        }
        
        if osc_type == 'sine':
            return self.generate_wavetable_oscillator(oscillators['sine'])
        else:
            return self.generate_bandlimited_oscillator(osc_type, oscillators[osc_type])
    
    def constant_folding(self, code):
        """Optimize constant expressions at compile time"""
        # Replace mathematical constants
        constants = {
            '2.0 * PI': '6.28318530718',
            'PI / 2.0': '1.57079632679',
            'sqrt(2.0)': '1.41421356237',
            'log(2.0)': '0.69314718056'
        }
        
        for expr, value in constants.items():
            code = code.replace(expr, value)
        
        return code
    
    def strength_reduction(self, code):
        """Replace expensive operations with cheaper equivalents"""
        optimizations = [
            (r'(\w+) \* 2\.0', r'\1 + \1'),  # Multiplication by 2 -> addition
            (r'(\w+) / 2\.0', r'\1 * 0.5'),  # Division by 2 -> multiplication
            (r'pow\((\w+), 2\.0\)', r'\1 * \1'),  # Power of 2 -> multiplication
            (r'pow\(2\.0, (\w+)\)', r'exp2(\1)'),  # 2^x -> exp2
        ]
        
        for pattern, replacement in optimizations:
            code = re.sub(pattern, replacement, code)
        
        return code
```

## Testing and Validation Tools

### Automated Test Framework

**test_framework.py** - Comprehensive testing infrastructure:
```python
#!/usr/bin/env python3
"""
Permut8 Firmware Test Framework
Automated testing for audio processing algorithms and firmware behavior
"""

import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
from pathlib import Path
import json
import subprocess

class AudioTestFramework:
    def __init__(self, sample_rate=44100, buffer_size=128):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.test_results = []
        
    def generate_test_signals(self):
        """Generate standard test signals for audio processing validation"""
        duration = 1.0  # 1 second test signals
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, endpoint=False)
        
        test_signals = {
            'sine_1khz': np.sin(2 * np.pi * 1000 * t),
            'sine_440hz': np.sin(2 * np.pi * 440 * t),
            'white_noise': np.random.normal(0, 0.1, samples),
            'pink_noise': self.generate_pink_noise(samples),
            'impulse': self.generate_impulse(samples),
            'chirp': scipy.signal.chirp(t, 20, duration, 20000),
            'square_1khz': scipy.signal.square(2 * np.pi * 1000 * t),
            'sawtooth_1khz': scipy.signal.sawtooth(2 * np.pi * 1000 * t)
        }
        
        return test_signals
    
    def generate_pink_noise(self, samples):
        """Generate pink noise (1/f noise) for testing"""
        white = np.random.normal(0, 1, samples)
        
        # Pink noise filter (approximate)
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        
        pink = scipy.signal.lfilter(b, a, white)
        return pink / np.max(np.abs(pink)) * 0.1
    
    def generate_impulse(self, samples):
        """Generate impulse signal for impulse response testing"""
        impulse = np.zeros(samples)
        impulse[100] = 1.0  # Impulse at sample 100
        return impulse
    
    def test_frequency_response(self, firmware_path, test_name):
        """Test frequency response of firmware using swept sine"""
        print(f"Testing frequency response: {test_name}")
        
        # Generate logarithmic sweep
        duration = 2.0
        f_start, f_end = 20, 20000
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        sweep = scipy.signal.chirp(t, f_start, duration, f_end, method='logarithmic')
        
        # Process through firmware
        output = self.process_audio_through_firmware(firmware_path, sweep)
        
        # Calculate frequency response
        freqs, response = self.calculate_frequency_response(sweep, output)
        
        # Analyze results
        analysis = {
            'test_name': test_name,
            'type': 'frequency_response',
            'frequencies': freqs.tolist(),
            'magnitude_db': 20 * np.log10(np.abs(response)).tolist(),
            'phase_deg': np.angle(response, deg=True).tolist(),
            'sample_rate': self.sample_rate
        }
        
        # Generate plots
        self.plot_frequency_response(freqs, response, test_name)
        
        self.test_results.append(analysis)
        return analysis
    
    def test_thd_noise(self, firmware_path, test_frequency=1000):
        """Test Total Harmonic Distortion + Noise"""
        print(f"Testing THD+N at {test_frequency}Hz")
        
        # Generate pure sine wave
        duration = 1.0
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        sine_wave = 0.5 * np.sin(2 * np.pi * test_frequency * t)
        
        # Process through firmware
        output = self.process_audio_through_firmware(firmware_path, sine_wave)
        
        # Calculate THD+N
        thd_n_percent, harmonic_levels = self.calculate_thd_n(output, test_frequency)
        
        analysis = {
            'test_name': f'THD+N_{test_frequency}Hz',
            'type': 'distortion',
            'test_frequency': test_frequency,
            'thd_n_percent': thd_n_percent,
            'harmonic_levels_db': harmonic_levels,
            'sample_rate': self.sample_rate
        }
        
        self.test_results.append(analysis)
        return analysis
    
    def test_dynamic_range(self, firmware_path):
        """Test dynamic range and noise floor"""
        print("Testing dynamic range")
        
        # Test with silence (measure noise floor)
        silence = np.zeros(int(self.sample_rate))
        noise_output = self.process_audio_through_firmware(firmware_path, silence)
        noise_floor_db = 20 * np.log10(np.sqrt(np.mean(noise_output**2)) + 1e-12)
        
        # Test with full-scale sine wave
        full_scale_sine = 0.99 * np.sin(2 * np.pi * 1000 * np.linspace(0, 1, int(self.sample_rate)))
        full_scale_output = self.process_audio_through_firmware(firmware_path, full_scale_sine)
        signal_level_db = 20 * np.log10(np.sqrt(np.mean(full_scale_output**2)))
        
        dynamic_range = signal_level_db - noise_floor_db
        
        analysis = {
            'test_name': 'dynamic_range',
            'type': 'dynamic',
            'noise_floor_db': noise_floor_db,
            'signal_level_db': signal_level_db,
            'dynamic_range_db': dynamic_range,
            'sample_rate': self.sample_rate
        }
        
        self.test_results.append(analysis)
        return analysis
    
    def process_audio_through_firmware(self, firmware_path, input_audio):
        """Process audio through firmware using test harness"""
        # Save input audio to temporary file
        temp_input = Path('temp_input.wav')
        temp_output = Path('temp_output.wav')
        
        # Convert to 16-bit format expected by firmware
        input_scaled = np.clip(input_audio * 32767, -32768, 32767).astype(np.int16)
        
        # Write test file (simplified - would use proper audio library)
        with open(temp_input, 'wb') as f:
            # Write simple raw audio format for testing
            f.write(input_scaled.tobytes())
        
        # Run firmware test harness
        test_cmd = [
            'permut8-test-harness',
            '--firmware', str(firmware_path),
            '--input', str(temp_input),
            '--output', str(temp_output),
            '--sample-rate', str(self.sample_rate),
            '--buffer-size', str(self.buffer_size)
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Firmware test failed: {result.stderr}")
        
        # Read output audio
        with open(temp_output, 'rb') as f:
            output_data = f.read()
        
        output_audio = np.frombuffer(output_data, dtype=np.int16).astype(np.float32) / 32767.0
        
        # Cleanup
        temp_input.unlink(missing_ok=True)
        temp_output.unlink(missing_ok=True)
        
        return output_audio
    
    def calculate_frequency_response(self, input_signal, output_signal):
        """Calculate frequency response from input/output signals"""
        # Use scipy's signal processing for accurate analysis
        freqs, input_fft = scipy.signal.welch(input_signal, self.sample_rate, nperseg=2048)
        _, output_fft = scipy.signal.welch(output_signal, self.sample_rate, nperseg=2048)
        
        # Calculate transfer function
        response = output_fft / (input_fft + 1e-12)  # Avoid division by zero
        
        return freqs, response
    
    def calculate_thd_n(self, signal, fundamental_freq):
        """Calculate Total Harmonic Distortion + Noise"""
        # FFT analysis
        window = np.hanning(len(signal))
        fft = np.fft.rfft(signal * window)
        freqs = np.fft.rfftfreq(len(signal), 1/self.sample_rate)
        
        # Find fundamental frequency bin
        fund_bin = np.argmin(np.abs(freqs - fundamental_freq))
        fund_magnitude = np.abs(fft[fund_bin])
        
        # Find harmonic frequencies (up to Nyquist)
        harmonics = []
        harmonic_levels = []
        
        for h in range(2, 11):  # 2nd through 10th harmonics
            harmonic_freq = fundamental_freq * h
            if harmonic_freq < self.sample_rate / 2:
                harm_bin = np.argmin(np.abs(freqs - harmonic_freq))
                harm_magnitude = np.abs(fft[harm_bin])
                harmonics.append(harm_magnitude)
                harmonic_levels.append(20 * np.log10(harm_magnitude / fund_magnitude))
        
        # Calculate THD+N
        harmonic_power = sum(h**2 for h in harmonics)
        
        # Estimate noise power (excluding fundamental and harmonics)
        noise_bins = list(range(len(fft)))
        
        # Remove fundamental and harmonic bins
        exclude_bins = [fund_bin]
        for h in range(2, 11):
            harmonic_freq = fundamental_freq * h
            if harmonic_freq < self.sample_rate / 2:
                harm_bin = np.argmin(np.abs(freqs - harmonic_freq))
                exclude_bins.extend(range(max(0, harm_bin-2), min(len(fft), harm_bin+3)))
        
        noise_bins = [b for b in noise_bins if b not in exclude_bins]
        noise_power = sum(np.abs(fft[b])**2 for b in noise_bins)
        
        thd_n = np.sqrt(harmonic_power + noise_power) / fund_magnitude
        thd_n_percent = thd_n * 100
        
        return thd_n_percent, harmonic_levels
    
    def plot_frequency_response(self, freqs, response, test_name):
        """Generate frequency response plots"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Magnitude plot
        magnitude_db = 20 * np.log10(np.abs(response))
        ax1.semilogx(freqs, magnitude_db)
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Magnitude (dB)')
        ax1.set_title(f'{test_name} - Frequency Response')
        ax1.grid(True)
        ax1.set_xlim(20, 20000)
        
        # Phase plot
        phase_deg = np.angle(response, deg=True)
        ax2.semilogx(freqs, phase_deg)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.grid(True)
        ax2.set_xlim(20, 20000)
        
        plt.tight_layout()
        plt.savefig(f'{test_name}_frequency_response.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_test_report(self, output_file='test_report.json'):
        """Generate comprehensive test report"""
        report = {
            'test_framework_version': '1.0.0',
            'test_date': datetime.now().isoformat(),
            'test_configuration': {
                'sample_rate': self.sample_rate,
                'buffer_size': self.buffer_size
            },
            'test_results': self.test_results,
            'summary': self.generate_test_summary()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Test report generated: {output_file}")
        return report
    
    def generate_test_summary(self):
        """Generate test summary statistics"""
        summary = {
            'total_tests': len(self.test_results),
            'test_types': list(set(r['type'] for r in self.test_results)),
            'passed_tests': 0,
            'failed_tests': 0,
            'warnings': []
        }
        
        for result in self.test_results:
            # Apply pass/fail criteria based on test type
            if result['type'] == 'distortion':
                if result['thd_n_percent'] < 1.0:  # Less than 1% THD+N
                    summary['passed_tests'] += 1
                else:
                    summary['failed_tests'] += 1
                    summary['warnings'].append(f"High THD+N: {result['thd_n_percent']:.2f}%")
            
            elif result['type'] == 'dynamic':
                if result['dynamic_range_db'] > 60:  # More than 60dB dynamic range
                    summary['passed_tests'] += 1
                else:
                    summary['failed_tests'] += 1
                    summary['warnings'].append(f"Low dynamic range: {result['dynamic_range_db']:.1f}dB")
            
            else:
                summary['passed_tests'] += 1  # Default pass for analysis tests
        
        return summary
```

## Deployment and Distribution

### Automated Deployment Pipeline

**deploy.sh** - Production deployment automation:
```bash
#!/bin/bash
# Permut8 Firmware Deployment Pipeline
# Automates building, testing, and distributing firmware releases

set -euo pipefail

# Configuration
PROJECT_NAME="permut8_firmware"
VERSION_FILE="version.txt"
BUILD_DIR="build"
DIST_DIR="dist"
UPLOAD_SERVER="firmware.permut8.com"
BACKUP_SERVER="backup.permut8.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    required_tools=("git" "python3" "make" "scp" "sha256sum")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check for clean git working directory
    if [[ -n $(git status --porcelain) ]]; then
        log_warn "Working directory is not clean"
        git status --short
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "Prerequisites check passed"
}

# Version management
bump_version() {
    local bump_type=${1:-patch}
    
    if [[ ! -f "$VERSION_FILE" ]]; then
        echo "1.0.0" > "$VERSION_FILE"
    fi
    
    local current_version=$(cat "$VERSION_FILE")
    local new_version
    
    case $bump_type in
        major)
            new_version=$(echo "$current_version" | awk -F. '{print ($1+1)".0.0"}')
            ;;
        minor)
            new_version=$(echo "$current_version" | awk -F. '{print $1".".($2+1)".0"}')
            ;;
        patch)
            new_version=$(echo "$current_version" | awk -F. '{print $1"."$2".".($3+1)}')
            ;;
        *)
            log_error "Invalid bump type: $bump_type (use major, minor, or patch)"
            exit 1
            ;;
    esac
    
    echo "$new_version" > "$VERSION_FILE"
    log_info "Version bumped from $current_version to $new_version"
    
    # Create git tag
    git add "$VERSION_FILE"
    git commit -m "Bump version to $new_version"
    git tag -a "v$new_version" -m "Release version $new_version"
    
    echo "$new_version"
}

# Build all configurations
build_all_configurations() {
    log_info "Building all firmware configurations..."
    
    configurations=("debug" "release" "size" "speed")
    
    for config in "${configurations[@]}"; do
        log_info "Building $config configuration..."
        
        python3 build.py --optimization "$config" --no-tests --clean
        
        if [[ $? -ne 0 ]]; then
            log_error "Build failed for $config configuration"
            exit 1
        fi
        
        # Copy to distribution directory
        mkdir -p "$DIST_DIR/$config"
        cp "$BUILD_DIR/${PROJECT_NAME}.bin" "$DIST_DIR/$config/"
        cp "$BUILD_DIR/build_info.json" "$DIST_DIR/$config/"
        
        # Generate checksum
        cd "$DIST_DIR/$config"
        sha256sum "${PROJECT_NAME}.bin" > "${PROJECT_NAME}.bin.sha256"
        cd - > /dev/null
    done
    
    log_info "All configurations built successfully"
}

# Run comprehensive test suite
run_test_suite() {
    log_info "Running comprehensive test suite..."
    
    # Unit tests
    log_info "Running unit tests..."
    python3 -m pytest tests/unit/ -v
    
    # Integration tests
    log_info "Running integration tests..."
    python3 -m pytest tests/integration/ -v
    
    # Audio processing tests
    log_info "Running audio processing tests..."
    python3 test_framework.py --firmware "$DIST_DIR/release/${PROJECT_NAME}.bin"
    
    # Performance benchmarks
    log_info "Running performance benchmarks..."
    python3 benchmark.py --firmware "$DIST_DIR/release/${PROJECT_NAME}.bin"
    
    log_info "All tests passed"
}

# Generate release documentation
generate_release_docs() {
    local version=$1
    
    log_info "Generating release documentation..."
    
    # Create release directory
    local release_dir="$DIST_DIR/release_$version"
    mkdir -p "$release_dir/docs"
    
    # Copy firmware binaries
    for config in debug release size speed; do
        cp -r "$DIST_DIR/$config" "$release_dir/"
    done
    
    # Generate release notes
    cat > "$release_dir/RELEASE_NOTES.md" << EOF
# Permut8 Firmware Release $version

## Release Information
- **Version**: $version
- **Release Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Git Commit**: $(git rev-parse HEAD)
- **Git Branch**: $(git branch --show-current)

## Build Configurations

### Release (Recommended)
- Optimized for performance and stability
- Debug symbols removed
- All optimizations enabled
- **File**: release/${PROJECT_NAME}.bin

### Debug
- Debug symbols included
- Optimizations disabled
- Enhanced error checking
- **File**: debug/${PROJECT_NAME}.bin

### Size
- Optimized for minimal code size
- Function sections enabled
- Ideal for memory-constrained applications
- **File**: size/${PROJECT_NAME}.bin

### Speed
- Maximum performance optimizations
- Loop unrolling enabled
- Fastest execution time
- **File**: speed/${PROJECT_NAME}.bin

## Installation

1. Connect your Permut8 device via USB
2. Run: \`permut8-upload --firmware release/${PROJECT_NAME}.bin\`
3. Verify installation with: \`permut8-upload --verify\`

## Verification

All firmware binaries include SHA256 checksums for integrity verification:

\`\`\`bash
# Verify firmware integrity
sha256sum -c release/${PROJECT_NAME}.bin.sha256
\`\`\`

## Changes Since Previous Release

$(git log --oneline --since="$(git tag --sort=-version:refname | sed -n '2p')" --until="$(git tag --sort=-version:refname | head -1)" || echo "First release")

## Technical Details

- **Target Device**: Permut8 v2
- **Compiler**: Impala $(impala-compiler --version | head -1)
- **Build System**: Custom Python + Make
- **Test Coverage**: $(python3 -m coverage report --show-missing 2>/dev/null | tail -1 || echo "Coverage not available")

## Support

For technical support and documentation:
- **Documentation**: docs/
- **Issues**: GitHub Issues
- **Community**: Permut8 Forum
EOF

    # Copy documentation
    cp -r docs/* "$release_dir/docs/" 2>/dev/null || true
    
    # Generate manifest
    find "$release_dir" -type f -exec sha256sum {} \; > "$release_dir/MANIFEST.sha256"
    
    log_info "Release documentation generated in $release_dir"
}

# Upload to distribution servers
upload_release() {
    local version=$1
    local release_dir="$DIST_DIR/release_$version"
    
    log_info "Uploading release to distribution servers..."
    
    # Create release archive
    tar -czf "${release_dir}.tar.gz" -C "$DIST_DIR" "release_$version"
    
    # Upload to primary server
    log_info "Uploading to primary server..."
    scp "${release_dir}.tar.gz" "deploy@${UPLOAD_SERVER}:/releases/"
    scp "${release_dir}.tar.gz.sha256" "deploy@${UPLOAD_SERVER}:/releases/"
    
    # Upload to backup server
    log_info "Uploading to backup server..."
    scp "${release_dir}.tar.gz" "deploy@${BACKUP_SERVER}:/releases/"
    
    # Update latest symlink on servers
    ssh "deploy@${UPLOAD_SERVER}" "cd /releases && ln -sf release_$version.tar.gz latest.tar.gz"
    
    log_info "Release uploaded successfully"
}

# Backup current release
backup_previous_release() {
    log_info "Backing up previous release..."
    
    # Create backup directory with timestamp
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Copy current distribution
    if [[ -d "$DIST_DIR" ]]; then
        cp -r "$DIST_DIR" "$backup_dir/"
        log_info "Previous release backed up to $backup_dir"
    fi
}

# Main deployment function
deploy() {
    local bump_type=${1:-patch}
    local skip_tests=${2:-false}
    
    log_info "Starting deployment pipeline..."
    
    # Prerequisites
    check_prerequisites
    
    # Backup
    backup_previous_release
    
    # Clean previous builds
    rm -rf "$BUILD_DIR" "$DIST_DIR"
    
    # Version management
    local new_version=$(bump_version "$bump_type")
    
    # Build
    build_all_configurations
    
    # Test
    if [[ "$skip_tests" != "true" ]]; then
        run_test_suite
    else
        log_warn "Skipping tests (not recommended for production)"
    fi
    
    # Documentation
    generate_release_docs "$new_version"
    
    # Upload
    upload_release "$new_version"
    
    # Push git changes
    git push origin main
    git push origin "v$new_version"
    
    log_info "Deployment completed successfully!"
    log_info "Released version: $new_version"
    log_info "Download: https://$UPLOAD_SERVER/releases/release_$new_version.tar.gz"
}

# Command line interface
case "${1:-}" in
    deploy)
        deploy "${2:-patch}" "${3:-false}"
        ;;
    bump)
        bump_version "${2:-patch}"
        ;;
    build)
        build_all_configurations
        ;;
    test)
        run_test_suite
        ;;
    docs)
        generate_release_docs "$(cat $VERSION_FILE)"
        ;;
    *)
        echo "Usage: $0 {deploy|bump|build|test|docs} [options]"
        echo ""
        echo "Commands:"
        echo "  deploy [major|minor|patch] [skip-tests]  - Full deployment pipeline"
        echo "  bump [major|minor|patch]                 - Bump version number"
        echo "  build                                    - Build all configurations"
        echo "  test                                     - Run test suite"
        echo "  docs                                     - Generate documentation"
        echo ""
        echo "Examples:"
        echo "  $0 deploy minor          - Deploy with minor version bump"
        echo "  $0 deploy patch true     - Deploy with patch bump, skip tests"
        echo "  $0 bump major           - Bump major version only"
        exit 1
        ;;
esac
```

## Development Environment Tools

### IDE Integration and Developer Tools

**vscode_extension/** - Visual Studio Code extension for Permut8 development:

```json
// package.json - VSCode extension manifest
{
    "name": "permut8-dev",
    "displayName": "Permut8 Development Tools",
    "description": "Comprehensive development environment for Permut8 firmware",
    "version": "1.0.0",
    "engines": {
        "vscode": "^1.60.0"
    },
    "categories": ["Programming Languages", "Debuggers", "Other"],
    "main": "./out/extension.js",
    "contributes": {
        "languages": [
            {
                "id": "impala",
                "aliases": ["Impala", "impala"],
                "extensions": [".impala"],
                "configuration": "./language-configuration.json"
            }
        ],
        "grammars": [
            {
                "language": "impala",
                "scopeName": "source.impala",
                "path": "./syntaxes/impala.tmLanguage.json"
            }
        ],
        "commands": [
            {
                "command": "permut8.build",
                "title": "Build Firmware",
                "category": "Permut8"
            },
            {
                "command": "permut8.upload",
                "title": "Upload to Device",
                "category": "Permut8"
            },
            {
                "command": "permut8.test",
                "title": "Run Tests",
                "category": "Permut8"
            }
        ],
        "keybindings": [
            {
                "command": "permut8.build",
                "key": "ctrl+shift+b",
                "when": "resourceExtname == .impala"
            },
            {
                "command": "permut8.upload",
                "key": "ctrl+shift+u",
                "when": "resourceExtname == .impala"
            }
        ],
        "taskDefinitions": [
            {
                "type": "permut8",
                "required": ["task"],
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The Permut8 task to execute"
                    }
                }
            }
        ]
    }
}
```

## Best Practices and Guidelines

### Tool Development Standards

**Development Principles**:
- **Automation First**: Automate repetitive tasks to reduce human error
- **Testing Integration**: Build testing into every tool and workflow
- **Documentation**: Every tool includes comprehensive usage documentation
- **Error Handling**: Robust error handling with clear diagnostic messages
- **Performance**: Tools should complete quickly to maintain development flow
- **Compatibility**: Support multiple platforms and development environments

**Code Quality Standards**:
```python
# Tool quality checklist
class ToolQualityStandards:
    """Standards for all Permut8 development tools"""
    
    def __init__(self):
        self.requirements = {
            'error_handling': 'Comprehensive exception handling',
            'logging': 'Detailed logging with levels',
            'configuration': 'Flexible configuration options',
            'testing': 'Unit tests with >90% coverage',
            'documentation': 'API docs and usage examples',
            'performance': 'Completion time <30 seconds for normal tasks',
            'compatibility': 'Support Windows, macOS, Linux'
        }
    
    def validate_tool(self, tool_path):
        """Validate tool meets quality standards"""
        checks = [
            self.check_error_handling(tool_path),
            self.check_documentation(tool_path),
            self.check_test_coverage(tool_path),
            self.check_performance(tool_path),
            self.check_configuration(tool_path)
        ]
        
        return all(checks)
```

### Integration Patterns

**Tool Chain Integration**:
- **Build System**: All tools integrate with main build system
- **CI/CD Pipeline**: Tools support continuous integration workflows
- **IDE Support**: Integration with popular development environments
- **Version Control**: Git hooks and automation support
- **Monitoring**: Build and deployment monitoring capabilities

**Configuration Management**:
```ini
# .permut8rc - Global tool configuration
[tools]
default_optimization = release
auto_upload = false
test_on_build = true
backup_on_deploy = true

[paths]
sdk_path = /usr/local/permut8-sdk
tools_path = /usr/local/permut8-tools
projects_path = ~/permut8-projects

[upload]
default_device = permut8_v2
verify_after_upload = true
backup_firmware = true

[testing]
audio_test_enabled = true
performance_test_enabled = true
regression_test_enabled = true
```

---

This comprehensive custom build tools reference provides the foundation for professional Permut8 firmware development workflows. From simple build automation to complete CI/CD pipelines, these tools enable teams to develop, test, and deploy firmware with confidence and efficiency.
