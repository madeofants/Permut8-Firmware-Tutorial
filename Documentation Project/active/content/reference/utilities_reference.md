# Utilities Reference

## What This Is
Essential utility functions for Permut8 firmware development. Includes native system functions, math operations, string handling, and debugging tools.

## Native Functions

### Memory Operations
```impala
read(int offset, int frameCount, pointer values)
write(int offset, int frameCount, pointer values)
```

**Read from delay memory:**
```impala
array buffer[2];  // For stereo pair
read(1000, 1, buffer);  // Read 1 frame at offset 1000
int leftSample = buffer[0];
int rightSample = buffer[1];
```

**Write to delay memory:**
```impala
array samples[2] = {signal[0], signal[1]};
write(clock, 1, samples);  // Write current samples at clock position
```

**Frame format:** Interleaved stereo (left, right, left, right...)  
**Range:** -2047 to 2047 (12-bit signed)  
**Auto-wrapping:** Offsets automatically wrap to delay line size

### Control Flow
```impala
yield()  // Return control to audio engine
abort()  // Kill firmware, restore normal operation
```

#### yield() - Real-time Cooperative Processing
**Purpose**: Returns control to the Permut8 audio engine while preserving function state.

**Real-time Behavior**:
- **Timing**: Must be called every sample period (≈20.8μs at 48kHz)
- **State preservation**: Local variables and function position maintained
- **Audio I/O**: `signal[]` array updated by hardware before next cycle
- **Parameter updates**: `params[]` array refreshed with current control/switch values

**Critical Usage Patterns**:
```impala
function process() {
    loop {
        // Process exactly one audio sample per yield
        signal[0] = processLeft(signal[0]);
        signal[1] = processRight(signal[1]);
        
        yield();  // REQUIRED: Return control every sample
    }
}

// WRONG: This will cause audio dropouts
function process() {
    int i;
    for (i = 0 to 1000) {
        // Processing 1000 samples without yield = 20ms gap!
        signal[0] = signal[0] >> 1;
        // yield(); // MISSING - audio engine will timeout
    }
}
```

**Performance Notes**:
- More efficient than function returns (preserves call stack)
- Enables infinite loops without stack overflow
- Essential for real-time audio processing constraints

#### abort() - Emergency Firmware Termination
**Purpose**: Immediately terminates firmware and restores default Permut8 operation.

**When to Use**:
- **Fatal errors**: Division by zero, array bounds violations
- **Emergency stop**: User safety in runaway feedback scenarios  
- **Development debugging**: Quick exit when testing dangerous code

**Usage Scenarios**:
```impala
function process() {
    // Safety check for runaway feedback
    if (signal[0] > 4000 || signal[0] < -4000) {
        trace("EMERGENCY: Audio overflow detected!");
        abort();  // Immediately stop firmware
    }
    
    // Emergency user override (both switches pressed)
    int switches = (int)params[SWITCHES_PARAM_INDEX];
    if ((switches & 0x03) == 0x03) {
        trace("User emergency stop activated");
        abort();  // User requested immediate stop
    }
    
    yield();
}

function safeDivide(float a, float b) 
returns float result {
    if ((b < SMALL_FLOAT && b > -SMALL_FLOAT)) {
        trace("ERROR: Division by zero prevented");
        abort();  // Terminate rather than crash
    }
    result = a / b;
}
```

**Post-abort Behavior**:
- Firmware immediately stops executing
- Permut8 returns to default parameter processing
- All audio routing restored to normal operation
- Plugin must be reloaded to restart custom firmware

### Debugging
```impala
trace(pointer string)  // Output debug message
```

#### trace() - Debug Output and Development Logging
**Purpose**: Outputs debug messages to Permut8 console for development and troubleshooting.

**Console Access**: 
- Open Permut8 plugin in DAW
- Use plugin interface to load firmware
- Trace messages appear in real-time console window

**Development Workflows**:

**1. Parameter Monitoring**:
```impala
function update() {
    array buffer[64];
    array message[128];
    
    // Monitor control changes
    strcpy(message, "Knob1=");
    strcat(message, intToString((int)params[OPERAND_1_HIGH_PARAM_INDEX], 10, 1, buffer));
    strcat(message, " Knob2=");
    strcat(message, intToString((int)params[OPERAND_1_LOW_PARAM_INDEX], 10, 1, buffer));
    trace(message);
}
```

**2. Audio Processing Debug**:
```impala
global int debugCounter = 0;

function process() {
    debugCounter = debugCounter + 1;
    
    // Trace every 4800 samples (10x per second at 48kHz)
    if ((debugCounter % 4800) == 0) {
        array msg[128];
        array temp[32];
        
        strcpy(msg, "L=");
        strcat(msg, intToString(signal[0], 10, 1, temp));
        strcat(msg, " R=");
        strcat(msg, intToString(signal[1], 10, 1, temp));
        trace(msg);
    }
    
    yield();
}
```

**3. State Machine Debugging**:
```impala
global int currentState = 0;
global int lastState = -1;

function process() {
    // Only trace on state changes
    if (currentState != lastState) {
        array stateMsg[64];
        array numBuf[16];
        
        strcpy(stateMsg, "State change: ");
        strcat(stateMsg, intToString(lastState, 10, 1, numBuf));
        strcat(stateMsg, " -> ");
        strcat(stateMsg, intToString(currentState, 10, 1, numBuf));
        trace(stateMsg);
        
        lastState = currentState;
    }
    
    yield();
}
```

**4. Error Condition Tracing**:
```impala
function checkAudioLevels() {
    if (signal[0] > 2047 || signal[0] < -2047) {
        trace("WARNING: Left channel clipping detected");
    }
    if (signal[1] > 2047 || signal[1] < -2047) {
        trace("WARNING: Right channel clipping detected");
    }
}

function validateParameters() {
    int switches = (int)params[SWITCHES_PARAM_INDEX];
    if (switches > 255) {
        trace("ERROR: Invalid switch parameter value");
        abort();
    }
}
```

**5. Performance Profiling**:
```impala
global int processingTime = 0;
global int maxProcessingTime = 0;

function process() {
    int startTime = clock;
    
    // Your processing code here
    doAudioProcessing();
    
    processingTime = clock - startTime;
    if (processingTime > maxProcessingTime) {
        maxProcessingTime = processingTime;
        array perfMsg[64];
        array timeBuf[16];
        
        strcpy(perfMsg, "New max processing time: ");
        strcat(perfMsg, intToString(maxProcessingTime, 10, 1, timeBuf));
        trace(perfMsg);
    }
    
    yield();
}
```

**Performance Considerations**:
- String operations in trace() can be expensive
- Use trace() sparingly in `process()` function
- Batch multiple values into single trace() call
- Consider using counters to limit trace frequency
- Remove trace() calls in production firmware for best performance

## Math Utilities

### ⚠️ Math Function Compatibility

**Advanced math functions may not be available in all Impala implementations:**
- `sin()`, `cos()`, `tan()` - Check availability, use lookup tables if needed
- `exp()`, `log()`, `sqrt()`, `pow()` - May require fixed-point alternatives
- For guaranteed compatibility, use integer math and lookup tables

### Trigonometric Functions
```impala
// These functions may not be available in basic Impala:
float cos(float x)    // Cosine - use lookup table alternative
float sin(float x)    // Sine - use lookup table alternative
float tan(float x)    // Tangent - use lookup table alternative
```

**Generate oscillator (compatible version):**
```impala
const int TWO_PI_SCALED = 6283;  // 2π * 1000 for fixed-point math
global int phase = 0;            // Integer phase 0-999

function process() {
    // Create triangle wave (guaranteed to work)
    int sineOut;
    if (phase < 500) {
        sineOut = (phase * 4094) / 500 - 2047;  // Rising edge
    } else {
        sineOut = 2047 - ((phase - 500) * 4094) / 500;  // Falling edge
    }
    
    signal[0] = sineOut;
    signal[1] = sineOut;
    
    // Advance phase (440Hz at 48kHz approximation)
    phase += 9;  // Approximation for 440Hz
    if (phase >= 1000) phase = 0;
    
    yield();
}
```

### Exponential and Logarithmic
```impala
// These functions may not be available in basic Impala:
float exp(float x)     // e^x - use fixed-point approximation
float log(float x)     // Natural log - use lookup table
float log2(float x)    // Base-2 log - use lookup table
float log10(float x)   // Base-10 log - use lookup table
float pow(float x, float y) // x^y - use repeated multiplication
float sqrt(float x)    // Square root - use approximation
```

**Exponential envelope (compatible version):**
```impala
global int envelope = 1000;  // Fixed-point: 1000 = 1.0

function process() {
    // Fixed-point exponential decay approximation
    envelope = (envelope * 999) >> 10;  // Decay rate approximation
    
    int enveloped = (signal[0] * envelope) >> 10;
    signal[0] = enveloped;
    signal[1] = enveloped;
    
    yield();
}
```

### Number Manipulation
```impala
// These functions may not be available in basic Impala:
float floor(float x)   // Round down - use integer division
float ceil(float x)    // Round up - use integer math
float round(float x)   // Round to nearest - use (x + 0.5) cast
float trunc(float x)   // Remove fractional part - use ftoi()
float fmod(float x, float y) // Floating point modulo - use % operator
```

**Quantize to steps:**
```impala
float quantize(float input, int steps) {
    return round(input * itof(steps)) / itof(steps);
}

// Usage: quantize control to 8 steps
float controlValue = itof((int)params[OPERAND_1_HIGH_PARAM_INDEX]) / 255.0;
float stepped = quantize(controlValue, 8);
```

### Min/Max Functions
```impala
float minFloat(float a, float b)
float maxFloat(float a, float b)
int minInt(int a, int b)
int maxInt(int a, int b)
```

**Clipping:**
```impala
function clipSample(int sample) 
returns int clipped {
    clipped = maxInt(-2047, minInt(2047, sample));
}
```

### Random Number Generation
```impala
int xorShiftRandom()  // Returns random integer
```

**Setup random seed:**
```impala
function init() {
    // Use instance for unique seed per plugin
    xorShiftRandomSeedX = instance * 1234567;
    xorShiftRandomSeedY = instance * 7654321;
}
```

**Random effects:**
```impala
function process() {
    // Random bit crushing
    int randomBits = (xorShiftRandom() & 0xFF) + 1;  // 1-256
    int reduction = 8 - (randomBits >> 5);           // 1-8 bits
    
    signal[0] = signal[0] >> reduction << reduction;
    signal[1] = signal[1] >> reduction << reduction;
    
    yield();
}
```

## String Utilities

### Basic String Operations
```impala
int strlen(pointer s)                    // String length
pointer strcpy(pointer dest, pointer src) // Copy string
pointer strcat(pointer dest, pointer src) // Concatenate
int strcmp(pointer s1, pointer s2)       // Compare strings
int strncmp(pointer s1, pointer s2, int n) // Compare n chars
pointer stpcpy(pointer dest, pointer src)  // Copy, return end pointer
```

### Number Conversion
```impala
pointer intToString(int i, int radix, int minLength, pointer buffer)
pointer floatToString(float f, int precision, pointer buffer)
pointer stringToFloat(pointer string, pointer result)
```

**Debug parameter values:**
```impala
function update() {
    array buffer[64];
    array message[128];
    
    strcpy(message, "Control 1: ");
    strcat(message, intToString((int)params[OPERAND_1_HIGH_PARAM_INDEX], 10, 1, buffer));
    trace(message);
}
```

### Debug Tracing
```impala
void traceInt(pointer text, int value)
void traceInts(pointer text, int count, pointer values)
void traceFloat(pointer text, float value)  
void traceFloats(pointer text, int count, pointer values)
void error(pointer message)  // Trace message and abort
```

**Trace arrays:**
```impala
function update() {
    traceInts("All params: ", PARAM_COUNT, params);
    traceFloat("Current gain: ", currentGain);
}
```

## Integer Math Alternatives

### Safe Utility Functions
For guaranteed compatibility, use these integer-based implementations:

```impala
// Integer absolute value
function intAbs(int value) returns int result {
    if (value < 0) {
        result = -value;
    } else {
        result = value;
    }
}

// Integer square root approximation
function intSqrt(int x) returns int result {
    if (x <= 1) return x;
    
    int guess = x >> 1;  // Start with x/2
    int i;
    for (i = 0 to 8) {  // 8 iterations for convergence
        guess = (guess + x / guess) >> 1;
    }
    result = guess;
}

// Fixed-point sine approximation (input: 0-999, output: -1000 to 1000)
function intSine(int angle) returns int result {
    angle = angle % 1000;  // Wrap to 0-999
    
    if (angle < 250) {  // 0-90 degrees
        result = (angle * 4000) / 250;  // Linear approximation
    } else if (angle < 500) {  // 90-180 degrees
        result = 1000 - ((angle - 250) * 4000) / 250;
    } else if (angle < 750) {  // 180-270 degrees
        result = -((angle - 500) * 4000) / 250;
    } else {  // 270-360 degrees
        result = -1000 + ((angle - 750) * 4000) / 250;
    }
}
```

## Lookup Tables

### Exponential Response Tables
```impala
readonly array EIGHT_BIT_EXP_TABLE[256] = { /* 256 values */ };
readonly array SEVEN_BIT_EXP_TABLE[128] = { /* 128 values */ };
```

**These provide the same exponential curves used by built-in Permut8 operators.**

**Exponential parameter scaling:**
```impala
function update() {
    int controlRaw = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int expValue = (int)EIGHT_BIT_EXP_TABLE[controlRaw];
    
    // expValue now ranges from 0x0 to 0xFFFF with exponential curve
    global delayTime = expValue;
    
    // LED feedback shows exponential response
    displayLEDs[0] = expValue >> 8;  // High byte for LED display
}
```

**7-bit version for finer control:**
```impala
function update() {
    int knobRaw = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int index = knobRaw >> 1;  // Convert 8-bit to 7-bit index
    int expValue = (int)SEVEN_BIT_EXP_TABLE[index];
    
    global feedbackAmount = expValue;
}
```

## Mathematical Constants

```impala
// Fixed-point mathematical constants (scaled by 1000)
const int LOG2_SCALED = 693;           // ln(2) * 1000
const int LOG2R_SCALED = 1443;         // 1/ln(2) * 1000
const int LOG10R_SCALED = 434;         // 1/ln(10) * 1000
const int E_SCALED = 2718;             // e * 1000
const int HALF_PI_SCALED = 1571;       // π/2 * 1000
const int PI_SCALED = 3142;            // π * 1000
const int TWO_PI_SCALED = 6283;        // 2π * 1000
const int COS_EPSILON_SCALED = 1;      // Small value for comparisons
```

```impala
// Fixed-point threshold constants
const int EPSILON_SCALED = 1;          // Smallest comparison value
const int SMALL_SCALED = 10;           // Small threshold * 1000000
const int LARGE_SCALED = 10000000;     // Large threshold scaled
const int HUGE_SCALED = 2000000000;    // Large integer value
```

## Performance Tips

### Efficient Cosine Tables
```impala
const int COS_TABLE_BITS = 10;
const int COS_TABLE_SIZE = (1 << COS_TABLE_BITS);
global array cosTable[COS_TABLE_SIZE + 1];

function init() {
    int i;
    for (i = 0 to COS_TABLE_SIZE) {
        cosTable[i] = ftoi(cos((TWO_PI_SCALED / itof(COS_TABLE_SIZE * 1000)) * itof(i)) * 2047.0);
    }
    cosTable[COS_TABLE_SIZE] = cosTable[0];  // Wrap for interpolation
}

function fastCos(int phase) 
returns int result {
    int index = phase >> (16 - COS_TABLE_BITS);
    int fract = phase & ((1 << (16 - COS_TABLE_BITS)) - 1);
    int c0 = cosTable[index];
    int c1 = cosTable[index + 1];
    
    result = c0 + (((c1 - c0) * fract) >> (16 - COS_TABLE_BITS));
}
```

### Batch String Operations
```impala
function buildStatusMessage(array buffer[256]) {
    pointer p = buffer;
    
    p = stpcpy(p, "Delay: ");
    p = stpcpy(p, intToString(currentDelay, 10, 1, tempBuffer));
    p = stpcpy(p, " Feedback: ");
    p = stpcpy(p, floatToString(currentFeedback, 2, tempBuffer));
    
    trace(buffer);
}
```

### Error Handling
```impala
function safeDivide(float a, float b) 
returns float result {
    if ((b < SMALL_FLOAT && b > -SMALL_FLOAT)) {
        error("Division by zero detected");
    }
    result = a / b;
}
```

## Common Patterns

### Parameter-Driven Oscillator (Compatible Version)
```impala
global int oscPhase = 0;
global int oscFreq = 9;  // Frequency increment

function update() {
    // Convert control to frequency increment (1Hz - 1000Hz)
    int freqIndex = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int expValue = (int)EIGHT_BIT_EXP_TABLE[freqIndex];
    oscFreq = 1 + (expValue >> 7);  // Scale to 1-500 increment range
}

function process() {
    // Generate triangle wave
    int oscOut;
    if (oscPhase < 500) {
        oscOut = (oscPhase * 4094) / 500 - 2047;
    } else {
        oscOut = 2047 - ((oscPhase - 500) * 4094) / 500;
    }
    
    signal[0] = (signal[0] + oscOut) >> 1;  // Mix with input
    signal[1] = (signal[1] + oscOut) >> 1;
    
    oscPhase += oscFreq;
    if (oscPhase >= 1000) oscPhase -= 1000;
    
    yield();
}
```

### Random Modulation (Compatible Version)
```impala
global int randomCounter = 0;
global int currentRandom = 256;  // Fixed-point: 256 = 1.0

function process() {
    // Update random value every 1000 samples
    randomCounter = randomCounter + 1;
    if (randomCounter >= 1000) {
        randomCounter = 0;
        currentRandom = (xorShiftRandom() & 0xFF) + 1;  // 1-256 range
    }
    
    // Apply random modulation to input (fixed-point)
    signal[0] = (signal[0] * currentRandom) >> 8;
    signal[1] = (signal[1] * currentRandom) >> 8;
    
    yield();
}
```

## Key Points

- **Buffer sizes**: String buffers need adequate space (64-256 chars typical)
- **Compatibility**: Use integer math for guaranteed compatibility across Impala implementations
- **Tables**: Pre-compute expensive operations (sin/cos) in lookup tables for performance
- **Float functions**: Verify availability before using advanced math functions
- **Error handling**: Always check for division by zero and domain errors
- **Tracing**: Use debug functions extensively during development
- **Seeding**: Initialize random seeds with unique values per instance