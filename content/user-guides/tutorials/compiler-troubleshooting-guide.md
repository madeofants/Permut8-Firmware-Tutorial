# PikaCmd.exe Compiler Troubleshooting Guide

**Master the compilation process and resolve common issues systematically**

This comprehensive guide explains the technical architecture behind PikaCmd.exe compilation and provides systematic solutions to common compilation failures. Whether you're encountering your first compilation error or dealing with complex build environment issues, this guide will help you understand and resolve the problem.

## What You'll Learn

By the end of this guide, you'll understand:
- The three-layer technical architecture of PikaCmd.exe compilation
- How to systematically diagnose and resolve compilation failures
- Platform-specific compilation considerations
- Advanced compiler usage patterns
- Professional troubleshooting methodology

**Prerequisites**: Basic command line familiarity  
**Time Required**: 30-45 minutes  
**Difficulty**: Beginner to Intermediate

## Chapter 1: Understanding the Three-Layer Compilation Architecture

The initial command `PikaCmd.exe -compile ringmod_code.impala` failed due to a combination of three distinct technical issues, each of which was solved in turn:

1. **Shell Execution Policy**: PowerShell's security model requires explicit pathing for executables in the current directory. This was solved by prefixing the command with `.\`.
2. **Program Role (Interpreter vs. Compiler)**: The program PikaCmd.exe is not a standalone compiler but a language interpreter. It requires a script file as its first argument to know what logic to execute. This was solved by providing `impala.pika`.
3. **Script-Level Argument Parsing**: The `impala.pika` script has its own internal logic for handling command-line arguments, which needed to be satisfied in the correct order.

### Layer 1: PowerShell Command Precedence and Path Resolution

**The Error**:
```
The term 'PikaCmd.exe' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Technical Reason**: This is a direct consequence of PowerShell's command execution policy and its use of the PATH environment variable.

#### PATH Environment Variable Behavior
- **PATH Search**: When you type a command, the shell doesn't search every folder on your computer. It only searches the specific list of directories defined in the system's PATH variable.
- **Security Feature**: For security reasons, the current working directory (`.`) is not included in the PATH by default in PowerShell. This prevents you from accidentally running a malicious executable (e.g., a fake `ls.exe`) that might be present in a downloaded folder.

#### The Fix: Explicit Path Resolution
```bash
# Wrong - relies on PATH search
PikaCmd.exe -compile ringmod_code.impala

# Correct - explicit path resolution
.\PikaCmd.exe -compile ringmod_code.impala
```

**Why This Works**: The `.` is an alias for the current directory location. By prefixing the executable with `.\`, you are providing a direct, unambiguous path to the file, telling the shell "Don't search the PATH; execute the file named PikaCmd.exe found right here." This bypasses the standard PATH search and satisfies the security policy.

### Layer 2: Interpreter vs. Standalone Executable

**The Error** (after using the `.\` prefix):
```
!!!! Cannot open file for reading: 'compile'
```

**Technical Reason**: This error revealed the fundamental nature of PikaCmd.exe. It is not a monolithic compiler but a scripting language interpreter.

#### Understanding Executable Types

**Standalone Executable**: A standalone program (like a traditional C++ compiler) would have the "compile" logic built into its own machine code. It would parse `compile` as a command-line switch or flag.

**Interpreter**: An interpreter (like `python.exe`, `node.exe`, or `perl.exe`) is a generic program whose main purpose is to read, parse, and execute a script file that is provided to it as an argument.

#### The Error's Meaning
When you ran `.\PikaCmd.exe compile ...`, you were instructing the Pika interpreter to find, open, and execute a script file literally named `compile` in the current directory. Since no such file existed, the interpreter's file-handling routine failed with the "Cannot open file for reading" error.

#### The Fix: Providing the Script
```bash
# Wrong - interpreter looks for script named "compile"
.\PikaCmd.exe compile ringmod_code.impala

# Correct - provides the actual script to execute
.\PikaCmd.exe impala.pika compile ringmod_code.impala
```

**Why This Works**: The solution was to provide the interpreter with the script it was meant to run: `impala.pika`. This file contains the actual Pika-language source code that defines the compiler's logic.

### Layer 3: Script-Level Command-Line Argument Parsing

With the interpreter now running the correct script, the final step was to provide arguments in the format that the script itself expected.

**Correct Command**:
```bash
.\PikaCmd.exe impala.pika compile ringmod_code.impala ringmod_code.gazl
```

**Technical Reason**: The command-line shell tokenizes (splits) this input string by spaces. The PikaCmd.exe process receives an array of these tokens as its arguments (argv in C/C++ or accessible via a system library in Pika).

#### Argument Flow Analysis
1. **PikaCmd.exe** (the interpreter) consumes the first argument, `impala.pika`, as the script to execute.
2. It then makes the remaining tokens available to the running `impala.pika` script.
3. Inside the `impala.pika` script, the logic looks for these arguments:

```pika
if ($1 == 'compile') {

    source = load($2);

    if (exists(@$3)) {
        save($3, collected);
    }

}
```

- The script checks its first argument (`$1`) to see if it's the string 'compile'. This matches.
- It then uses its second argument (`$2`) as the input filename to load. This matches `ringmod_code.impala`.
- It uses its third argument (`$3`) as the output filename to save to. This matches `ringmod_code.gazl`.

The command succeeded because the arguments were provided in the precise sequence and format that the `impala.pika` script's internal parsing logic was written to handle.

## Chapter 2: Systematic Compilation Troubleshooting

### Troubleshooting Flowchart

```
1. Command not recognized?
   ↓
   Add .\ prefix: .\PikaCmd.exe

2. "Cannot open file for reading" error?
   ↓
   Add script file: .\PikaCmd.exe impala.pika

3. Script errors or unexpected behavior?
   ↓
   Check argument order: .\PikaCmd.exe impala.pika compile input.impala output.gazl

4. Still failing?
   ↓
   Check file permissions, syntax, and environment
```

### Common Error Patterns and Solutions

#### Error Pattern 1: Command Not Found
**Symptoms**:
```
'PikaCmd.exe' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Diagnosis**: Shell cannot locate the executable
**Solution**: Use explicit path resolution with `.\`

#### Error Pattern 2: File Reading Errors
**Symptoms**:
```
!!!! Cannot open file for reading: 'compile'
!!!! Cannot open file for reading: 'input.impala'
```

**Diagnosis**: 
- First case: Missing script file argument
- Second case: Missing or incorrect input file

**Solutions**:
```bash
# For missing script
.\PikaCmd.exe impala.pika compile input.impala output.gazl

# For missing input file
# Check file exists and path is correct
ls *.impala
```

#### Error Pattern 3: Argument Order Issues
**Symptoms**:
- Compilation appears to start but produces no output
- Unexpected behavior or wrong files being processed

**Diagnosis**: Arguments provided in wrong order
**Solution**: Follow exact pattern: `script action input output`

#### Error Pattern 4: Permission Errors
**Symptoms**:
```
Access denied
Permission denied
Cannot write to file
```

**Diagnosis**: File system permissions or read-only files
**Solutions**:
```bash
# Check file permissions
ls -la *.impala *.gazl

# Make files writable if needed
chmod 644 *.impala *.gazl

# Run as administrator if necessary (Windows)
```

## Chapter 3: Platform-Specific Considerations

### Windows (PowerShell/Command Prompt)
**Executable Resolution**:
```powershell
# PowerShell (requires .\ prefix)
.\PikaCmd.exe impala.pika compile input.impala output.gazl

# Command Prompt (no prefix needed if in PATH)
PikaCmd.exe impala.pika compile input.impala output.gazl
```

**Path Separators**: Use backslashes or forward slashes
```powershell
.\PikaCmd.exe impala.pika compile firmware\input.impala firmware\output.gazl
.\PikaCmd.exe impala.pika compile firmware/input.impala firmware/output.gazl
```

### macOS/Linux (Bash/Zsh)
**Executable Resolution**:
```bash
# Requires ./ prefix for local executables
./PikaCmd.exe impala.pika compile input.impala output.gazl

# Or add to PATH first
export PATH=$PATH:.
PikaCmd.exe impala.pika compile input.impala output.gazl
```

**Case Sensitivity**: File names are case-sensitive
```bash
# These are different files on Unix systems
input.impala
Input.impala
INPUT.IMPALA
```

## Chapter 4: Advanced Compiler Usage

### Complete Command Syntax
```bash
.\PikaCmd.exe <script> <action> [arguments...]

# Where:
# <script>     - Always "impala.pika" for compilation
# <action>     - "compile" for standard compilation
# [arguments]  - Input file, output file, and optional flags
```

### Advanced Compilation Options
```bash
# Basic compilation
.\PikaCmd.exe impala.pika compile input.impala output.gazl

# Compilation with verbose output
.\PikaCmd.exe impala.pika compile input.impala output.gazl -verbose

# Compilation with optimization
.\PikaCmd.exe impala.pika compile input.impala output.gazl -optimize

# Debug compilation
.\PikaCmd.exe impala.pika compile input.impala output.gazl -debug
```

### Batch Compilation
```bash
# Windows batch file example
@echo off
for %%f in (*.impala) do (
    echo Compiling %%f...
    .\PikaCmd.exe impala.pika compile "%%f" "%%~nf.gazl"
)
```

```bash
# Unix shell script example
#!/bin/bash
for file in *.impala; do
    echo "Compiling $file..."
    ./PikaCmd.exe impala.pika compile "$file" "${file%.impala}.gazl"
done
```

## Chapter 5: Environment Setup and Verification

### Verification Checklist
```bash
# 1. Check files exist
ls -la PikaCmd.exe impala.pika

# 2. Check permissions
# Windows: Right-click → Properties → Security
# Unix: ls -la PikaCmd.exe impala.pika

# 3. Test basic execution
.\PikaCmd.exe impala.pika

# 4. Test with sample file
.\PikaCmd.exe impala.pika compile ringmod_code.impala ringmod_code.gazl
```

### Development Environment Integration

#### VS Code Integration
```json

{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Compile Impala",
            "type": "shell",
            "command": ".\\PikaCmd.exe",
            "args": ["impala.pika", "compile", "${file}", "${fileDirname}\\${fileBasenameNoExtension}.gazl"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

#### Automated Build Watching
```bash
# Watch for changes and auto-compile (requires inotify-tools on Linux)
while inotifywait -e modify *.impala; do
    for file in *.impala; do
        .\PikaCmd.exe impala.pika compile "$file" "${file%.impala}.gazl"
    done
done
```

## Chapter 6: Professional Troubleshooting Methodology

### Step-by-Step Diagnosis Process

#### Step 1: Isolate the Problem Layer
1. **Test shell execution**: Can you run `.\PikaCmd.exe` at all?
2. **Test interpreter**: Does `.\PikaCmd.exe impala.pika` show help or error?
3. **Test script logic**: Does `.\PikaCmd.exe impala.pika compile` show specific errors?

#### Step 2: Gather Environment Information
```bash
# Check working directory
pwd

# List relevant files
ls -la *.exe *.pika *.impala

# Check environment variables
echo $PATH  # Unix
echo %PATH% # Windows

# Test with absolute paths
/full/path/to/PikaCmd.exe impala.pika compile input.impala output.gazl
```

#### Step 3: Minimal Reproduction
```bash
# Create minimal test case
echo 'function process() { yield() }' > test.impala
.\PikaCmd.exe impala.pika compile test.impala test.gazl

# If this works, the issue is in your specific .impala file
# If this fails, the issue is in your environment setup
```

#### Step 4: Systematic Resolution
1. **Fix environment issues first** (paths, permissions, file existence)
2. **Fix command syntax second** (argument order, script specification)
3. **Fix source code issues last** (syntax errors, logic problems)

### Documentation and Logging
```bash
# Create compilation log
.\PikaCmd.exe impala.pika compile input.impala output.gazl > compilation.log 2>&1

# Save successful configurations
echo "Working command: .\PikaCmd.exe impala.pika compile input.impala output.gazl" > notes.txt
```

## Chapter 7: Integration with Development Workflow

### Professional Build Scripts
```bash
#!/bin/bash
# build.sh - Professional Impala build script

set -e  # Exit on any error

PIKACMD="./PikaCmd.exe"
SCRIPT="impala.pika"
ACTION="compile"

# Check prerequisites
if [ ! -f "$PIKACMD" ]; then
    echo "Error: PikaCmd.exe not found"
    exit 1
fi

if [ ! -f "$SCRIPT" ]; then
    echo "Error: impala.pika not found"
    exit 1
fi

# Compile all .impala files
echo "Starting compilation..."
for file in *.impala; do
    if [ -f "$file" ]; then
        output="${file%.impala}.gazl"
        echo "Compiling: $file -> $output"
        
        if "$PIKACMD" "$SCRIPT" "$ACTION" "$file" "$output"; then
            echo "  ✓ Success"
        else
            echo "  ✗ Failed"
            exit 1
        fi
    fi
done

echo "All files compiled successfully!"
```

### Continuous Integration
```yaml
# .github/workflows/build.yml
name: Build Firmware
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Compile firmware
        run: |
          .\PikaCmd.exe impala.pika compile *.impala
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: compiled-firmware
          path: "*.gazl"
```

## Summary and Quick Reference

### Essential Commands
```bash
# Basic compilation
.\PikaCmd.exe impala.pika compile input.impala output.gazl

# Troubleshooting sequence
1. .\PikaCmd.exe                    # Test executable
2. .\PikaCmd.exe impala.pika        # Test script loading
3. .\PikaCmd.exe impala.pika compile input.impala output.gazl  # Full compilation
```

### Common Issues Quick Fix
| Problem | Solution |
|---------|----------|
| Command not recognized | Add `.\` prefix |
| Cannot open file 'compile' | Add `impala.pika` after executable |
| Wrong files processed | Check argument order |
| Permission denied | Check file permissions and admin rights |
| No output generated | Verify input file exists and syntax is correct |

### Next Steps

1. **Practice Implementation**: [Complete Development Workflow Tutorial](complete-development-workflow.md)
   - Learn end-to-end development process with proper compilation integration

2. **Debug Compilation Issues**: [Debug Your Plugin Tutorial](debug-your-plugin.md)
   - Learn systematic debugging when compilation succeeds but runtime fails

3. **Professional Build Setup**: [GAZL Integration Guide](../../assembly/gazl-integration-production.md)
   - Set up automated build pipelines and professional development workflows

### Technical Architecture Reference

You now understand that PikaCmd.exe compilation involves three distinct layers:
1. **Shell Layer**: Command resolution and executable location
2. **Interpreter Layer**: Script loading and execution environment
3. **Script Layer**: Argument parsing and compilation logic

This knowledge forms the foundation for professional firmware development and troubleshooting any compilation issues you may encounter.

---

*Part of the Permut8 Firmware Development Tutorial Series*