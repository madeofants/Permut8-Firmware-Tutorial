# Standard Library Reference

## Overview

The Impala language provides essential native functions and mathematical operations optimized for real-time audio processing on Permut8 firmware. This reference documents all available built-in functions, their usage patterns, and practical applications in firmware development.

Impala focuses on real-time safety with static allocation, cooperative multitasking, and direct hardware integration for professional audio processing.

## Native Functions

### Memory Operations

Essential functions for delay line and audio buffer management:

```impala
// Read from delay memory
read(int offset, int frameCount, pointer buffer)

// Write to delay memory  
write(int offset, int frameCount, pointer buffer)
```

**Delay Line Example:**
```impala
global array signal[2]      // Audio I/O
global array delayBuffer[2] // For reading delay samples

function process() {
    loop {
        // Write current samples to delay line
        write(global clock, 1, global signal)
        
        // Read delayed samples (1000 samples ago)
        read(global clock - 1000, 1, delayBuffer)
        
        // Mix with delay
        global signal[0] = (global signal[0] + delayBuffer[0]) >> 1
        global signal[1] = (global signal[1] + delayBuffer[1]) >> 1
        
        yield()
    }
}
```

### Control Flow Functions

```impala
// Return control to audio engine (REQUIRED in processing loops)
yield()

// Kill firmware and restore normal operation
abort()
```

**Processing Loop Pattern:**
```impala
function process() {
    loop {
        // Process audio samples
        global signal[0] = global signal[0] >> 1  // Simple gain reduction
        global signal[1] = global signal[1] >> 1
        
        yield()  // CRITICAL: Return control to system
    }
}
```

### Debug Functions

```impala
// Output debug message to console
trace(pointer string)
```

**Debug Usage:**
```impala
function update() {
    trace("Parameters updated")
    trace("Control 1 value changed")
}
```

## Mathematical Operations

### Basic Arithmetic

Impala supports standard arithmetic with integer and floating-point operations:

```impala
// Integer arithmetic (preferred for performance)
int result = a + b       // Addition
int result = a - b       // Subtraction  
int result = a * b       // Multiplication
int result = a / b       // Division
int result = a % b       // Modulo

// Bitwise operations (very fast)
int result = a & b       // Bitwise AND
int result = a | b       // Bitwise OR
int result = a ^ b       // Bitwise XOR
int result = ~a          // Bitwise NOT
int result = a << 2      // Left shift (multiply by 4)
int result = a >> 2      // Right shift (divide by 4)
```

### Trigonometric Functions

Available floating-point math functions:

```impala
// Basic trigonometric functions
float cos(float x)       // Cosine function
float sin(float x)       // Sine function
float tan(float x)       // Tangent function
```

**Oscillator Example:**
```impala
const float TWO_PI = 6.28318530717958647692

global float phase = 0.0

function process() {
    loop {
        // Generate sine wave
        int sineOutput = ftoi(sin(phase) * 1000.0)
        
        global signal[0] = sineOutput
        global signal[1] = sineOutput
        
        // Advance phase for 440Hz at 48kHz sample rate
        phase = phase + TWO_PI * 440.0 / 48000.0
        if (phase > TWO_PI) phase = phase - TWO_PI
        
        yield()
    }
}
```

### Number Functions

```impala
// Absolute value
int abs(int x)           // Integer absolute value
float fabs(float x)      // Floating-point absolute value

// Min/max functions
int min(int a, int b)    // Minimum value
int max(int a, int b)    // Maximum value
float fmin(float a, float b)  // Float minimum
float fmax(float a, float b)  // Float maximum
```

**Audio Clipping Example:**
```impala
function clipToRange(int sample) returns int clipped {
    clipped = max(-2047, min(2047, sample))  // Clip to 12-bit audio range
}
```

### Type Conversion

```impala
// Convert between int and float
float itof(int x)        // Integer to float
int ftoi(float x)        // Float to integer (truncates)
```

**Parameter Scaling Example:**
```impala
function update() {
    // Convert 8-bit parameter (0-255) to float (0.0-1.0)
    float knobValue = itof((int)global params[0]) / 255.0
    
    // Convert to audio range
    int audioGain = ftoi(knobValue * 2047.0)
}
```

## String Operations

Basic string utilities for debugging and parameter display:

```impala
// String length
int strlen(pointer string)

// String copy
pointer strcpy(pointer dest, pointer src)

// String concatenation  
pointer strcat(pointer dest, pointer src)

// String comparison
int strcmp(pointer str1, pointer str2)
```

**Debug Message Building:**
```impala
function debugParameterChange() {
    array message[64]
    array valueStr[16]
    
    strcpy(message, "Param changed: ")
    // Convert parameter value to string representation
    // (Note: number-to-string conversion depends on available utilities)
    strcat(message, valueStr)
    
    trace(message)
}
```

## Memory Management

### Static Allocation Only

Impala uses static memory allocation - no dynamic allocation available:

```impala
// Global arrays (allocated at compile time)
global array largeBuffer[8192]     // Global storage
global int bufferPosition = 0      // Global state

// Local arrays (function scope)
function processBuffer() {
    array tempBuffer[64]           // Local temporary storage
    int localCounter               // Local variable
    
    // All memory sizes must be known at compile time
}
```

### Safe Array Access

Always validate array indices to prevent memory corruption:

```impala
function safeArrayAccess(array buffer[1024], int index, int value) {
    // Bounds checking
    if (index >= 0 && index < 1024) {
        buffer[index] = value     // Safe access
    }
}

// Circular buffer with wraparound
function circularAccess(array buffer[256], int position) returns int value {
    int safePosition = position % 256  // Automatic wraparound
    value = buffer[safePosition]
}
```

## Random Number Generation

Simple random number generation for audio effects:

```impala
// Basic linear congruential generator
global int randomSeed = 1

function simpleRandom() returns int randomValue {
    randomSeed = randomSeed * 1103515245 + 12345
    randomValue = (randomSeed >> 16) & 0x7FFF  // 15-bit positive value
}

// Random value in range
function randomRange(int minVal, int maxVal) returns int result {
    int range = maxVal - minVal + 1
    result = minVal + (simpleRandom() % range)
}
```

**Noise Generator Example:**
```impala
function process() {
    loop {
        // Generate white noise
        int noise = randomRange(-1000, 1000)
        
        // Mix with input
        global signal[0] = (global signal[0] + noise) >> 1
        global signal[1] = (global signal[1] + noise) >> 1
        
        yield()
    }
}
```

## Performance Utilities

### Fixed-Point Arithmetic

Prefer integer operations for best performance:

```impala
// Use bit shifts instead of division/multiplication by powers of 2
int half = input >> 1        // Divide by 2
int quarter = input >> 2     // Divide by 4
int double = input << 1      // Multiply by 2

// Fixed-point scaling (8.8 format - 8 integer bits, 8 fractional bits)
int scaledValue = (input * 256) >> 8  // Multiply by 1.0 in 8.8 format
```

### Lookup Tables

Pre-compute expensive calculations for real-time performance:

```impala
global array sineTable[256]

function init() {
    // Pre-compute sine table during initialization
    int i
    for (i = 0 to 255) {
        float angle = itof(i) * TWO_PI / 256.0
        sineTable[i] = ftoi(sin(angle) * 2047.0)  // Scale to audio range
    }
}

function fastSine(int phase) returns int result {
    int index = (phase >> 8) & 0xFF  // Scale phase to table index
    result = sineTable[index]
}
```

## Audio-Specific Utilities

### Parameter Scaling

Convert parameter values to useful audio ranges:

```impala
// Scale 8-bit parameter to frequency range using lookup table
global array freqLookupTable[256]  // Pre-computed frequency values

function paramToFrequency(int paramValue) returns int frequency {
    // paramValue: 0-255 → frequency: 20Hz-20000Hz (logarithmic)
    if (paramValue >= 0 && paramValue <= 255) {
        frequency = freqLookupTable[paramValue]
    } else {
        frequency = 440  // Default frequency
    }
}

// Scale parameter to linear gain using lookup table
global array gainLookupTable[256]  // Pre-computed gain values

function paramToGain(int paramValue) returns int linearGain {
    // paramValue: 0-255 → gain: linear values from lookup table
    if (paramValue >= 0 && paramValue <= 255) {
        linearGain = gainLookupTable[paramValue]
    } else {
        linearGain = 256  // Default unity gain (scaled)
    }
}
```

### Audio Processing Helpers

```impala
// Soft clipping using integer approximation
function softClip(int input) returns int output {
    if (input > 1500) {
        output = 1500 + ((input - 1500) >> 2)  // Gentle compression above threshold
    } else if (input < -1500) {
        output = -1500 + ((input + 1500) >> 2)
    } else {
        output = input  // Linear region
    }
    
    // Hard limit to audio range
    if (output > 2047) output = 2047
    if (output < -2047) output = -2047
}

// Simple low-pass filter
global int filterMemory = 0

function lowPass(int input, int cutoff) returns int filtered {
    // cutoff: 0-255, higher values = more filtering
    int difference = input - filterMemory
    filterMemory = filterMemory + ((difference * cutoff) >> 8)
    filtered = filterMemory
}
```

## Best Practices

### Real-Time Safety
- **Use static allocation** - all array sizes known at compile time
- **Call yield() regularly** - in all processing loops
- **Prefer integer math** - faster than floating-point operations
- **Avoid complex algorithms** - keep processing predictable

### Performance Optimization
- **Use lookup tables** for expensive calculations (sin, exp, etc.)
- **Use bit shifts** instead of multiplication/division by powers of 2
- **Cache parameter values** - avoid repeated array access
- **Minimize function calls** in inner loops

### Memory Management
- **Initialize arrays** to known values in init() function
- **Validate array indices** before access
- **Use modulo arithmetic** for circular buffers
- **Group related data** together for cache efficiency

### Error Prevention
- **Always clip audio output** to valid range (-2047 to 2047)
- **Check for division by zero** in calculations
- **Validate parameter ranges** before use
- **Use trace() liberally** during development

---

*This reference covers the core Impala standard library functions available for Permut8 firmware development. For advanced patterns and examples, see the [Cookbook](../user-guides/cookbook/) and [Tutorials](../user-guides/tutorials/).*