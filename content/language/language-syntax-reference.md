# Language Syntax Reference

Complete syntax guide for the Impala programming language used in Permut8 firmware development.

## Overview

Impala is a C-like language that compiles to GAZL assembly for the Permut8 device. It provides real-time audio processing capabilities with static memory allocation and cooperative multitasking.

**Key Features:**
- C-like syntax with simplified semantics
- Static memory allocation (no malloc/free)
- Cooperative multitasking with `yield()`
- Built-in audio processing constructs
- Direct hardware integration

## Program Structure

Every Impala firmware follows this basic structure:

```impala
/*
    Firmware comments and description
*/

/* ------ Required Format Declaration ------ */
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

/* ------ Global Variables ------ */
global array signal[2]
global array positions[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

/* ------ Global State ------ */
global int myVariable = 0
global array myBuffer[1024]

/* ------ Required Functions ------ */
function process()
function operate1(int a) returns int processed

/* ------ Optional Functions ------ */
function init()
function reset()
function update()
```

## Data Types

### Basic Types
| Type | Size | Range | Description |
|------|------|-------|-------------|
| `int` | 32-bit | -2,147,483,648 to 2,147,483,647 | Signed integer |
| `float` | 32-bit | IEEE 754 | Floating point |
| `pointer` | 32-bit | Memory address | Pointer to memory |

### Arrays
```impala

array buffer[1024]
global array delayLine[8192]
readonly array table[256]


buffer[0] = 123;
int value = buffer[0];
```

### Type Casting
```impala
int x = (int) global params[0];
float f = itof(x);
int i = ftoi(f);
pointer p = &buffer[0];
```

## Constants and Variables

### Constants
```impala
const int BUFFER_SIZE = 1024
const float PI = 3.14159265
const int FALSE = 0
const int TRUE = 1
```

### Variable Declarations
```impala

int sampleCount
float delayTime = 0.5
array tempBuffer[64]


global int position = 0
global array circularBuffer[2048]
global float mixLevel


readonly array sineTable[1024] = { /* data */ }
readonly int maxDelay = 8000
```

## Operators

### Arithmetic Operators
```impala
int a = 10 + 5;
int b = 10 - 5;
int c = 10 * 5;
int d = 10 / 5;
int e = 10 % 3;
```

### Bitwise Operators
```impala
int a = 0xFF & 0x0F;
int b = 0xFF | 0x0F;
int c = 0xFF ^ 0x0F;
int d = ~0xFF;
int e = 0xFF << 2;
int f = 0xFF >> 2;
```

### Comparison Operators
```impala
if (a == b) { }
if (a != b) { }
if (a < b) { }
if (a <= b) { }
if (a > b) { }
if (a >= b) { }
```

### Logical Operators
```impala
if (a && b) { }
if (a || b) { }
if (!a) { }
```

## Control Flow

### Conditional Statements
```impala

if (condition) {

}


if (condition) {

} else {

}


if (condition1) {

} else if (condition2) {

} else {

}
```

### Loops

#### For Loops
```impala

for (i = 0 to n) {

}


for (i = 0; i < n; i = i + 2) {

}
```

#### While Loops
```impala
while (condition) {

}


int i = 0;
while (i < 10) {

    i = i + 1;
}
```

#### Infinite Loops
```impala
loop {


    yield();
}
```

## Functions

### Function Declaration
```impala

function myFunction() {

}


function processSignal(int gain, float frequency) {

}


function calculateGain(int input) 
returns int output
{
    output = input * 2;
}


function complexFunction(int param)
returns float result
locals int temp, array workspace[256]
{
    temp = param * 2;
    result = itof(temp);
}
```

### Required Functions for Firmware

#### Full Patches
```impala
function process() {
    loop {


        
        yield();
    }
}
```

#### Mod Patches
```impala
function operate1(int a)
returns int processed
{
    if ((int) global params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {


        processed = 1;
    } else {
        processed = 0;
    }
}

function operate2(int a)
returns int processed
{

    processed = 0;
}
```

### Optional Callback Functions
```impala
function init() {


}

function reset() {


}

function update() {


}
```

## Built-in Functions

### Audio Processing
```impala

read(int offset, int frameCount, pointer buffer)
write(int offset, int frameCount, pointer buffer)


yield()
abort()
```

### Debug Functions
```impala
trace(pointer string)
```

### Math Functions
```impala

float cos(float x)
float sin(float x)
float abs(float x)
float floor(float x)
```

## Global Variables and APIs

### Always Available
```impala
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clock
global int instance
```

### Full Patches Only
```impala
global array signal[2]

```

### Mod Patches Only
```impala
global array positions[2]

```

### Parameter Access
```impala

int knob1 = (int) global params[OPERAND_1_HIGH_PARAM_INDEX];
int knob2 = (int) global params[OPERAND_1_LOW_PARAM_INDEX];
int switches = (int) global params[SWITCHES_PARAM_INDEX];


if ((int) global params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK) {

}
```

## Memory Management

### Static Allocation Only
```impala

global array largeBuffer[16384]
array tempBuffer[64]



```

### Memory Access Patterns
```impala

array buffer[1024];
int index = 0;
if (index >= 0 && index < 1024) {
    buffer[index] = value;
}


global int writePos = 0;
global array circularBuffer[1024];

writePos = (writePos + 1) % 1024;
circularBuffer[writePos] = newValue;
```

## Real-time Considerations

### Cooperative Multitasking
```impala
function process() {
    loop {

        
        yield();
    }
}
```

### Performance Guidelines
```impala

int sample = (int) global signal[0];
sample = sample >> 1;
global signal[0] = sample;


readonly array expTable[256] = { /* precomputed values */ };
int result = expTable[input & 0xFF];
```

## Common Patterns

### Parameter Scaling
```impala

int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;
float gain = itof((int) global params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;
int delay = (int) global params[OPERAND_1_HIGH_PARAM_INDEX] << 3;
```

### Audio Range Clamping
```impala

if (sample > 2047) sample = 2047;
else if (sample < -2047) sample = -2047;
```

### LED Display
```impala

global displayLEDs[0] = 0x01;
global displayLEDs[0] = 0x80;
global displayLEDs[0] = 0xFF;
global displayLEDs[0] = 1 << position;
```

### Delay Line Access
```impala

array buffer[2];


write(global clock, 1, global signal);


read(global clock - delayTime, 1, buffer);
int delayedLeft = buffer[0];
int delayedRight = buffer[1];
```

## Comments
```impala


/*
   Multi-line comment
   can span multiple lines
*/

/* 
 * Traditional C-style
 * multi-line comment
 */
```

## Preprocessor
**Note:** Impala has NO preprocessor. These don't exist:
- `#include`
- `#define`
- `#ifdef`
- `#pragma`

All configuration must be done with `const` declarations and conditional compilation is not available.

## Error Handling
```impala

function safeDivide(int a, int b)
returns int result
{
    if (b != 0) {
        result = a / b;
    } else {
        result = 0;
        trace("Division by zero avoided");
    }
}
```

## Example: Complete Bit Crusher
```impala
/*
    Simple bit crusher firmware demonstrating core Impala syntax
*/
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function process() {
    loop {

        int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 4) + 1;
        

        int mask = 0xFFF0 << (12 - bits);
        

        global signal[0] = (int) global signal[0] & mask;
        global signal[1] = (int) global signal[1] & mask;
        

        global displayLEDs[0] = (1 << bits) - 1;
        
        yield();
    }
}
```

This syntax reference reflects the actual Impala language as implemented in the Permut8 compiler, based on analysis of working source code.

---

## See Also

**📚 Essential References:**
- **<a href="core_language_reference.html">Core Language Reference</a>** - Quick start guide with minimal examples
- **<a href="../reference/memory_management.html">Memory Management Reference</a>** - Delay lines, read/write operations, advanced patterns
- **<a href="../reference/utilities_reference.html">Utilities Reference</a>** - Native functions, math library, debugging tools
- **[Impala Snippets](../../../Impala Snippets.txt)** - Copy-paste utility functions and advanced math

**🍳 Practical Examples:**
- **<a href="../user-guides/QUICKSTART.html">QUICKSTART Guide</a>** - 30-minute firmware tutorial
- **[Cookbook Fundamentals](../user-guides/cookbook/fundamentals/)** - Basic building blocks
- **[Audio Effects Cookbook](../user-guides/cookbook/audio-effects/)** - Complete effect implementations

**🏗️ System Architecture:**
- **<a href="../architecture/memory-model.html">Memory Model</a>** - Static allocation, delay lines, position arrays
- **<a href="../architecture/processing-order.html">Processing Order</a>** - Function call sequence and timing
- **<a href="../architecture/state-management.html">State Management</a>** - Global variables and persistence

**🔧 Development:**
- **<a href="../user-guides/tutorials/build-your-first-filter.html">Build Your First Filter</a>** - Step-by-step tutorial
- **<a href="../user-guides/tutorials/debug-your-plugin.html">Debug Your Plugin</a>** - Debugging and troubleshooting
- **<a href="../user-guides/tutorials/test-your-plugin.html">Test Your Plugin</a>** - Validation and testing