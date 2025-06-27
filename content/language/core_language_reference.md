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
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

## Firmware Format Versions

### Version 2 (Standard) - Recommended for Most Projects
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
```
- **Features**: Basic parameter handling, standard memory layout
- **Step Sequencing**: 16 steps maximum
- **Compatibility**: All Permut8 versions
- **Use Cases**: Effects, basic sequencers, audio processors

### Version 3 (Advanced) - Professional Features
```impala  
const int PRAWN_FIRMWARE_PATCH_FORMAT = 3
```
- **Features**: Extended parameter handling, host synchronization
- **Step Sequencing**: 32 steps maximum
- **Host Integration**: DAW transport sync, position tracking
- **Use Cases**: Complex sequencers, synchronized effects
- **Examples**: FooBar firmware (official advanced sequencer)

## Standard Global Layout (Bank-Compatible)

```impala

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

### Mod Patch (Operator Replacement)
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array positions[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function operate1(int a)
returns int processed
{

    if ((int) global params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {


        processed = 1;
    } else {
        processed = 0;
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

const int CLOCK_FREQ_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int PARAM_COUNT


const int OPERATOR_1_NOP
const int OPERATOR_1_AND
const int OPERATOR_1_MUL
const int OPERATOR_1_OSC
const int OPERATOR_1_RND

const int OPERATOR_2_NOP
const int OPERATOR_2_OR
const int OPERATOR_2_XOR
const int OPERATOR_2_MSK
const int OPERATOR_2_SUB
```

### Switch Bitmasks
```impala

const int SWITCHES_SYNC_MASK
const int SWITCHES_TRIPLET_MASK
const int SWITCHES_DOTTED_MASK
const int SWITCHES_WRITE_PROTECT_MASK
const int SWITCHES_REVERSE_MASK


if ((int) global params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK) {

}
```

## Official Parameter Handling Patterns

Based on Beatrick and FooBar official firmware implementations:

### Parameter Update Mask (Critical Pattern)
```impala

const int updateMask = (
    (1 << OPERATOR_1_PARAM_INDEX) |
    (1 << OPERAND_1_HIGH_PARAM_INDEX) |
    (1 << OPERAND_1_LOW_PARAM_INDEX) |
    (1 << OPERATOR_2_PARAM_INDEX) |
    (1 << OPERAND_2_HIGH_PARAM_INDEX) |
    (1 << OPERAND_2_LOW_PARAM_INDEX)
);
```

### Bit Manipulation for High/Low Parameters
```impala

function readParameterPair(int highIndex, int lowIndex)
returns int combined
{
    int high = (int) global params[highIndex];
    int low = (int) global params[lowIndex];
    combined = (high << 8) | low;
}
```

### Parameter Reading in update() Function
```impala

function update() {

    int operator1 = (int) global params[OPERATOR_1_PARAM_INDEX];
    

    int operand1 = readParameterPair(OPERAND_1_HIGH_PARAM_INDEX, 
                                     OPERAND_1_LOW_PARAM_INDEX);
    

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
yield()
abort()
trace(string)
read(offset, count, buffer)
write(offset, count, buffer)
```

## Data Types

### Basic Types
- `int` - 32-bit signed integer
- `float` - 32-bit floating point
- `pointer` - Memory address
- `array` - Fixed-size array

### Type Casting
```impala
int x = (int) global params[3];
float f = itof(x);
int i = ftoi(f);
```

## Control Flow

### Loops
```impala
loop { }
for (i = 0 to n) { }
while (x < 10) { }
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
global displayLEDs[0] = 0x01;
global displayLEDs[0] = 0x80;
global displayLEDs[0] = 0xFF;
global displayLEDs[0] = 0x0F;
global displayLEDs[0] = 1 << position;
```

## Common Patterns

### Parameter Scaling
```impala

int depth = (int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 2;
int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;
float mix = itof((int) global params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;
```

### Safe Audio Processing
```impala

if (sample > 2047) sample = 2047;
else if (sample < -2047) sample = -2047;
```

### Memory Access (Delays)
```impala
array buffer[2];
read(global clock - 1000, 1, buffer);

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
if (DEBUG) {
    trace("Debug mode active");
}
```

## Minimal Working Examples

### Bit Crusher (Full Patch)
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

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

global array positions[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function operate1(int a)
returns int r
{
    if ((int) global params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {
        int shift = (int) global params[OPERAND_1_HIGH_PARAM_INDEX] << 8;
        global positions[0] = (int) global positions[0] + shift;
        global positions[1] = (int) global positions[1] + shift;
        r = 1;
    } else {
        r = 0;
    }
}
```

---

## Bank Integration Patterns

### Bank-Compatible Firmware Requirements

For firmware that works with .p8bank deployment:

#### Standard Global Layout (Required)
```impala

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clock = 0
```

#### Required Function Structure
```impala

function reset() {

}

function update() {

}

function process() {
    loop {

        yield();
    }
}
```

#### Preset Integration Patterns
```impala

function update() {

    int mode = (int) global params[OPERATOR_1_PARAM_INDEX];
    

    switch (mode) {
        case 1: setupLightMode(); break;
        case 2: setupHeavyMode(); break;

    }
}
```

---

## See Also

**📚 Complete Documentation:**
- **<a href="language-syntax-reference.html">Complete Language Syntax Reference</a>** - Full syntax guide with all operators and constructs
- **<a href="../reference/memory_management.html">Memory Management Reference</a>** - Delay lines, read/write operations, position arrays
- **<a href="../reference/utilities_reference.html">Utilities Reference</a>** - Native functions, math, strings, debugging
- **[Impala Snippets](../../../Impala Snippets.txt)** - Copy-paste utility functions and math library

**📦 Bank Integration:**
- **<a href="../architecture/p8bank-format.html">P8Bank Format</a>** - Complete firmware packaging
- **<a href="../user-guides/tutorials/creating-firmware-banks.html">Creating Firmware Banks</a>** - Distribution workflow
- **<a href="../user-guides/cookbook/advanced/firmware-patterns.html">Official Firmware Patterns</a>** - Beatrick/FooBar patterns

**🍳 Cookbook Examples:**
- **<a href="../user-guides/cookbook/fundamentals/basic-oscillator.html">Basic Oscillator</a>** - Simple sine wave generation
- **<a href="../user-guides/cookbook/audio-effects/make-a-delay.html">Make a Delay</a>** - Basic delay effect implementation
- **<a href="../user-guides/cookbook/fundamentals/parameter-mapping.html">Parameter Mapping</a>** - Knob and switch handling

**🏗️ Architecture:**
- **<a href="../architecture/memory-model.html">Memory Model</a>** - Understanding Permut8's memory system
- **<a href="../architecture/processing-order.html">Processing Order</a>** - When functions are called
- **<a href="../architecture/mod-vs-full.html">Mod vs Full Patches</a>** - Choosing the right patch type