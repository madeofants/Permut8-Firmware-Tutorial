# Official Firmware Patterns

Essential patterns extracted from Beatrick and FooBar official firmware for creating professional-quality Permut8 firmware.

## Overview

This guide contains real-world patterns from official Permut8 firmware. These patterns are battle-tested and represent best practices for parameter handling, memory management, and audio processing.

## Firmware Format Evolution

### Version 2 (Beatrick) - Standard Format
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
```
**Features**:
- 16-step sequencing maximum
- Basic parameter handling
- Standard memory operations
- Compatible with all Permut8 versions

### Version 3 (FooBar) - Advanced Format
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 3
```
**Features**:
- 32-step sequencing
- Host synchronization support
- Advanced random pattern generation
- Extended parameter handling
- Latest Permut8 firmware required

## Core Architecture Patterns

### Standard Memory Layout (Both Firmwares)
```impala
// Official pattern used in both Beatrick and FooBar
global array signal[2]       // Audio I/O [left, right]
global array params[PARAM_COUNT]  // Plugin parameters
global array displayLEDs[4]  // LED displays
global int clock = 0         // Clock counter

// Additional globals for advanced features
global int hostPosition = 0  // DAW sync (Version 3 only)
```

### Required Function Structure
```impala
// Official pattern - all firmware must implement
function reset() {
    // Initialize state, clear delays
    // Called when firmware loads or reset
}

function update() {
    // Handle parameter changes
    // Called when knobs/switches change
}

function process() {
    loop {
        // Main audio processing
        // Called every sample
        yield();
    }
}
```

## Parameter Handling Patterns

### Parameter Update Mask (Critical Pattern)
```impala
// Official pattern from both Beatrick and FooBar
const int updateMask = (
    (1 << OPERATOR_1_PARAM_INDEX) |
    (1 << OPERAND_1_HIGH_PARAM_INDEX) |
    (1 << OPERAND_1_LOW_PARAM_INDEX) |
    (1 << OPERATOR_2_PARAM_INDEX) |
    (1 << OPERAND_2_HIGH_PARAM_INDEX) |
    (1 << OPERAND_2_LOW_PARAM_INDEX)
);

// Usage in update() function
function update() {
    if (updateMask & (1 << OPERAND_1_HIGH_PARAM_INDEX)) {
        // Parameter changed, recalculate derived values
        recalculateEffectParameters();
    }
}
```

### Bit Manipulation for Parameter Packing
```impala
// Official pattern for combining high/low parameter bytes
function readCombinedParameter() 
returns int combined
{
    int high = (int) global params[OPERAND_1_HIGH_PARAM_INDEX];
    int low = (int) global params[OPERAND_1_LOW_PARAM_INDEX];
    combined = (high << 8) | low;  // 16-bit value (0-65535)
}

// Switch state reading
function readSwitchStates()
returns int switches
{
    switches = (int) global params[SWITCHES_PARAM_INDEX];
    int syncEnabled = (switches & SWITCHES_SYNC_MASK) != 0;
    int reverseEnabled = (switches & SWITCHES_REVERSE_MASK) != 0;
}
```

## Step Sequencing Patterns

### Beatrick Pattern (16 Steps)
```impala
// Official Beatrick sequencing pattern
const int STEP_COUNT = 16

global array steps[STEP_COUNT]     // Step data
global array gains[STEP_COUNT]     // Volume per step
global array holds[STEP_COUNT]     // Hold states
global array sfxs[STEP_COUNT]      // Effects per step

function processStepSequencer() {
    // Current step calculation
    int currentStep = (clock >> 8) & (STEP_COUNT - 1);
    
    // Lookahead processing (official pattern)
    const int LOOKAHEAD = 0x80;
    int lookaheadStep = ((clock + LOOKAHEAD) >> 8) & (STEP_COUNT - 1);
    
    // Read step data
    int stepData = steps[currentStep];
    int gain = gains[currentStep];
    int effect = sfxs[currentStep];
}
```

### FooBar Pattern (32 Steps + Randomization)
```impala
// Official FooBar advanced sequencing pattern
const int STEP_COUNT = 32

global array stepFXs[STEP_COUNT]   // Effects per step
global int randomSeed = 0          // Random generator state

function processAdvancedSequencer() {
    // Extended step calculation
    int currentStep = (clock >> 7) & (STEP_COUNT - 1);
    
    // Random pattern generation (official algorithm)
    function generateRandomPattern() {
        // Deterministic random based on parameter seed
        int seed = (int) global params[OPERAND_1_LOW_PARAM_INDEX];
        randomSeed = (randomSeed * 1103515245 + 12345) & 0x7FFFFFFF;
        randomSeed ^= seed;  // Parameter influence
    }
    
    // Host position sync (Version 3 only)
    if (hostPosition != 0) {
        // Sync with DAW transport
        currentStep = (hostPosition >> 10) & (STEP_COUNT - 1);
    }
}
```

## Audio Processing Patterns

### Interpolation for Smooth Effects
```impala
// Official pattern from both firmwares
function smoothParameterChange(int currentValue, int targetValue) 
returns int smoothedValue
{
    int difference = targetValue - currentValue;
    int smoothed = difference >> 5;  // Divide by 32 for smooth transition
    smoothedValue = currentValue + smoothed;
}

// Gain interpolation (Beatrick pattern)
global int currentGain = 0;
function processWithGainSmoothing() {
    int targetGain = gains[currentStep];
    currentGain = smoothParameterChange(currentGain, targetGain);
    
    // Apply smooth gain
    global signal[0] = (global signal[0] * currentGain) >> 8;
    global signal[1] = (global signal[1] * currentGain) >> 8;
}
```

### Effect Implementation Patterns

#### Beatrick Effects (Version 2)
```impala
// Official effect constants from Beatrick
const int NOP = 0;
const int MUTE = 1;
const int REPEAT = 2;
const int SKIP = 3;
const int HOLD = 4;
const int ACCENT = 1;      // Same ID, different context
const int STUTTER = 2;
const int REVERSE = 3;
const int TAPE_STOP = 4;

function processBeatrickEffects(int effect) {
    switch (effect) {
        case MUTE:
            global signal[0] = 0;
            global signal[1] = 0;
            break;
            
        case REPEAT:
            // Replay previous step data
            repeatPreviousStep();
            break;
            
        case HOLD:
            // Freeze and replay current audio slice
            holdCurrentSlice();
            break;
            
        case REVERSE:
            // Backward playback
            reversePlayback();
            break;
    }
}
```

#### FooBar Effects (Version 3)
```impala
// Official effect constants from FooBar
const int REVERSE_FX = 0;
const int BIT_CRUSH_EFFECT = 1;
const int TRANCE_GATE_EFFECT = 2;
const int REPEAT_EFFECT = 3;
const int STRETCH_EFFECT = 4;
const int PITCH_SHIFT_EFFECT = 5;
const int HALF_SPEED_EFFECT = 6;
const int TAPE_STOP_FX = 7;

function processFooBarEffects(int effect, int intensity) {
    switch (effect) {
        case BIT_CRUSH_EFFECT:
            // Bit reduction based on intensity
            int bits = 12 - (intensity >> 5);  // 12 to 4 bits
            int mask = 0xFFF0 << (12 - bits);
            global signal[0] &= mask;
            global signal[1] &= mask;
            break;
            
        case PITCH_SHIFT_EFFECT:
            // Pitch shifting with interpolation
            processPitchShift(intensity);
            break;
            
        case HALF_SPEED_EFFECT:
            // Time stretching
            processTimeStretch(intensity);
            break;
    }
}
```

## Memory Management Patterns

### Delay Line Operations (Official Pattern)
```impala
// Standard delay pattern from both firmwares
global int delayLength = 22050;  // 0.5 seconds at 44.1kHz
global int writePos = 0;

function processDelay() {
    // Read delayed signal
    array delayed[2];
    int readPos = writePos - delayLength;
    if (readPos < 0) readPos += delayLength;
    
    read(readPos, 1, delayed);
    
    // Write current signal
    write(writePos, 1, signal);
    
    // Advance write position
    writePos = (writePos + 1) % delayLength;
    
    // Mix with delayed signal
    global signal[0] = (global signal[0] + delayed[0]) >> 1;
    global signal[1] = (global signal[1] + delayed[1]) >> 1;
}
```

### Clock and Timing Patterns
```impala
// Official clock handling pattern
global int clock = 0;  // Auto-incremented by Permut8

function processWithTiming() {
    // Clock frequency limiting (from both firmwares)
    const int clockFreqLimit = 132300;
    
    // Tempo-based step calculation
    int tempoParam = (int) global params[CLOCK_FREQ_PARAM_INDEX];
    int stepRate = tempoParam + 1;  // 1-256 range
    
    // Clock division for different rates
    int stepClock = clock >> stepRate;
    int currentStep = stepClock & 15;  // 16-step cycle
    
    // Beat sync calculation
    int measure = stepClock >> 4;  // Measure counter
    int beat = stepClock & 3;      // Beat within measure
}
```

## LED Display Patterns

### Visual Feedback (Official Patterns)
```impala
// Beatrick LED pattern
function updateBeatrickLEDs() {
    // Step indicator
    global displayLEDs[0] = 1 << currentStep & 7;  // 8 LEDs max
    
    // Gain visualization
    global displayLEDs[1] = currentGain >> 3;  // Scale to 8-bit
    
    // Effect status
    global displayLEDs[2] = effectMask;  // Show active effects
    
    // Combined status
    global displayLEDs[3] = displayLEDs[0] | displayLEDs[1];
}

// FooBar LED pattern (more sophisticated)
function updateFooBarLEDs() {
    // Random pattern visualization
    global displayLEDs[0] = randomSeed & 0xFF;
    
    // Step progression
    global displayLEDs[1] = 1 << (currentStep & 7);
    
    // Effect intensity
    global displayLEDs[2] = effectIntensity;
    
    // Combined random + step
    global displayLEDs[3] = displayLEDs[0] ^ displayLEDs[1];
}
```

## Host Integration Patterns (Version 3)

### DAW Synchronization
```impala
// FooBar host sync pattern (Version 3 only)
global int hostPosition = 0;  // Updated by Permut8

function processWithHostSync() {
    // Check if host sync is enabled
    int syncMode = (int) global params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK;
    
    if (syncMode && hostPosition != 0) {
        // Use host position for sequencing
        int hostStep = (hostPosition >> 10) & 31;  // 32-step from host
        currentStep = hostStep;
    } else {
        // Use internal clock
        currentStep = (clock >> 8) & 31;
    }
    
    // Two-bar synchronization
    int twoBarClock = hostPosition >> 13;  // Measure-level sync
    int measure = twoBarClock & 1;  // Odd/even measures
}
```

## Optimization Patterns

### Performance Optimization
```impala
// Official patterns for efficient processing

// Bit shifting instead of division
int scaledValue = parameter >> 3;  // Divide by 8

// Lookup tables for expensive operations
readonly array sineTable[256] = { /* precomputed values */ };
int sineValue = sineTable[phase & 255];

// Early exit patterns
function processConditionally() {
    if (bypassMode) return;  // Skip processing when bypassed
    
    // Continue with processing...
}

// Efficient parameter change detection
static int lastParams[PARAM_COUNT];
function checkParameterChanges() {
    for (int i = 0; i < PARAM_COUNT; i++) {
        if (params[i] != lastParams[i]) {
            updateParameter(i, params[i]);
            lastParams[i] = params[i];
        }
    }
}
```

## Best Practices Summary

### Must-Have Patterns
1. **Use updateMask** for parameter change detection
2. **Implement smooth interpolation** for parameter changes
3. **Follow standard memory layout** for bank compatibility
4. **Use official timing patterns** for consistent behavior
5. **Implement proper LED feedback** for user experience

### Performance Guidelines
- Use bit operations instead of division/multiplication
- Implement early exit conditions
- Cache frequently accessed values
- Use lookup tables for expensive calculations
- Minimize memory allocations

### Bank Compatibility
- Follow exact global variable layout
- Implement all required functions (reset, update, process)
- Use parameter indices correctly
- Design for preset switching
- Test across all parameter ranges

## See Also

- **[P8Bank Format](../../../architecture/p8bank-format.md)** - Bank file structure
- **[Creating Firmware Banks](../../tutorials/creating-firmware-banks.md)** - Bank creation workflow
- **[Core Language Reference](../../../language/core_language_reference.md)** - Language fundamentals