# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Permut8 firmware development environment containing:
- **Impala source code** (.impala files) - C-like language for DSP firmware
- **GAZL assembly output** (.gazl files) - Compiled firmware for Permut8 device 
- **Compilation tools** - PikaCmd.exe and associated compiler infrastructure
- **Documentation Project** - Comprehensive developer documentation with AI-assisted protocols

## Key Commands

### Compile Firmware
```bash
# Compile single file
PikaCmd.exe impala.pika compile <source.impala> <output.gazl>

# Auto-compile all .impala files (Windows)
"Compile Loop Windows.cmd"
```

### Load Firmware into Permut8
1. Open Permut8 plugin in DAW
2. Click console button (bottom right)
3. Type: `patch <filename.gazl>`

## Code Architecture

### Firmware Types
- **Full patches**: Implement `process()` for complete DSP chain replacement
- **Mod patches**: Implement `operate1()` and/or `operate2()` for operator replacement

### Core Impala Structure
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2  // Required for v1.1+

global array signal[2]      // Audio I/O: [left, right] 
global array params[8]      // Knob values: 0-255
global array displayLEDs[4] // LED displays: 8-bit masks

function process() {
    loop {
        // Main audio processing loop
        // Audio range: -2047 to 2047 (12-bit)
        yield()  // Return control to host
    }
}
```

### Memory Model
- **Static memory only** - No malloc/free
- **Delay-line memory** - Accessed via `read()`/`write()` natives
- **12-bit audio** - Sample range -2047 to 2047
- **Cooperative multitasking** - Use `yield()` for real-time operation

### Language Differences from C
- No preprocessor or `#include`
- No function pointers
- Built-in `loop` construct
- Native `yield()`, `read()`, `write()`, `trace()` functions

## Documentation Project Structure

The `Documentation Project/` contains a structured documentation system:

### Active Documentation (`active/`)
- `content/` - Main documentation content organized by theme
- `ai-context/` - AI session context and protocols
- `human-workspace/` - Human-facing planning and progress files  
- `session-logs/` - Detailed session logs

### Key Documentation Areas
- `user-guides/QUICKSTART.md` - 30-minute firmware tutorial
- `content/language/` - Language reference and syntax
- `content/cookbook/` - Recipe-based tutorials organized by category
- `content/architecture/` - Memory model and processing patterns
- `content/assembly/` - GAZL assembly integration

## Working with Documentation

### AI Session Protocols
When working on documentation, follow the protocols in `Protocols/active/`:

#### Session Recovery Command (use first in new sessions):
```
read session docs to recover our progress: TodoRead + Read Protocols/active/SESSION-START-PROTOCOL.md + Read Documentation Project/active/COMPREHENSIVE-AUDIT-TASK-TRACKER.md + Read Documentation Project/active/DOCUMENTATION_STATUS_TRACKER.md + Task "find most recent session log"
```

- Review `Protocols/active/SESSION-START-PROTOCOL.md` for session requirements
- Follow protocols in `Protocols/active/` for current standards
- Reference `Protocols/reference/` for comprehensive methodologies
- Create session logs for all work
- Update tracking documents after audits

### Content Organization
Documentation follows a cookbook + reference pattern:
- **Cookbook recipes** - Step-by-step tutorials for specific tasks
- **Reference docs** - Comprehensive API and language documentation  
- **Architecture guides** - System design and patterns
- **User guides** - Getting started and tutorials

## File Extensions
- `.impala` - Impala source code
- `.gazl` - Compiled GAZL assembly 
- `.pika` - Pika language files (compiler infrastructure)
- `.ivg` - Image files (logos, graphics)