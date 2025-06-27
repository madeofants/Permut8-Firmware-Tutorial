# Parameters Reference

## 🚨 CRITICAL: Parameter Access Requirements

**NEVER use raw indices** - these will cause compilation errors:
```impala

volume = params[3] * 2;
int knobValue = params[7];
```

**ALWAYS use parameter constants** - verified from all official firmware:
```impala

volume = (int)global params[OPERAND_2_HIGH_PARAM_INDEX] * 2;
int knobValue = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
```

**Required Constants** (must be defined in every firmware):
```impala
const int CLOCK_FREQ_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int PARAM_COUNT
```

---

## What This Is
The `params[]` array gives your firmware access to all knob positions, switch states, and system settings. Updated automatically by Permut8 when users turn knobs or flip switches.

**🚨 CRITICAL**: Never use raw indices like `params[3]`. Always use parameter constants for compilation.

## 🎛️ **Permut8 Interface Architecture**

### **Physical Controls (Actual Hardware)**

#### **Operation Selection Knobs**
- **Operator Control 1** (`params[OPERATOR_1_PARAM_INDEX]`) - Physical knob that selects Instruction 1 operation type
- **Operator Control 2** (`params[OPERATOR_2_PARAM_INDEX]`) - Physical knob that selects Instruction 2 operation type

#### **Parameter Setting Interface**  
- **Instruction 1 High Operand** (`params[OPERAND_1_HIGH_PARAM_INDEX]`) - Set via LED display + switches (0-255)
- **Instruction 1 Low Operand** (`params[OPERAND_1_LOW_PARAM_INDEX]`) - Set via LED display + switches (0-255)
- **Instruction 2 High Operand** (`params[OPERAND_2_HIGH_PARAM_INDEX]`) - Set via LED display + switches (0-255)
- **Instruction 2 Low Operand** (`params[OPERAND_2_LOW_PARAM_INDEX]`) - Set via LED display + switches (0-255)

#### **System Controls**
- **Clock Frequency Knob** (`params[CLOCK_FREQ_PARAM_INDEX]`) - Dedicated physical knob for tempo sync timing
- **Mode Switches** (`params[SWITCHES_PARAM_INDEX]`) - Five switches: SYNC, REV, Triplet, Dotted, Write Protect

## 📋 **Standard Terminology Convention**

### **✅ CORRECT Terminology Patterns**

#### **Original Operator System References**
- **"Operator Control 1"** - Only for the physical operation selection knob (`params[2]`)
- **"Operator Control 2"** - Only for the physical operation selection knob (`params[5]`)
- **"Instruction 1 High Operand"** - Parameter set via LED display/switches (`params[3]`)
- **"Instruction 1 Low Operand"** - Parameter set via LED display/switches (`params[4]`)
- **"Instruction 2 High Operand"** - Parameter set via LED display/switches (`params[6]`)
- **"Instruction 2 Low Operand"** - Parameter set via LED display/switches (`params[7]`)

#### **Custom Firmware Override References**
- **"Control 1"** - Custom meaning for `params[OPERAND_1_HIGH_PARAM_INDEX]` (was Instruction 1 High Operand)
- **"Control 2"** - Custom meaning for `params[OPERAND_1_LOW_PARAM_INDEX]` (was Instruction 1 Low Operand)
- **"Control 3"** - Custom meaning for `params[OPERAND_2_HIGH_PARAM_INDEX]` (was Instruction 2 High Operand)
- **"Control 4"** - Custom meaning for `params[OPERAND_2_LOW_PARAM_INDEX]` (was Instruction 2 Low Operand)

### **❌ AVOID These Patterns**
- **"Control 1/2/3/4"** - Preferred, refers to operand controls via params[0/1/3/4/6/7]
- **"Operator Control 1" for operand controls** - Incorrect, operator controls select operations
- **"Parameter knobs"** - Too vague, missing context
- **"The delay knob"** - Not specific enough

## 🔄 **Parameter Context: Original vs Custom Firmware**

### **Original Operator System**
Parameters directly control the built-in operator system:

| Parameter | Physical Control | Function | Range |
|-----------|-----------------|----------|-------|
| `params[0]` | **Clock Frequency Knob** | Tempo sync timing | 0-255 |
| `params[1]` | **Mode Switches** | Switch states bitmask | 0-31 |
| `params[2]` | **Operator Control 1** | Instruction 1 operation type | 0-4 |
| `params[3]` | **LED Display + Switches** | Instruction 1 High Operand | 0-255 |
| `params[4]` | **LED Display + Switches** | Instruction 1 Low Operand | 0-255 |
| `params[5]` | **Operator Control 2** | Instruction 2 operation type | 0-4 |
| `params[6]` | **LED Display + Switches** | Instruction 2 High Operand | 0-255 |
| `params[7]` | **LED Display + Switches** | Instruction 2 Low Operand | 0-255 |

### **Custom Firmware Override**
Same hardware, completely custom meanings:

| Parameter | Original Interface | Custom Override | Typical Custom Use |
|-----------|-------------------|-----------------|-------------------|
| `params[0]` | Clock Frequency Knob | Usually unchanged | Tempo sync or custom timing |
| `params[1]` | Mode Switches | Custom or ignored | Effect modes or unchanged |
| `params[2]` | Operator Control 1 | Usually ignored | N/A (set to NOP in presets) |
| `params[3]` | Instruction 1 High Operand | **Control 1** | Primary effect parameter |
| `params[4]` | Instruction 1 Low Operand | **Control 2** | Secondary effect parameter |
| `params[5]` | Operator Control 2 | Usually ignored | N/A (set to NOP in presets) |
| `params[6]` | Instruction 2 High Operand | **Control 3** | Third effect parameter |
| `params[7]` | Instruction 2 Low Operand | **Control 4** | Fourth effect parameter |

### **Operator Modification (Hybrid)**
Retains original meanings but with enhanced functionality:

- **Operator Knobs**: Still select operation types, but operations are custom-coded
- **Operand Controls**: Still set via LED displays/switches with original meanings
- **Custom Logic**: Enhanced operator behavior while maintaining familiar interface

## Core Concepts

### Array Structure
```impala
global array params[8]
```

**All parameters are integers from 0 to 255**, representing the full range of each physical control.

### Parameter Indices
```impala
params[0] = CLOCK_FREQ_PARAM_INDEX
params[1] = SWITCHES_PARAM_INDEX
params[2] = OPERATOR_1_PARAM_INDEX
params[3] = OPERAND_1_HIGH_PARAM_INDEX
params[4] = OPERAND_1_LOW_PARAM_INDEX
params[5] = OPERATOR_2_PARAM_INDEX
params[6] = OPERAND_2_HIGH_PARAM_INDEX
params[7] = OPERAND_2_LOW_PARAM_INDEX
```

## Reading Parameters

### Basic Access
```impala
function update() {
    int control1 = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int switches = (int)params[SWITCHES_PARAM_INDEX];
    

    if (control1 > 127) {

    }
}
```

### Switch State Testing
```impala

if ((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK) {

}

if ((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_REVERSE_MASK) {

}
```

**Available switch masks:**
- `SWITCHES_SYNC_MASK` - Tempo sync enable
- `SWITCHES_TRIPLET_MASK` - Triplet timing
- `SWITCHES_DOTTED_MASK` - Dotted timing  
- `SWITCHES_WRITE_PROTECT_MASK` - Memory write protection
- `SWITCHES_REVERSE_MASK` - Reverse playback

### Operator Selection
```impala
if ((int)params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {

}

if ((int)params[OPERATOR_2_PARAM_INDEX] == OPERATOR_2_SUB) {

}
```

**Operator 1 constants:**
- `OPERATOR_1_NOP`, `OPERATOR_1_AND`, `OPERATOR_1_MUL`, `OPERATOR_1_OSC`, `OPERATOR_1_RND`

**Operator 2 constants:**  
- `OPERATOR_2_NOP`, `OPERATOR_2_OR`, `OPERATOR_2_XOR`, `OPERATOR_2_MSK`, `OPERATOR_2_SUB`

## Common Conversions

### Knob to Percentage
```impala
int percent = (int)params[OPERAND_1_HIGH_PARAM_INDEX] * 100 / 255;

```

### Knob to Float Range
```impala
float mix = itof((int)params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;

```

### Knob to Bit Depth
```impala
int bits = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;

```

### Combine Two Knobs (16-bit Value)
```impala
int combined = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] << 8) | 
               (int)params[OPERAND_1_LOW_PARAM_INDEX];

```

### Knob to Exponential Scale
```impala

readonly array EIGHT_BIT_EXP_TABLE[256] = { /* values */ };

int expValue = (int)EIGHT_BIT_EXP_TABLE[(int)params[OPERAND_1_HIGH_PARAM_INDEX]];
```

## Update Control

### Basic Update Function
```impala
function update() {


    
    global myDelay = (int)params[OPERAND_1_HIGH_PARAM_INDEX] * 1000;
    global myGain = itof((int)params[OPERAND_1_LOW_PARAM_INDEX]) / 255.0;
}
```

### Filtering Updates
```impala

readonly int updateMask = 
    (1 << OPERAND_1_HIGH_PARAM_INDEX) | 
    (1 << OPERAND_1_LOW_PARAM_INDEX) |
    (1 << SWITCHES_PARAM_INDEX);
```

This prevents `update()` from being called when clock frequency or operators change, reducing CPU usage.

## LED Feedback

### Display Parameter Values
```impala
function update() {
    int controlValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    

    int ledCount = controlValue >> 5;
    displayLEDs[0] = (1 << ledCount) - 1;
}
```

### Binary LED Display
```impala
function update() {
    int value = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    

    displayLEDs[0] = value;
}
```

## Performance Tips

### Copy to Locals for Speed
```impala
function process() {

    array localParams[PARAM_COUNT];
    copy(PARAM_COUNT from params to localParams);
    
    int control1 = localParams[OPERAND_1_HIGH_PARAM_INDEX];
    int control2 = localParams[OPERAND_1_LOW_PARAM_INDEX];
    

}
```

### Cache Calculated Values
```impala

global float gain;
global int delayTime;

function update() {

    gain = itof((int)params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;
    delayTime = (int)params[OPERAND_1_LOW_PARAM_INDEX] * 100;
}

function process() {

    signal[0] = ftoi(itof(signal[0]) * gain);
}
```

## Complete Example

```impala

global int mixAmount;
global float feedback;
global int isReversed;

function update() {

    mixAmount = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    

    feedback = itof((int)params[OPERAND_1_LOW_PARAM_INDEX]) * 0.95 / 255.0;
    

    isReversed = ((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_REVERSE_MASK) != 0;
    

    displayLEDs[0] = mixAmount;
    displayLEDs[1] = (int)(feedback * 255.0);
    
    if (isReversed) {
        displayLEDs[2] = 0xFF;
    } else {
        displayLEDs[2] = 0x00;
    }
}
```

## Key Points

- **Always cast to int**: `(int)params[index]` for calculations
- **Update once**: Do expensive parameter processing in `update()`, not `process()`
- **Use updateMask**: Filter unnecessary update calls for better performance
- **Provide LED feedback**: Always show parameter state to users
- **Cache globals**: Copy to locals in performance-critical code