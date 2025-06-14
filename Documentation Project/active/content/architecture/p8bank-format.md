# P8Bank Format Specification

Complete specification for Permut8 bank files (.p8bank) based on official Beatrick and FooBar firmware analysis.

## Overview

P8Bank files are the standard distribution format for Permut8 firmware. They package compiled firmware with preset configurations, enabling complete firmware distribution and easy loading via the Permut8 plugin interface.

## Bank File Structure

### Top-Level Format
```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: { /* A0-C9 preset configurations */ }
    Firmware: { /* Compiled GAZL assembly */ }
    Logo: { /* Optional vector graphics */ }
    About: { /* Optional documentation */ }
}
```

## Detailed Sections

### 1. CurrentProgram
**Purpose**: Default preset loaded when bank is opened  
**Format**: String (A0-C9)  
**Example**: `CurrentProgram: A0`

### 2. Programs Section

Complete preset configurations for A0-C9 programs:

```
Programs: {
    A0: {
        Name: "Preset Name"
        Modified: false
        InputLevel: "0.00000000"
        Limiter: "Off"
        FilterFreq: "---"
        FilterPlacement: "Output"
        FeedbackAmount: "0.00000000"
        FeedbackFlip: "Off"
        FeedbackInvert: "Off"
        OutputLevel: "0.00000000"
        Mix: "100.00000000"
        ClockFreq: "1/1"
        SyncMode: "Standard"
        Reverse: "Off"
        Operator1: "4"
        Operand1High: "0x00"
        Operand1Low: "0x00"
        Operator2: "0"
        Operand2High: "0x00"
        Operand2Low: "0x00"
    }
    // A1-C9 similar structure
}
```

#### Parameter Binding

**Plugin Parameters → Firmware Parameters**:
- `Operator1/2`: Maps to `params[OPERATOR_1_PARAM_INDEX]`
- `Operand1/2High`: Maps to `params[OPERAND_1_HIGH_PARAM_INDEX]`
- `Operand1/2Low`: Maps to `params[OPERAND_1_LOW_PARAM_INDEX]`

**Parameter Value Format**:
- Operators: String integers ("0", "1", "4", etc.)
- Operands: Hexadecimal strings ("0x00", "0x80", "0xFF")
- Audio levels: Decimal strings ("-6.02059984", "0.00000000")
- Switches: String ("On", "Off", "Standard")

### 3. Firmware Section

Contains the compiled GAZL assembly code:

```
Firmware: {
    Name: "firmware_name"
    Config: ""
    Code: {
        "PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #2"
        "FALSE: ! DEFi #0"
        "TRUE: ! DEFi #1"
        "signal: GLOB *2"
        "params: GLOB *PARAM_COUNT"
        "displayLEDs: GLOB *4"
        "clock: DATi #0"
        // ... complete GAZL assembly
        "process: FUNC"
        // ... function definitions
    }
}
```

#### Firmware Format Versions

**Version 2** (Standard):
```
"PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #2"
```
- Basic parameter handling
- 16-step sequencing maximum
- Standard memory layout

**Version 3** (Advanced):
```
"PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #3"
```
- Extended parameter handling
- 32-step sequencing
- Host synchronization
- Advanced random generation

### 4. Logo Section (Optional)

Vector graphics for plugin interface customization:
```
Logo: {
    // SVG or vector graphics data
    // Customizes plugin appearance
}
```

### 5. About Section (Optional)

Documentation and usage information:
```
About: {
    // Usage instructions
    // Parameter descriptions
    // Credits and version info
}
```

## Official Firmware Examples

### Beatrick Firmware Structure (Version 2)
- **Format**: `PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #2`
- **Features**: 16-step sequencer, 8 operators
- **Programs**: 30 presets (A0-C9) with creative names
- **Effects**: MUTE, REPEAT, SKIP, HOLD, ACCENT, STUTTER, REVERSE, TAPE_STOP

### FooBar Firmware Structure (Version 3)
- **Format**: `PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #3`
- **Features**: 32-step sequencer, 8 effects, randomization
- **Programs**: 30 presets with advanced parameter configurations
- **Effects**: REVERSE_FX, BIT_CRUSH, TRANCE_GATE, REPEAT, STRETCH, PITCH_SHIFT, HALF_SPEED, TAPE_STOP

## Bank Creation Workflow

### 1. Compile Firmware
```bash
PikaCmd.exe -compile your_firmware.impala
```
Produces: `your_firmware.gazl`

### 2. Create Bank Structure
Package GAZL content into bank format with preset configurations.

### 3. Test Bank
Load via: File → Load Bank → your_firmware.p8bank

### 4. Distribute
Share complete .p8bank file with end users.

## Parameter Design Guidelines

### Preset Organization Strategy
- **A0-A9**: Light/subtle effects
- **B0-B9**: Medium/moderate effects  
- **C0-C9**: Heavy/extreme effects

### Parameter Value Selection
```
Light Mode:   Operator1: "1", Operand1High: "0x20"
Medium Mode:  Operator1: "3", Operand1High: "0x80" 
Heavy Mode:   Operator1: "7", Operand1High: "0xFF"
```

### Naming Conventions
- **Descriptive**: "Subtle Chorus", "Heavy Distortion"
- **Intuitive**: "Light", "Medium", "Heavy"
- **Creative**: "Chop Till You Drop", "The Splice Must Flow"

## Technical Requirements

### Memory Constraints
- Bank files should be optimized for size
- Firmware memory usage should fit within Permut8 limits
- Large delay buffers may affect bank loading

### Compatibility
- Version 2 format: Compatible with all Permut8 versions
- Version 3 format: Requires latest Permut8 firmware
- Parameter ranges: 0-255 for all operand values

### Validation
- All presets must load without errors
- Parameter ranges must be within valid bounds
- GAZL assembly must compile and execute correctly

## See Also

- **[Creating Firmware Banks](../user-guides/tutorials/creating-firmware-banks.md)** - Step-by-step bank creation
- **[Core Language Reference](../language/core_language_reference.md)** - Bank-compatible firmware patterns
- **[Official Firmware Patterns](../user-guides/cookbook/advanced/firmware-patterns.md)** - Beatrick/FooBar examples