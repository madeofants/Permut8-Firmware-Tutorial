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

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clock = 0


global int hostPosition = 0
```

### Required Function Structure
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

## Parameter Handling Patterns

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


function update() {
    if (updateMask & (1 << OPERAND_1_HIGH_PARAM_INDEX)) {

        recalculateEffectParameters();
    }
}
```

### Bit Manipulation for Parameter Packing
```impala

function readCombinedParameter() 
returns int combined
{
    int high = (int) global params[OPERAND_1_HIGH_PARAM_INDEX];
    int low = (int) global params[OPERAND_1_LOW_PARAM_INDEX];
    combined = (high << 8) | low;
}


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

const int STEP_COUNT = 16

global array steps[STEP_COUNT]
global array gains[STEP_COUNT]
global array holds[STEP_COUNT]
global array sfxs[STEP_COUNT]

function processStepSequencer() {

    int currentStep = (clock >> 8) & (STEP_COUNT - 1);
    

    const int LOOKAHEAD = 0x80;
    int lookaheadStep = ((clock + LOOKAHEAD) >> 8) & (STEP_COUNT - 1);
    

    int stepData = steps[currentStep];
    int gain = gains[currentStep];
    int effect = sfxs[currentStep];
}
```

### FooBar Pattern (32 Steps + Randomization)
```impala

const int STEP_COUNT = 32

global array stepFXs[STEP_COUNT]
global int randomSeed = 0

function processAdvancedSequencer() {

    int currentStep = (clock >> 7) & (STEP_COUNT - 1);
    

    function generateRandomPattern() {

        int seed = (int) global params[OPERAND_1_LOW_PARAM_INDEX];
        randomSeed = (randomSeed * 1103515245 + 12345) & 0x7FFFFFFF;
        randomSeed ^= seed;
    }
    

    if (hostPosition != 0) {

        currentStep = (hostPosition >> 10) & (STEP_COUNT - 1);
    }
}
```

## Audio Processing Patterns

### Interpolation for Smooth Effects
```impala

function smoothParameterChange(int currentValue, int targetValue) 
returns int smoothedValue
{
    int difference = targetValue - currentValue;
    int smoothed = difference >> 5;
    smoothedValue = currentValue + smoothed;
}


global int currentGain = 0;
function processWithGainSmoothing() {
    int targetGain = gains[currentStep];
    currentGain = smoothParameterChange(currentGain, targetGain);
    

    global signal[0] = (global signal[0] * currentGain) >> 8;
    global signal[1] = (global signal[1] * currentGain) >> 8;
}
```

### Effect Implementation Patterns

#### Beatrick Effects (Version 2)
```impala

const int NOP = 0;
const int MUTE = 1;
const int REPEAT = 2;
const int SKIP = 3;
const int HOLD = 4;
const int ACCENT = 1;
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

            repeatPreviousStep();
            break;
            
        case HOLD:

            holdCurrentSlice();
            break;
            
        case REVERSE:

            reversePlayback();
            break;
    }
}
```

#### FooBar Effects (Version 3)
```impala

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

            int bits = 12 - (intensity >> 5);
            int mask = 0xFFF0 << (12 - bits);
            global signal[0] &= mask;
            global signal[1] &= mask;
            break;
            
        case PITCH_SHIFT_EFFECT:

            processPitchShift(intensity);
            break;
            
        case HALF_SPEED_EFFECT:

            processTimeStretch(intensity);
            break;
    }
}
```

## Memory Management Patterns

### Delay Line Operations (Official Pattern)
```impala

global int delayLength = 22050;
global int writePos = 0;

function processDelay() {

    array delayed[2];
    int readPos = writePos - delayLength;
    if (readPos < 0) readPos += delayLength;
    
    read(readPos, 1, delayed);
    

    write(writePos, 1, signal);
    

    writePos = (writePos + 1) % delayLength;
    

    global signal[0] = (global signal[0] + delayed[0]) >> 1;
    global signal[1] = (global signal[1] + delayed[1]) >> 1;
}
```

### Clock and Timing Patterns
```impala

global int clock = 0;

function processWithTiming() {

    const int clockFreqLimit = 132300;
    

    int tempoParam = (int) global params[CLOCK_FREQ_PARAM_INDEX];
    int stepRate = tempoParam + 1;
    

    int stepClock = clock >> stepRate;
    int currentStep = stepClock & 15;
    

    int measure = stepClock >> 4;
    int beat = stepClock & 3;
}
```

## LED Display Patterns

### Visual Feedback (Official Patterns)
```impala

function updateBeatrickLEDs() {

    global displayLEDs[0] = 1 << currentStep & 7;
    

    global displayLEDs[1] = currentGain >> 3;
    

    global displayLEDs[2] = effectMask;
    

    global displayLEDs[3] = displayLEDs[0] | displayLEDs[1];
}


function updateFooBarLEDs() {

    global displayLEDs[0] = randomSeed & 0xFF;
    

    global displayLEDs[1] = 1 << (currentStep & 7);
    

    global displayLEDs[2] = effectIntensity;
    

    global displayLEDs[3] = displayLEDs[0] ^ displayLEDs[1];
}
```

## Host Integration Patterns (Version 3)

### DAW Synchronization
```impala

global int hostPosition = 0;

function processWithHostSync() {

    int syncMode = (int) global params[SWITCHES_PARAM_INDEX] & SWITCHES_SYNC_MASK;
    
    if (syncMode && hostPosition != 0) {

        int hostStep = (hostPosition >> 10) & 31;
        currentStep = hostStep;
    } else {

        currentStep = (clock >> 8) & 31;
    }
    

    int twoBarClock = hostPosition >> 13;
    int measure = twoBarClock & 1;
}
```

## Optimization Patterns

### Performance Optimization
```impala



int scaledValue = parameter >> 3;


readonly array sineTable[256] = { /* precomputed values */ };
int sineValue = sineTable[phase & 255];


function processConditionally() {
    if (bypassMode) return;
    

}


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