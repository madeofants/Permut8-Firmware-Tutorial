# Creating Firmware Banks

Complete step-by-step guide to packaging your compiled firmware into distributable .p8bank files.

## What You'll Learn

- Package .gazl files into .p8bank format
- Create multiple presets for your firmware
- Test and validate bank files
- Distribute professional firmware packages

## Prerequisites

- Compiled .gazl firmware file
- Understanding of parameter mapping
- Basic knowledge of Permut8 plugin interface

## Complete Workflow Overview

```
.impala source → .gazl assembly → .p8bank package → Distribution
```

## Step 1: Prepare Your Compiled Firmware

### Ensure Clean Compilation
```bash
PikaCmd.exe -compile your_effect.impala
```

**Verify Output**:
- `your_effect.gazl` file created
- No compilation errors
- Firmware follows bank-compatible patterns

### Bank-Compatible Firmware Requirements

Your firmware must include these elements:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clock = 0


function process() {
    loop {

        yield();
    }
}
```

## Step 2: Design Your Preset System

### Preset Organization Strategy

**A0-A9: Light/Subtle Effects**
- Low intensity settings
- Gentle parameter values
- Suitable for mixing/mastering

**B0-B9: Medium/Moderate Effects** 
- Balanced intensity
- Noticeable but controlled
- Good for creative processing

**C0-C9: Heavy/Extreme Effects**
- High intensity settings
- Dramatic parameter values  
- Special effects and sound design

### Parameter Mapping Strategy

Design your firmware to respond to different operator values:

```impala
function update() {
    int mode = (int) global params[OPERATOR_1_PARAM_INDEX];
    
    switch (mode) {
        case 1:
            setupLightProcessing();
            break;
        case 2:
            setupHeavyProcessing();
            break;
        case 3:
            setupExperimentalProcessing();
            break;
    }
}
```

## Step 3: Create Bank Structure

### Basic Bank Template

**⚠️ Critical**: Header must be exactly `Permut8BankV2: {` (not filename-based)

```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: {
            Name: "Subtle Effect"
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
            Operator1: "1"
            Operand1High: "0x20"
            Operand1Low: "0x00"
            Operator2: "0"
            Operand2High: "0x00"
            Operand2Low: "0x00"
        }
        A1: {
            Name: "Medium Effect"
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
            Operator1: "2"
            Operand1High: "0x80"
            Operand1Low: "0x40"
            Operator2: "0"
            Operand2High: "0x00"
            Operand2Low: "0x00"
        }

    }
    Firmware: {
        Name: "your_effect"
        Config: ""
        Code: {

            "PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #2"
            "signal: GLOB *2"
            "params: GLOB *PARAM_COUNT"
            "displayLEDs: GLOB *4"
            "clock: DATi #0"

            "process: FUNC"

        }
    }
}
```

### Parameter Value Guidelines

**Operator Values** (String format):
- "0": No operation/bypass
- "1": Light processing
- "2": Medium processing  
- "3": Heavy processing
- "4"-"7": Specialized modes

**Operand Values** (Hexadecimal strings):
- "0x00": Minimum (0)
- "0x40": Quarter (64)
- "0x80": Half (128)
- "0xC0": Three-quarters (192)
- "0xFF": Maximum (255)

**Audio Levels** (Decimal strings):
- "0.00000000": Unity gain
- "-6.02059984": Half volume (-6dB)
- "6.02059984": Double volume (+6dB)

## Step 4: GAZL Integration

### Clean GAZL Content First

**⚠️ Critical**: GAZL must be cleaned before bank integration to avoid loading errors.

1. **Open your_effect.gazl** in a text editor
2. **Remove compiler-generated comments**:
   ```
   ; Compiled with Impala version 1.0    ← DELETE THIS LINE
   ```
3. **Remove any separator lines**:
   ```
   ;-----------------------------------------------------------------------------    ← DELETE THESE LINES
   ```
4. **Keep only pure assembly code** (no comments, no decorative formatting)

### Extract GAZL Content

1. **Copy cleaned assembly code** (after removing comments/separators)
2. **Format for bank structure**:

```
Code: {
    "line 1 of GAZL assembly"
    "line 2 of GAZL assembly"
    "line 3 of GAZL assembly"

}
```

### GAZL Formatting Rules

- Each line becomes a quoted string
- Preserve exact spacing and syntax
- Include all assembly directives
- Maintain line order exactly
- **No compiler comments or separator lines**

**Example GAZL Integration**:
```
Code: {
    "PRAWN_FIRMWARE_PATCH_FORMAT: ! DEFi #2"
    "FALSE: ! DEFi #0"
    "TRUE: ! DEFi #1"
    "signal: GLOB *2"
    "params: GLOB *PARAM_COUNT"
    "displayLEDs: GLOB *4"
    "process: FUNC"
    "PARA *1"
    "$sample: LOCi"
    "loop {"
    "  PEEK $sample &signal:0"
    "
    "  POKE &signal:0 $sample"
    "  CALL ^yield %0 *1"
    "}"
    "RETU"
}
```

## Step 5: Testing and Validation

### Pre-Distribution Checklist

**Bank Loading Test**:
- [ ] Bank loads without errors
- [ ] All presets (A0-C9) accessible
- [ ] Default preset (CurrentProgram) loads correctly

**Parameter Testing**:
- [ ] All parameter ranges functional (0-255)
- [ ] Operator switching works between presets
- [ ] Operand values produce expected results
- [ ] LED displays respond correctly

**Audio Testing**:
- [ ] Audio processing works across all presets
- [ ] No audio dropouts or glitches
- [ ] Parameter changes are smooth (no clicks)
- [ ] Audio levels appropriate for each preset

**Preset Validation**:
- [ ] Preset names accurately describe sound
- [ ] A0-A9 presets are subtle/light
- [ ] B0-B9 presets are medium intensity
- [ ] C0-C9 presets are heavy/extreme
- [ ] Smooth progression between preset intensities

### Testing Workflow

```
1. Load bank: File → Load Bank → your_effect.p8bank
2. Test A0 preset:
   - Play audio through Permut8
   - Adjust all knobs (test parameter ranges)
   - Verify LED display functionality
   - Check audio quality and levels
3. Repeat for A1, A2, etc.
4. Test preset switching:
   - Switch between A0 → A1 → B0 → C0
   - Verify smooth transitions
   - No audio interruptions
5. Test bank unload/reload cycle
```

## Step 6: Professional Distribution

### Distribution Package

**Essential Files**:
- `your_effect.p8bank` (main bank file)
- `README.txt` (installation and usage instructions)

**Optional Files**:
- Demo audio examples
- Parameter guide
- Version history

### End-User Instructions Template

```
# Installing Your Effect Bank

## Installation
1. Download your_effect.p8bank
2. Open Permut8 plugin in your DAW
3. Go to File → Load Bank
4. Select your_effect.p8bank
5. Choose from presets A0-C9

## Preset Guide
- A0-A9: Light processing modes
  - A0: "Subtle Effect" - Gentle processing
  - A1: "Light Touch" - Minimal coloration
  - A2: "Soft Enhancement" - Mild effect
  
- B0-B9: Medium processing modes  
  - B0: "Balanced" - Even processing
  - B1: "Noticeable" - Clear effect
  - B2: "Pronounced" - Strong processing

- C0-C9: Heavy processing modes
  - C0: "Intense" - Heavy effect
  - C1: "Extreme" - Maximum processing
  - C2: "Experimental" - Special effects

## Parameters
- Control 1: [Primary effect parameter]
- Control 2: [Secondary parameter]
- Control 3: [Modulation/mix parameter] 
- Control 4: [Special feature parameter]

## Tips
- Start with A0 preset for subtle effects
- Use B presets for creative processing
- C presets are for special effects and sound design
- All parameters respond in real-time
```

## Advanced Bank Features

### Multi-Effect Banks

For firmware with multiple effects, organize presets by effect type:

```
A0-A3: Delay effects (short to long)
A4-A7: Reverb effects (room to hall)  
A8-A9: Combined delay+reverb

B0-B3: Distortion effects (light to heavy)
B4-B7: Filter effects (low to high resonance)
B8-B9: Combined distortion+filter

C0-C9: Experimental combinations
```

### Version Management

Track your bank versions:

```
Firmware: {
    Name: "your_effect_v1_2"
    Config: ""
    Code: { /* assembly */ }
}
```

### Bank Optimization

**Memory Optimization**:
- Remove unused code sections
- Optimize delay buffer sizes
- Minimize global variable usage

**Performance Optimization**:
- Use efficient parameter change detection
- Implement smooth parameter interpolation
- Optimize real-time processing loops

## Common Issues and Solutions

### Bank Won't Load
- **"Invalid data format (unsupported version?)"**: Check bank header format
  - Must start with `Permut8BankV2: {` (exact format, case-sensitive)
  - Not `filename.p8bank: {` or other variations
- **"Invalid mnemonic: Compiled"**: Clean GAZL file first
  - Remove compiler comment: `; Compiled with Impala version 1.0`
  - Remove from first line of .gazl before bank creation
- **"Invalid mnemonic" with dashes**: Remove decorative separators
  - Remove lines like `;-----------------------------------------------------------------------------`
  - Keep only pure assembly code
- **Check GAZL syntax**: Ensure no formatting errors in clean assembly
- **Verify parameter ranges**: All values within 0-255
- **Test individual presets**: Isolate problematic preset

### Parameter Issues
- **No response**: Check parameter index mapping
- **Wrong ranges**: Verify operand value format
- **Unexpected behavior**: Review firmware parameter handling

### Audio Problems
- **No sound**: Verify signal processing loop
- **Distorted audio**: Check audio level calculations
- **Clicks/pops**: Add parameter smoothing

## See Also

- **[P8Bank Format](../../architecture/p8bank-format.md)** - Complete format specification
- **[Core Language Reference](../../language/core_language_reference.md)** - Bank-compatible patterns
- **[Complete Development Workflow](complete-development-workflow.md)** - Full development process