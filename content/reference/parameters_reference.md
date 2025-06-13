# Parameters Reference

## What This Is
The `params[]` array gives your firmware access to all knob positions, switch states, and system settings. Updated automatically by Permut8 when users turn knobs or flip switches.

## Core Concepts

### Array Structure
```impala
global array params[8]  // 8-bit values (0-255)
```

**All parameters are integers from 0 to 255**, representing the full range of each physical control.

### Parameter Indices
```impala
params[0] = CLOCK_FREQ_PARAM_INDEX      // Sample rate in Hz
params[1] = SWITCHES_PARAM_INDEX        // Bit mask of switch states  
params[2] = OPERATOR_1_PARAM_INDEX      // Operator 1 selection (0-4)
params[3] = OPERAND_1_HIGH_PARAM_INDEX  // Knob 1 (top-left)
params[4] = OPERAND_1_LOW_PARAM_INDEX   // Knob 2 (bottom-left) 
params[5] = OPERATOR_2_PARAM_INDEX      // Operator 2 selection (0-4)
params[6] = OPERAND_2_HIGH_PARAM_INDEX  // Knob 3 (top-right)
params[7] = OPERAND_2_LOW_PARAM_INDEX   // Knob 4 (bottom-right)
```

## Reading Parameters

### Basic Access
```impala
function update() {
    int knob1 = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int switches = (int)params[SWITCHES_PARAM_INDEX];
    
    // Always cast to int for calculations
    if (knob1 > 127) {
        // Do something when knob is past halfway
    }
}
```

### Switch State Testing
```impala
// Test individual switches using bit masks
if ((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK) {
    // Sync switch is ON
}

if ((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_REVERSE_MASK) {
    // Reverse switch is ON
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
    // Operator 1 is set to multiply
}

if ((int)params[OPERATOR_2_PARAM_INDEX] == OPERATOR_2_SUB) {
    // Operator 2 is set to subtract
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
// Result: 0% to 100%
```

### Knob to Float Range
```impala
float mix = itof((int)params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;
// Result: 0.0 to 1.0
```

### Knob to Bit Depth
```impala
int bits = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;
// Result: 1 to 8 bits
```

### Combine Two Knobs (16-bit Value)
```impala
int combined = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] << 8) | 
               (int)params[OPERAND_1_LOW_PARAM_INDEX];
// Result: 0 to 65535
```

### Knob to Exponential Scale
```impala
// Use lookup table for exponential response
readonly array EIGHT_BIT_EXP_TABLE[256] = { /* values */ };

int expValue = (int)EIGHT_BIT_EXP_TABLE[(int)params[OPERAND_1_HIGH_PARAM_INDEX]];
```

## Update Control

### Basic Update Function
```impala
function update() {
    // Called whenever params[] changes
    // Update your global variables here
    
    global myDelay = (int)params[OPERAND_1_HIGH_PARAM_INDEX] * 1000;
    global myGain = itof((int)params[OPERAND_1_LOW_PARAM_INDEX]) / 255.0;
}
```

### Filtering Updates
```impala
// Only trigger update() for specific parameters
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
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    // Convert to LED pattern (0-7 LEDs)
    int ledCount = knobValue >> 5;  // Divide by 32
    displayLEDs[0] = (1 << ledCount) - 1;  // Light up 'ledCount' LEDs
}
```

### Binary LED Display
```impala
function update() {
    int value = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    // Show binary representation
    displayLEDs[0] = value;  // Direct 8-bit pattern
}
```

## Performance Tips

### Copy to Locals for Speed
```impala
function process() {
    // Globals are slow - copy to locals for repeated use
    array localParams[PARAM_COUNT];
    copy(PARAM_COUNT from params to localParams);
    
    int knob1 = localParams[OPERAND_1_HIGH_PARAM_INDEX];
    int knob2 = localParams[OPERAND_1_LOW_PARAM_INDEX];
    
    // Use local copies in calculations
}
```

### Cache Calculated Values
```impala
// Calculate expensive conversions in update(), not process()
global float gain;
global int delayTime;

function update() {
    // Do heavy math once when parameters change
    gain = itof((int)params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;
    delayTime = (int)params[OPERAND_1_LOW_PARAM_INDEX] * 100;
}

function process() {
    // Use pre-calculated values
    signal[0] = ftoi(itof(signal[0]) * gain);
}
```

## Complete Example

```impala
// Global variables updated by parameters
global int mixAmount;
global float feedback;
global int isReversed;

function update() {
    // Convert knob 1 to mix amount (0-255)
    mixAmount = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    // Convert knob 2 to feedback (0.0-0.95)
    feedback = itof((int)params[OPERAND_1_LOW_PARAM_INDEX]) * 0.95 / 255.0;
    
    // Check reverse switch
    isReversed = ((int)params[SWITCHES_PARAM_INDEX] & SWITCHES_REVERSE_MASK) != 0;
    
    // LED feedback - show mix amount
    displayLEDs[0] = mixAmount;
    displayLEDs[1] = (int)(feedback * 255.0);
    
    if (isReversed) {
        displayLEDs[2] = 0xFF;  // All LEDs on when reversed
    } else {
        displayLEDs[2] = 0x00;  // All LEDs off
    }
}
```

## Key Points

- **Always cast to int**: `(int)params[index]` for calculations
- **Update once**: Do expensive parameter processing in `update()`, not `process()`
- **Use updateMask**: Filter unnecessary update calls for better performance
- **Provide LED feedback**: Always show parameter state to users
- **Cache globals**: Copy to locals in performance-critical code