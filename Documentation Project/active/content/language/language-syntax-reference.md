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
global array signal[2]              // Full patches only
global array positions[2]           // Mod patches only  
global array params[PARAM_COUNT]    // Always available
global array displayLEDs[4]         // Always available

/* ------ Global State ------ */
global int myVariable = 0
global array myBuffer[1024]

/* ------ Required Functions ------ */
function process()                   // Full patches
function operate1(int a) returns int processed  // Mod patches

/* ------ Optional Functions ------ */
function init()                     // Called once at load
function reset()                    // Called on reset
function update()                   // Called on parameter change
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
// Fixed-size arrays only
array buffer[1024]              // Local array
global array delayLine[8192]    // Global array
readonly array table[256]       // Read-only array

// Array access
buffer[0] = 123;               // Set element
int value = buffer[0];         // Get element
```

### Type Casting
```impala
int x = (int) global params[0];         // Cast to int
float f = itof(x);                      // int to float
int i = ftoi(f);                        // float to int
pointer p = &buffer[0];                 // Address of array element
```

## Constants and Variables

### Constants
```impala
const int BUFFER_SIZE = 1024            // Integer constant
const float PI = 3.14159265             // Float constant
const int FALSE = 0                     // Boolean constant
const int TRUE = 1                      // Boolean constant
```

### Variable Declarations
```impala
// Local variables
int sampleCount
float delayTime = 0.5
array tempBuffer[64]

// Global variables (accessible across functions)
global int position = 0
global array circularBuffer[2048]
global float mixLevel

// Read-only global data
readonly array sineTable[1024] = { /* data */ }
readonly int maxDelay = 8000
```

## Operators

### Arithmetic Operators
```impala
int a = 10 + 5;        // Addition
int b = 10 - 5;        // Subtraction  
int c = 10 * 5;        // Multiplication
int d = 10 / 5;        // Division
int e = 10 % 3;        // Modulo
```

### Bitwise Operators
```impala
int a = 0xFF & 0x0F;   // Bitwise AND
int b = 0xFF | 0x0F;   // Bitwise OR
int c = 0xFF ^ 0x0F;   // Bitwise XOR
int d = ~0xFF;         // Bitwise NOT
int e = 0xFF << 2;     // Left shift
int f = 0xFF >> 2;     // Right shift
```

### Comparison Operators
```impala
if (a == b) { }        // Equal
if (a != b) { }        // Not equal
if (a < b) { }         // Less than
if (a <= b) { }        // Less than or equal
if (a > b) { }         // Greater than
if (a >= b) { }        // Greater than or equal
```

### Logical Operators
```impala
if (a && b) { }        // Logical AND
if (a || b) { }        // Logical OR  
if (!a) { }            // Logical NOT
```

## Control Flow

### Conditional Statements
```impala
// Basic if statement
if (condition) {
    // statements
}

// If-else
if (condition) {
    // statements
} else {
    // statements
}

// If-else-if chain
if (condition1) {
    // statements
} else if (condition2) {
    // statements
} else {
    // statements
}
```

### Loops

#### For Loops
```impala
// Inclusive range (0, 1, 2, ..., n)
for (i = 0 to n) {
    // loop body
}

// With step (manual implementation)
for (i = 0; i < n; i = i + 2) {
    // loop body  
}
```

#### While Loops
```impala
while (condition) {
    // loop body
}

// Example
int i = 0;
while (i < 10) {
    // process
    i = i + 1;
}
```

#### Infinite Loops
```impala
loop {
    // Main processing loop
    // MUST include yield() for real-time processing
    yield();
}
```

## Functions

### Function Declaration
```impala
// Basic function
function myFunction() {
    // function body
}

// Function with parameters
function processSignal(int gain, float frequency) {
    // function body
}

// Function with return value
function calculateGain(int input) 
returns int output
{
    output = input * 2;
}

// Function with local variables
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
        // Process global signal[0] and signal[1]
        // Audio range: -2047 to 2047 (12-bit)
        
        yield();  // REQUIRED - return control to host
    }
}
```

#### Mod Patches
```impala
function operate1(int a)
returns int processed
{
    if ((int) global params[OPERATOR_1_PARAM_INDEX] == OPERATOR_1_MUL) {
        // Process global positions[0] and positions[1]
        // Return 1 if handled, 0 to pass through
        processed = 1;
    } else {
        processed = 0;
    }
}

function operate2(int a)
returns int processed
{
    // Similar to operate1 for second operator
    processed = 0;  // Pass through by default
}
```

### Optional Callback Functions
```impala
function init() {
    // Called once when firmware loads
    // Initialize lookup tables, state, etc.
}

function reset() {
    // Called on reset button or DAW reset
    // Clear delays, reset state
}

function update() {
    // Called when parameters change
    // Recalculate derived values
}
```

## Built-in Functions

### Audio Processing
```impala
// Memory operations (delay lines)
read(int offset, int frameCount, pointer buffer)
write(int offset, int frameCount, pointer buffer)

// Control flow
yield()                 // Return control to host (required in loops)
abort()                 // Kill firmware, restore normal operation
```

### Debug Functions
```impala
trace(pointer string)   // Output debug string to console
```

### Math Functions
```impala
// Basic math (from source examples)
float cos(float x)      // Cosine (if available)
float sin(float x)      // Sine (if available)
float abs(float x)      // Absolute value
float floor(float x)    // Floor function
```

## Global Variables and APIs

### Always Available
```impala
global array params[PARAM_COUNT]        // Parameter values (0-255)
global array displayLEDs[4]            // LED displays (8-bit masks)
global int clock                       // Sample counter (0-65535)
global int instance                    // Unique plugin instance ID
```

### Full Patches Only
```impala
global array signal[2]                 // Audio I/O: [left, right]
                                       // Range: -2047 to 2047 (12-bit)
```

### Mod Patches Only
```impala
global array positions[2]              // Memory positions: [left, right]
                                       // Range: 0x00000 to 0xFFFFF (20-bit fixed point)
```

### Parameter Access
```impala
// Use predefined constants (externally defined)
int knob1 = (int) global params[OPERAND_1_HIGH_PARAM_INDEX];
int knob2 = (int) global params[OPERAND_1_LOW_PARAM_INDEX];
int switches = (int) global params[SWITCHES_PARAM_INDEX];

// Switch testing
if ((int) global params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK) {
    // Sync is enabled
}
```

## Memory Management

### Static Allocation Only
```impala
// All memory must be declared at compile time
global array largeBuffer[16384]    // Global storage
array tempBuffer[64]               // Local storage (function scope)

// NO dynamic allocation - these don't exist:
// malloc(), free(), new, delete
```

### Memory Access Patterns
```impala
// Safe array access
array buffer[1024];
int index = 0;
if (index >= 0 && index < 1024) {
    buffer[index] = value;  // Safe
}

// Circular buffer pattern
global int writePos = 0;
global array circularBuffer[1024];

writePos = (writePos + 1) % 1024;   // Wrap around
circularBuffer[writePos] = newValue;
```

## Real-time Considerations

### Cooperative Multitasking
```impala
function process() {
    loop {
        // Process one sample or small batch
        
        yield();  // REQUIRED - return control regularly
    }
}
```

### Performance Guidelines
```impala
// Prefer integer operations for speed
int sample = (int) global signal[0];
sample = sample >> 1;  // Fast divide by 2
global signal[0] = sample;

// Use lookup tables for expensive calculations
readonly array expTable[256] = { /* precomputed values */ };
int result = expTable[input & 0xFF];
```

## Common Patterns

### Parameter Scaling
```impala
// Map 0-255 parameter to useful range
int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 5) + 1;  // 1-8
float gain = itof((int) global params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;  // 0.0-1.0
int delay = (int) global params[OPERAND_1_HIGH_PARAM_INDEX] << 3;  // 0-2040
```

### Audio Range Clamping
```impala
// Ensure audio stays in valid range
if (sample > 2047) sample = 2047;
else if (sample < -2047) sample = -2047;
```

### LED Display
```impala
// Set LED patterns (8-bit mask, bit 0 = leftmost LED)
global displayLEDs[0] = 0x01;           // Single LED left
global displayLEDs[0] = 0x80;           // Single LED right  
global displayLEDs[0] = 0xFF;           // All LEDs on
global displayLEDs[0] = 1 << position;  // Variable position
```

### Delay Line Access
```impala
// Read/write delay memory
array buffer[2];  // Stereo pair

// Write current sample to delay line
write(global clock, 1, global signal);

// Read delayed sample
read(global clock - delayTime, 1, buffer);
int delayedLeft = buffer[0];
int delayedRight = buffer[1];
```

## Comments
```impala
// Single line comment

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
// No exceptions - use return values and defensive programming
function safeDivide(int a, int b)
returns int result
{
    if (b != 0) {
        result = a / b;
    } else {
        result = 0;  // Safe default
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

global array signal[2]              // Audio I/O
global array params[PARAM_COUNT]    // Parameters
global array displayLEDs[4]        // LED displays

function process() {
    loop {
        // Get bit depth from first knob (1-12 bits)
        int bits = ((int) global params[OPERAND_1_HIGH_PARAM_INDEX] >> 4) + 1;
        
        // Create bit mask for quantization
        int mask = 0xFFF0 << (12 - bits);
        
        // Apply bit crushing to both channels
        global signal[0] = (int) global signal[0] & mask;
        global signal[1] = (int) global signal[1] & mask;
        
        // Show bit depth on LEDs
        global displayLEDs[0] = (1 << bits) - 1;
        
        yield();  // Return control to host
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