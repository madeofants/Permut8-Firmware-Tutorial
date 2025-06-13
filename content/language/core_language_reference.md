# Core Language Reference - Essential Impala

The minimal language reference you need to start creating Permut8 firmware.

## Impala Basics

Impala is a C-like language that compiles to GAZL assembly. If you know C, you know 90% of Impala.

### Key Differences from C:
- No `#include` or preprocessor
- No pointers to functions
- No `malloc/free` (static memory only)
- Built-in `loop` construct
- Native `yield()` for cooperative multitasking

## Essential Firmware Structure

### Full Patch (Audio Processing)
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2  // Required!

global array signal[2]      // Audio I/O: [left, right]
global array params[8]      // Knob values: 0-255
global array displayLEDs[4] // LED displays: 8-bit masks

function process() {
    loop {  // Infinite processing loop
        // Process global signal[0] and signal[1]
        // Audio range: -2047 to 2047 (12-bit)
        
        yield();  // Return control to Permut8
    }
}
```

### Mod Patch (Operator Replacement)
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2  // Required!

global array positions[2]   // Memory positions: [left, right]
global array params[PARAM_COUNT]   // Parameters array
global array displayLEDs[4]        // LED displays

function operate1(int a)
returns int processed
{
    // Check if we should handle this operator
    if ((int) global params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {
        // Modify global positions[0] and positions[1]
        // Positions: 0x00000 to 0xFFFFF (20-bit with 4 frac bits)
        processed = 1;  // Return 1 if handled, 0 to pass through
    } else {
        processed = 0;  // Pass to default handler
    }
}
```

## Core Global Variables

### Always Available
| Global | Type | Description |
|--------|------|-------------|
| `global array params[PARAM_COUNT]` | int array | Knob/switch values (0-255) |
| `global array displayLEDs[4]` | int array | LED displays under knobs |
| `global int clock` | int | Sample counter (0-65535) |
| `global int instance` | int | Unique plugin instance ID |

### Full Patches Only
| Global | Type | Description |
|--------|------|-------------|
| `global array signal[2]` | int array | Audio samples L/R (-2047 to 2047) |

### Mod Patches Only
| Global | Type | Description |
|--------|------|-------------|
| `global array positions[2]` | int array | Memory positions L/R (20-bit fixed point) |

## Parameter Indices

Access knob/switch values via `global params[]`:

```impala
// Parameter indices (externally defined constants)
const int CLOCK_FREQ_PARAM_INDEX       // Clock rate
const int SWITCHES_PARAM_INDEX         // Switch states (bitmask)
const int OPERATOR_1_PARAM_INDEX       // Operator 1 selection
const int OPERAND_1_HIGH_PARAM_INDEX   // First knob (top)
const int OPERAND_1_LOW_PARAM_INDEX    // Second knob
const int OPERATOR_2_PARAM_INDEX       // Operator 2 selection
const int OPERAND_2_HIGH_PARAM_INDEX   // Third knob
const int OPERAND_2_LOW_PARAM_INDEX    // Fourth knob (bottom)
const int PARAM_COUNT                  // Total parameter count

// Operator constants (externally defined)
const int OPERATOR_1_NOP               // No operation
const int OPERATOR_1_AND               // Bitwise AND
const int OPERATOR_1_MUL               // Multiply
const int OPERATOR_1_OSC               // Oscillator
const int OPERATOR_1_RND               // Random

const int OPERATOR_2_NOP               // No operation
const int OPERATOR_2_OR                // Bitwise OR
const int OPERATOR_2_XOR               // Bitwise XOR
const int OPERATOR_2_MSK               // Mask
const int OPERATOR_2_SUB               // Subtract
```

### Switch Bitmasks
```impala
// Switch bitmasks (externally defined constants)
const int SWITCHES_SYNC_MASK           // Tempo sync enabled
const int SWITCHES_TRIPLET_MASK        // Triplet timing
const int SWITCHES_DOTTED_MASK         // Dotted timing
const int SWITCHES_WRITE_PROTECT_MASK  // Write protection
const int SWITCHES_REVERSE_MASK        // Reverse playback

// Example usage:
if ((int) global params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK) {
    // Sync is ON
}
```

## Essential Functions

### Required by Permut8
| Function | When Called | Purpose |
|----------|-------------|---------|
| `process()` | Every sample (full patch) | Main audio processing |
| `operate1/2()` | When operator active (mod patch) | Modify memory positions |

### Optional Callbacks  
| Function | When Called | Purpose |
|----------|-------------|---------|
| `init()` | Once at load | Initialize tables/state |
| `reset()` | Reset switch/DAW | Clear delays/state |
| `update()` | Parameter change | Recalculate values |

### Native Functions
```impala
yield()         // Return control (use in process loop)
abort()         // Kill firmware, restore normal operation
trace(string)   // Debug output (console/DebugView)
read(offset, count, buffer)   // Read from delay memory
write(offset, count, buffer)  // Write to delay memory
```

## Data Types

### Basic Types
- `int` - 32-bit signed integer
- `float` - 32-bit floating point
- `pointer` - Memory address
- `array` - Fixed-size array

### Type Casting
```impala
int x = (int) global params[3];     // Always cast params[]
float f = itof(x);                  // int to float
int i = ftoi(f);                    // float to int
```

## Control Flow

### Loops
```impala
loop { }                // Infinite loop (use yield()!)
for (i = 0 to n) { }    // Inclusive: 0,1,2,...,n
while (x < 10) { }      // Standard while
```

### Conditionals
```impala
if (x > 0) { }
else if (x < 0) { }
else { }
```

## LED Display Patterns

LEDs are 8-bit values (0-255) where each bit lights one LED:

```impala
global displayLEDs[0] = 0x01;  // Single LED (leftmost)
global displayLEDs[0] = 0x80;  // Single LED (rightmost)
global displayLEDs[0] = 0xFF;  // All LEDs on
global displayLEDs[0] = 0x0F;  // Left 4 LEDs
global displayLEDs[0] = 1 << position;  // Variable position
```

## Common Patterns

### Parameter Scaling
```impala
// Map 0-255 to useful range
int depth = (int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 2;      // 0-63
int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1; // 1-8
float mix = itof((int) global params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0; // 0.0-1.0
```

### Safe Audio Processing
```impala
// Clamp to valid range
if (sample > 2047) sample = 2047;
else if (sample < -2047) sample = -2047;
```

### Memory Access (Delays)
```impala
array buffer[2];
read(global clock - 1000, 1, buffer);  // Read 1000 samples ago
// buffer[0] = left, buffer[1] = right
```

## Quick Debugging

### Trace Values
```impala
array buf[128];
sprintf(buf, "Value: %d", myValue);
trace(buf);
```

### Test Mode
```impala
if (DEBUG) {  // Defined when loading from console
    trace("Debug mode active");
}
```

## Minimal Working Examples

### Bit Crusher (Full Patch)
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]              // Audio I/O
global array params[PARAM_COUNT]    // Parameters
global array displayLEDs[4]        // LED displays

function process() {
    loop {
        int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;
        int mask = 0xFFF0 << (12 - bits);
        global signal[0] = (int) global signal[0] & mask;
        global signal[1] = (int) global signal[1] & mask;
        yield();
    }
}
```

### Position Shifter (Mod Patch)
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array positions[2]           // Memory positions 
global array params[PARAM_COUNT]    // Parameters
global array displayLEDs[4]        // LED displays

function operate1(int a)
returns int r
{
    if ((int) global params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {
        int shift = (int) global params[OPERAND_1_HIGH_PARAM_INDEX] << 8;
        global positions[0] = (int) global positions[0] + shift;
        global positions[1] = (int) global positions[1] + shift;
        r = 1;  // Handled
    } else {
        r = 0;  // Pass through
    }
}
```

---

## See Also

**📚 Complete Documentation:**
- **[Complete Language Syntax Reference](language-syntax-reference.md)** - Full syntax guide with all operators and constructs
- **[Memory Management Reference](../reference/memory_management.md)** - Delay lines, read/write operations, position arrays
- **[Utilities Reference](../reference/utilities_reference.md)** - Native functions, math, strings, debugging
- **[Impala Snippets](../../../Impala Snippets.txt)** - Copy-paste utility functions and math library

**🍳 Cookbook Examples:**
- **[Basic Oscillator](../user-guides/cookbook/fundamentals/basic-oscillator.md)** - Simple sine wave generation
- **[Make a Delay](../user-guides/cookbook/audio-effects/make-a-delay.md)** - Basic delay effect implementation
- **[Parameter Mapping](../user-guides/cookbook/fundamentals/parameter-mapping.md)** - Knob and switch handling

**🏗️ Architecture:**
- **[Memory Model](../architecture/memory-model.md)** - Understanding Permut8's memory system
- **[Processing Order](../architecture/processing-order.md)** - When functions are called
- **[Mod vs Full Patches](../architecture/mod-vs-full.md)** - Choosing the right patch type