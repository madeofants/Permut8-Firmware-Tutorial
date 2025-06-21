# Understanding Impala Language Fundamentals

**Master the foundation of Permut8 firmware development**

This comprehensive tutorial bridges the gap between general programming knowledge and Impala-specific concepts. Whether you're coming from C, JavaScript, Python, or any other language, this guide will teach you everything you need to understand Impala's unique approach to audio DSP programming.

## Required Parameter Constants
```impala
// Standard parameter index constants used throughout all examples
const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8
```

## What You'll Learn

By the end of this tutorial, you'll understand:
- How Impala differs from C and other languages
- Essential syntax and language constructs
- Memory model and real-time constraints
- Basic audio processing concepts
- How to structure a Permut8 firmware patch

**Prerequisites**: Basic programming experience in any language  
**Time Required**: 45-60 minutes  
**Difficulty**: Beginner to Intermediate

## Chapter 1: Language Overview and Philosophy

### Impala's Design Goals

Impala is specifically designed for **real-time audio processing** on embedded hardware. Unlike general-purpose programming languages, every feature is optimized for:

1. **Predictable timing** - No malloc/free, no garbage collection
2. **Audio-first design** - Built-in audio types and processing constructs  
3. **Hardware integration** - Direct mapping to Permut8's capabilities
4. **Safety** - Prevent common real-time audio bugs

### Key Differences from C

If you know C, here are the major differences:

| Feature | C | Impala |
|---------|---|---------|
| **Memory Management** | malloc/free available | Static allocation only |
| **Preprocessor** | #include, #define | No preprocessor |
| **Function Pointers** | Supported | Not available |
| **Loops** | for, while, do-while | `loop` construct + for/while |
| **Real-time Support** | Manual | Built-in `yield()` |
| **Audio Types** | Manual scaling | 12-bit audio range |

```impala
// C style (NOT valid in Impala)
#include <stdio.h>
float* buffer = malloc(1024 * sizeof(float));

// Impala style  
const int BUFFER_SIZE = 1024
global array buffer[BUFFER_SIZE]
```

## Chapter 2: Basic Syntax and Data Types

### Variables and Constants

Impala uses explicit type declarations with clear scoping:

```impala
// Constants (compile-time values)
const int SAMPLE_RATE = SAMPLE_RATE_44K1
const int BUFFER_SIZE = 512
const int MAX_VOLUME = AUDIO_MAX

// Global variables (persistent across function calls)
global int currentPhase = 0
global int amplitude = 1000

// Local variables (function scope)
function processAudio()
locals tempValue, result
{
    tempValue = global currentPhase * 2
    result = tempValue + 100
    return result
}
```

### Data Types

Impala keeps it simple with essential types:

```impala
// Integer types  
wholeNumber = 42          // 32-bit signed integer (declare in locals)
const int MAX_VALUE = AUDIO_MAX    // Constants are always int

// Arrays (fixed size, no dynamic allocation)
global array audioBuffer[1024]    // Global array
locals array tempBuffer[256]      // Local array (in function)

// No floating point in basic Impala
// Use integer math with scaling instead:
scaledValue = (input * 1000) / 255  // Simulate 0.0-1.0 range (declare in locals)
```

### Essential Operators

```impala
// Arithmetic
sum = a + b          // Variables declared in locals
difference = a - b  
product = a * b
quotient = a / b
remainder = a % b

// Bitwise operations (important for audio processing)
shifted = value << 2      // Left shift (multiply by 4)
masked = value & 0xFF     // Keep only lower 8 bits
combined = a | b          // Bitwise OR

// Comparison
if (a == b) { }              // Equal
if (a != b) { }              // Not equal
if (a < b) { }               // Less than
if (a >= b) { }              // Greater than or equal

// Logical
if (a && b) { }              // Logical AND
if (a || b) { }              // Logical OR
if (!a) { }                  // Logical NOT
```

## Chapter 3: Functions and Control Flow

### Function Declaration

Impala functions are explicit about their inputs, outputs, and local variables:

```impala
// Basic function
function calculateGain(inputLevel, maxLevel)
returns outputGain
locals scaledLevel, result
{
    scaledLevel = inputLevel * 1000 / maxLevel
    result = scaledLevel + 100
    return result
}

// Function with no return value
function resetState()
locals i
{
    global currentPhase = 0
    for (i = 0 to 1023) {
        global audioBuffer[i] = 0
    }
}

// Function with multiple return values
function processFilter(input)
returns lowpass, highpass
locals temp
{
    temp = input / 2
    lowpass = temp
    highpass = input - temp
}
```

### Control Flow Constructs

#### The `loop` Construct (Unique to Impala)

The most important construct for real-time audio:

```impala
function process()
{
    loop {
        // This runs forever, processing one audio sample per iteration
        
        // Get input audio
        inputLeft = global signal[0]
        inputRight = global signal[1]
        
        // Process audio
        outputLeft = inputLeft * global amplitude / 1000
        outputRight = inputRight * global amplitude / 1000
        
        // Set output audio
        global signal[0] = outputLeft
        global signal[1] = outputRight
        
        // CRITICAL: Return control to host
        yield()
    }
}
```

#### Traditional Loops

```impala
// For loops (inclusive range)
for (i = 0 to 9) {
    global buffer[i] = i * 10
}

// For loops (exclusive range)  
for (i = 0 to< 10) {
    global buffer[i] = i * 10
}

// While loops
while (global phase < AUDIO_FULL_RANGE) {
    global phase = global phase + global increment
    // Process sample
}

// Conditional statements
if (input > 1000) {
    output = 1000  // Limit output
} else if (input < -1000) {
    output = -1000
} else {
    output = input
}
```

## Chapter 4: Memory Model and Real-Time Constraints

### Static Memory Only

Unlike C, Impala uses **only static memory allocation**:

```impala
// GOOD: Static allocation
global array delayBuffer[SAMPLE_RATE_44K1]    // 1 second delay at 44.1kHz
const int BUFFER_SIZE = 1024

// BAD: Dynamic allocation (not available in Impala)
// buffer = malloc(size * sizeof(int))  // This doesn't exist!
```

### Global vs Local Variables

Understanding scope is crucial for real-time performance:

```impala
// Global variables persist between function calls
global int oscillatorPhase = 0      // Keeps state between audio samples
global array filterHistory[4]       // Persistent filter memory

function process()
locals inputSample, outputSample  // Created fresh each call
{
    inputSample = global signal[0]
    
    // Modify global state
    global oscillatorPhase = global oscillatorPhase + 1000
    
    // Use global state
    outputSample = global filterHistory[0] + inputSample
    
    global signal[0] = outputSample
    yield()
}
```

### Memory Access Patterns

Efficient memory access is critical for real-time audio:

```impala
// GOOD: Sequential access
for (i = 0 to 1023) {
    global buffer[i] = global buffer[i] * gain
}

// GOOD: Predictable patterns
int readPos = global writePos - global delayTime
if (readPos < 0) readPos = readPos + BUFFER_SIZE

// AVOID: Complex indirect addressing when possible
// Complex calculations can cause audio dropouts
```

## Chapter 5: Audio-Specific Concepts

### 12-Bit Audio Range

Permut8 uses 12-bit audio with range **-AUDIO_MAX to +AUDIO_MAX**:

```impala
// Audio sample range
const int AUDIO_MIN = -AUDIO_MAX
const int AUDIO_MAX = AUDIO_MAX
const int AUDIO_ZERO = 0

// Safe gain application
function applyGain(sample, gainPercent)
returns result
locals scaled
{
    // gainPercent: 0-255 represents 0% to 100%
    scaled = sample * gainPercent / 255
    
    // Clamp to valid range
    if (scaled > AUDIO_MAX) scaled = AUDIO_MAX
    if (scaled < AUDIO_MIN) scaled = AUDIO_MIN
    
    return scaled
}
```

### Parameter Range (0-255)

Permut8 knobs provide values from 0 to 255:

```impala
// Parameter scaling examples
function scaleToGain(param)
returns gain
{
    // Linear scaling: 0-255 → 0-1000 (0% to 100%)
    gain = param * 1000 / 255
}

function scaleToFrequency(param)  
returns frequency
{
    // Logarithmic scaling: 0-255 → 20Hz to 20kHz
    // Using lookup table or approximation
    if (param == 0) return 20
    if (param == 255) return 20000
    
    // Simple exponential approximation
    return 20 + (param * param * 78) / 255  // Rough curve
}
```

### The `yield()` Function

**Most important concept**: `yield()` returns control to the host system:

```impala
// Required native function declaration
extern native yield

function process()
{
    loop {
        // Process ONE audio sample here
        
        int input = global signal[0]
        int output = input * 2  // Simple amplification
        global signal[0] = output
        
        // MUST call yield() to return control
        yield()  // Host will call us again for next sample
    }
}
```

**Why yield() matters**:
- Permut8 processes audio one sample at a time
- `yield()` lets the host handle timing and scheduling
- Missing `yield()` = audio dropouts and system freeze
- Call `yield()` exactly once per audio sample

## Chapter 6: Essential Native Functions

Impala provides built-in functions for Permut8 integration:

### Audio Processing Natives

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

// Required native function declarations
extern native yield
extern native read
extern native write

// Example: Simple delay effect
function createDelay()
locals delayTime, array inputBuffer[2], array outputBuffer[2]
{
    delayTime = SAMPLE_RATE_HALF  // 0.5 second delay at 44.1kHz
    
    loop {
        // Read current input
        inputBuffer[0] = global signal[0]
        inputBuffer[1] = global signal[1]
        
        // Write input to delay line
        write(global clock, 1, inputBuffer)
        
        // Read delayed audio
        read(global clock - delayTime, 1, outputBuffer)
        
        // Mix with input (50/50)
        global signal[0] = (inputBuffer[0] + outputBuffer[0]) / 2
        global signal[1] = (inputBuffer[1] + outputBuffer[1]) / 2
        
        yield()
    }
}
```

### Debug and Utility Natives

```impala
// Debug output (use sparingly - can affect timing)
trace("Debug message")

// Emergency stop (debugging only)
abort()  // Stops firmware execution
```

## Chapter 7: Permut8 Firmware Structure

### Required Components

Every Permut8 firmware patch needs these elements:

```impala
// 1. REQUIRED: Firmware format declaration
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// 2. REQUIRED: Audio input/output
global array signal[2]  // [left, right] audio samples

// 3. REQUIRED: Parameter access  
global array params[PARAM_COUNT]  // Knob values (0-255)

// 4. REQUIRED: LED display
global array displayLEDs[4]  // LED control arrays

// 5. REQUIRED: Main processing function
function process()
{
    loop {
        // Your audio processing here
        yield()
    }
}
```

### Optional Components

```impala
// Optional: Initialization
function init()
{
    // Called once when firmware loads
    global amplitude = 1000
    trace("Firmware initialized")
}

// Optional: Parameter change notification
function update()
{
    // Called when knobs change
    global amplitude = global params[OPERAND_2_HIGH_PARAM_INDEX] * 4  // Scale 0-255 to 0-1020
}

// Optional: Reset notification
function reset()
{
    // Called when reset button pressed
    global oscillatorPhase = 0
}
```

### Complete Minimal Example

Here's a complete, working Permut8 firmware:

```impala
// === SIMPLE AMPLIFIER FIRMWARE ===
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declaration
extern native yield

// Required globals
global array signal[2]
global array params[PARAM_COUNT] 
global array displayLEDs[4]
global clock = 0
global clockFreqLimit = 0

// Our state
global int amplification = 1000

function update()
{
    // Scale knob 0 (0-255) to amplification (0-2000)  
    global amplification = global params[OPERAND_1_HIGH_PARAM_INDEX] * 8
    
    // Show amplification on LEDs
    global displayLEDs[0] = global params[OPERAND_1_HIGH_PARAM_INDEX]
}

function process()
locals inputLeft, inputRight, outputLeft, outputRight
{
    loop {
        // Get input samples
        inputLeft = global signal[0]
        inputRight = global signal[1]
        
        // Apply amplification
        outputLeft = inputLeft * global amplification / 1000
        outputRight = inputRight * global amplification / 1000
        
        // Clamp to valid range
        if (outputLeft > AUDIO_MAX) outputLeft = AUDIO_MAX
        if (outputLeft < -AUDIO_MAX) outputLeft = -AUDIO_MAX
        if (outputRight > AUDIO_MAX) outputRight = AUDIO_MAX
        if (outputRight < -AUDIO_MAX) outputRight = -AUDIO_MAX
        
        // Set output
        global signal[0] = outputLeft
        global signal[1] = outputRight
        
        yield()
    }
}
```

## Chapter 8: Common Patterns and Best Practices

### Pattern 1: Parameter Scaling

```impala
// Linear scaling (0-255 to any range)
function scaleLinear(param, minValue, maxValue)
returns scaled
{
    scaled = minValue + (param * (maxValue - minValue) / 255)
}

// Example usage
function update()
{
    // Map knob to frequency range 100Hz-5000Hz
    global frequency = scaleLinear(global params[OPERAND_2_HIGH_PARAM_INDEX], 100, 5000)
    
    // Map knob to gain 0%-200%  
    global gainPercent = scaleLinear(global params[OPERAND_2_LOW_PARAM_INDEX], 0, 200)
}
```

### Pattern 2: Circular Buffer Management

```impala
global int writePosition = 0
const int BUFFER_SIZE = 1024

function writeToCircularBuffer(value)
{
    global audioBuffer[global writePosition] = value
    global writePosition = global writePosition + 1
    if (global writePosition >= BUFFER_SIZE) {
        global writePosition = 0  // Wrap around
    }
}

function readFromCircularBuffer(offset)
returns value
locals readPos
{
    readPos = global writePosition - offset
    if (readPos < 0) {
        readPos = readPos + BUFFER_SIZE  // Handle wraparound
    }
    return global audioBuffer[readPos]
}
```

### Pattern 3: Safe Audio Processing

```impala
// Always clamp audio to valid range
function clampAudio(sample)
returns clamped
{
    if (sample > AUDIO_MAX) return AUDIO_MAX
    if (sample < -AUDIO_MAX) return -AUDIO_MAX
    return sample
}

// Safe gain application
function applyGainSafe(sample, gain)
returns result
{
    result = sample * gain / 1000
    return clampAudio(result)
}
```

### Pattern 4: LED Feedback

```impala
function updateLEDDisplay()
locals level, ledMask, i
{
    // Create level meter from audio amplitude
    level = abs(global signal[0]) / 256  // 0-8 range
    
    // Build LED mask
    ledMask = 0
    for (i = 0 to level) {
        ledMask = ledMask | (1 << i)  // Turn on LED i
    }
    
    global displayLEDs[0] = ledMask
}
```

## Chapter 9: Common Mistakes and How to Avoid Them

### Mistake 1: Forgetting yield()

```impala
// WRONG: Will freeze the system
function process()
{
    loop {
        global signal[0] = global signal[0] * 2
        // Missing yield() - this loops forever without returning control!
    }
}

// CORRECT: Always yield once per sample
function process()
{
    loop {
        global signal[0] = global signal[0] * 2
        yield()  // Return control to host
    }
}
```

### Mistake 2: Audio Range Overflow

```impala
// WRONG: Can overflow audio range
function process()
{
    loop {
        global signal[0] = global signal[0] * 10  // Might exceed ±AUDIO_MAX!
        yield()
    }
}

// CORRECT: Always clamp results
function process()
locals result
{
    loop {
        result = global signal[0] * 10
        if (result > AUDIO_MAX) result = AUDIO_MAX
        if (result < -AUDIO_MAX) result = -AUDIO_MAX
        global signal[0] = result
        yield()
    }
}
```

### Mistake 3: Uninitialized Variables

```impala
// WRONG: Uninitialized globals have random values
global int filterState  // Could be any value!

function process()
{
    loop {
        global signal[0] = global signal[0] + global filterState  // Unpredictable!
        yield()
    }
}

// CORRECT: Always initialize
global int filterState = 0  // Known starting value

// Or initialize in init()
function init()
{
    global filterState = 0
}
```

### Mistake 4: Array Bounds

```impala
// WRONG: No bounds checking
global array buffer[1024]
global int index = 0

function process()
{
    loop {
        global buffer[global index] = global signal[0]  // Could exceed array!
        global index = global index + 1
        yield()
    }
}

// CORRECT: Always check bounds
function process()
{
    loop {
        global buffer[global index] = global signal[0]
        global index = global index + 1
        if (global index >= 1024) {
            global index = 0  // Wrap around safely
        }
        yield()
    }
}
```

## Chapter 10: Next Steps

Congratulations! You now understand Impala's fundamental concepts. Here's what to learn next:

### Immediate Next Steps

1. **Practice**: [QUICKSTART Tutorial](../QUICKSTART.md)
   - Get hands-on experience with your first working firmware
   - Build confidence with the compilation and loading process

2. **Read**: [Complete Development Workflow Tutorial](complete-development-workflow.md)
   - Learn the end-to-end development process
   - Understand compilation, testing, and debugging

3. **Practice**: Try the cookbook recipes
   - [Basic Filter](../cookbook/fundamentals/basic-filter.md) - Apply filtering concepts
   - [Basic Oscillator](../cookbook/fundamentals/basic-oscillator.md) - Generate audio signals
   - [Gain and Volume](../cookbook/fundamentals/gain-and-volume.md) - Master amplitude control

### Advanced Learning Path

4. **Advanced Optimization**: [Assembly Integration Guide](../../assembly/gazl-assembly-introduction.md)
   - Learn GAZL assembly for maximum performance
   - Advanced debugging and profiling techniques

5. **Complex Effects**: Explore cookbook categories
   - Audio effects for classic DSP algorithms
   - Spectral processing for frequency domain work
   - Parameter automation for dynamic control

### Development Resources

- **Language Reference**: [Core Language Reference](../../language/core_language_reference.md)
- **API Reference**: [Parameters Reference](../../reference/parameters_reference.md)
- **Architecture Guide**: [Memory Model](../../architecture/memory-model.md)

## Quick Reference Card

### Essential Syntax
```impala
const int CONSTANT = 42
global globalVar = 0  
locals localVar       // In function declaration

function myFunction(param)
returns result
{ }

loop { yield() }
for (i = 0 to 10) { }
if (condition) { } else { }
```

### Audio Essentials
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
global array signal[2]      // Audio I/O
global array params[PARAM_COUNT]  // Knobs (0-255)
global array displayLEDs[4]     // LED control

function process() {
    loop {
        // Process audio here
        yield()  // REQUIRED
    }
}
```

### Safe Patterns
```impala
// Clamp audio
if (sample > AUDIO_MAX) sample = AUDIO_MAX
if (sample < -AUDIO_MAX) sample = -AUDIO_MAX

// Scale parameters  
scaled = param * range / 255

// Circular buffer
index = (index + 1) % BUFFER_SIZE
```

---

You're now ready to create real Permut8 firmware! The language fundamentals you've learned here will be referenced throughout all other documentation and tutorials.

*Part of the Permut8 Foundation Tutorial Series*