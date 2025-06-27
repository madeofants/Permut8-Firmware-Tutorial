# Standard Library Reference

## Overview

The Impala language provides essential native functions and mathematical operations optimized for real-time audio processing on Permut8 firmware. This reference documents all available built-in functions, their usage patterns, and practical applications in firmware development.

Impala focuses on real-time safety with static allocation, cooperative multitasking, and direct hardware integration for professional audio processing.

## Native Functions

### Memory Operations

Essential functions for delay line and audio buffer management:

```impala

const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


read(int offset, int frameCount, pointer buffer)


write(int offset, int frameCount, pointer buffer)

```

**Delay Line Example:**
```impala
global array signal[2]
global array delayBuffer[2]

function process() {
    loop {

        write(global clock, 1, global signal)
        

        read(global clock - 1000, 1, delayBuffer)
        

        global signal[0] = (global signal[0] + delayBuffer[0]) >> 1
        global signal[1] = (global signal[1] + delayBuffer[1]) >> 1
        
        yield()
    }
}
```

### Control Flow Functions

```impala

yield()


abort()
```

**Processing Loop Pattern:**
```impala
function process() {
    loop {

        global signal[0] = global signal[0] >> 1
        global signal[1] = global signal[1] >> 1
        
        yield()
    }
}
```

### Debug Functions

```impala

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

int result = a + b
int result = a - b
int result = a * b
int result = a / b
int result = a % b


int result = a & b
int result = a | b
int result = a ^ b
int result = ~a
int result = a << 2
int result = a >> 2
```

### Trigonometric Functions

Available floating-point math functions:

```impala

float cos(float x)
float sin(float x)
float tan(float x)
```

**Oscillator Example:**
```impala
const float TWO_PI = 6.28318530717958647692

global float phase = 0.0

function process() {
    loop {

        int sineOutput = ftoi(sin(phase) * 1000.0)
        
        global signal[0] = sineOutput
        global signal[1] = sineOutput
        

        phase = phase + TWO_PI * 440.0 / 48000.0
        if (phase > TWO_PI) phase = phase - TWO_PI
        
        yield()
    }
}
```

### Number Functions

```impala

int abs(int x)
float fabs(float x)


int min(int a, int b)
int max(int a, int b)
float fmin(float a, float b)
float fmax(float a, float b)
```

**Audio Clipping Example:**
```impala
function clipToRange(int sample) returns int clipped {
    clipped = max(-2047, min(2047, sample))
}
```

### Type Conversion

```impala

float itof(int x)
int ftoi(float x)
```

**Parameter Scaling Example:**
```impala
function update() {

    float knobValue = itof((int)global (int)global params[CLOCK_FREQ_PARAM_INDEX]) / 255.0
    

    int audioGain = ftoi(knobValue * 2047.0)
}
```

## String Operations

Basic string utilities for debugging and parameter display:

```impala

int strlen(pointer string)


pointer strcpy(pointer dest, pointer src)


pointer strcat(pointer dest, pointer src)


int strcmp(pointer str1, pointer str2)
```

**Debug Message Building:**
```impala
function debugParameterChange() {
    array message[64]
    array valueStr[16]
    
    strcpy(message, "Param changed: ")


    strcat(message, valueStr)
    
    trace(message)
}
```

## Memory Management

### Static Allocation Only

Impala uses static memory allocation - no dynamic allocation available:

```impala

global array largeBuffer[8192]
global int bufferPosition = 0


function processBuffer() {
    array tempBuffer[64]
    int localCounter
    

}
```

### Safe Array Access

Always validate array indices to prevent memory corruption:

```impala
function safeArrayAccess(array buffer[1024], int index, int value) {

    if (index >= 0 && index < 1024) {
        buffer[index] = value
    }
}


function circularAccess(array buffer[256], int position) returns int value {
    int safePosition = position % 256
    value = buffer[safePosition]
}
```

## Random Number Generation

Simple random number generation for audio effects:

```impala

global int randomSeed = 1

function simpleRandom() returns int randomValue {
    randomSeed = randomSeed * 1103515245 + 12345
    randomValue = (randomSeed >> 16) & 0x7FFF
}


function randomRange(int minVal, int maxVal) returns int result {
    int range = maxVal - minVal + 1
    result = minVal + (simpleRandom() % range)
}
```

**Noise Generator Example:**
```impala
function process() {
    loop {

        int noise = randomRange(-1000, 1000)
        

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

int half = input >> 1
int quarter = input >> 2
int double = input << 1


int scaledValue = (input * 256) >> 8
```

### Lookup Tables

Pre-compute expensive calculations for real-time performance:

```impala
global array sineTable[256]

function init() {

    int i
    for (i = 0 to 255) {
        float angle = itof(i) * TWO_PI / 256.0
        sineTable[i] = ftoi(sin(angle) * 2047.0)
    }
}

function fastSine(int phase) returns int result {
    int index = (phase >> 8) & 0xFF
    result = sineTable[index]
}
```

## Audio-Specific Utilities

### Parameter Scaling

Convert parameter values to useful audio ranges:

```impala

global array freqLookupTable[256]

function paramToFrequency(int paramValue) returns int frequency {

    if (paramValue >= 0 && paramValue <= 255) {
        frequency = freqLookupTable[paramValue]
    } else {
        frequency = 440
    }
}


global array gainLookupTable[256]

function paramToGain(int paramValue) returns int linearGain {

    if (paramValue >= 0 && paramValue <= 255) {
        linearGain = gainLookupTable[paramValue]
    } else {
        linearGain = 256
    }
}
```

### Audio Processing Helpers

```impala

function softClip(int input) returns int output {
    if (input > 1500) {
        output = 1500 + ((input - 1500) >> 2)
    } else if (input < -1500) {
        output = -1500 + ((input + 1500) >> 2)
    } else {
        output = input
    }
    

    if (output > 2047) output = 2047
    if (output < -2047) output = -2047
}


global int filterMemory = 0

function lowPass(int input, int cutoff) returns int filtered {

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