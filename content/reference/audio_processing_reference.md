# Audio Processing Reference

## What This Is
Core DSP concepts and audio processing techniques for Permut8 firmware. Covers signal flow, filtering, effects algorithms, and optimization patterns for real-time audio.

## Parameter Interface System

**Original Permut8 Interface**: 
- Instruction operands controlled via scrollable LED displays + bit switches
- Users click/drag hex displays or flip individual bit switches to set values
- Each operand = 8-bit value (0-255) displayed as hex (00-FF)

**Custom Firmware Override**:
- Converts operand parameters into direct knob controls
- `panelTextRows` replaces hex displays with effect-specific labels
- Same parameter data (`params[3-7]`), different user interface

**Code Access Pattern**:
```impala
// Read parameter value (same regardless of interface type)
int value = (int)params[OPERAND_1_HIGH_PARAM_INDEX];  // 0-255
// This value comes from:
//   Original UI: User's switch/LED input
//   Custom firmware: Direct knob control

// Provide LED feedback
displayLEDs[0] = someCalculation;  // Show result to user
```

## Signal Flow Fundamentals

### Constants and Definitions
```impala
// Essential mathematical constants
const int TWO_PI_SCALED = 6283  // TWO_PI * 1000 for fixed-point math

// Permut8 audio sample range
const int AUDIO_MIN = -2047
const int AUDIO_MAX = 2047
const int AUDIO_ZERO = 0
```

### Audio Signal Range
```impala
// 12-bit signed samples
// Full scale ≈ ±2048 (12-bit range)
// Quiet signals: ±10 to ±100
// Moderate signals: ±500 to ±1500  
// Loud signals: ±1500 to ±2047

// Use the constants defined above:
// AUDIO_MIN = -2047, AUDIO_MAX = 2047, AUDIO_ZERO = 0
```

### Signal Processing Chain
```impala
function process() {
    // 1. Read input
    int inputLeft = signal[0];
    int inputRight = signal[1];
    
    // 2. Process audio
    int processedLeft = audioProcess(inputLeft);
    int processedRight = audioProcess(inputRight);
    
    // 3. Clip to valid range
    if (processedLeft > AUDIO_MAX) processedLeft = AUDIO_MAX;
    else if (processedLeft < AUDIO_MIN) processedLeft = AUDIO_MIN;
    if (processedRight > AUDIO_MAX) processedRight = AUDIO_MAX;
    else if (processedRight < AUDIO_MIN) processedRight = AUDIO_MIN;
    
    // 4. Write output
    signal[0] = processedLeft;
    signal[1] = processedRight;
    
    yield();
}
```

### Stereo Processing Patterns
```impala
// Identical processing (mono-in-stereo)
function processMonoStereo(int input) returns int {
    // Same processing for both channels
    signal[0] = audioEffect(input);
    signal[1] = signal[0];  // Copy left to right
}

// Independent processing
function processStereo() {
    signal[0] = leftChannelEffect(signal[0]);
    signal[1] = rightChannelEffect(signal[1]);
}

// Cross-channel processing  
function processCrossed() {
    int tempLeft = signal[0];
    int tempRight = signal[1];
    
    signal[0] = leftEffect(tempLeft, tempRight);   // L uses both inputs
    signal[1] = rightEffect(tempLeft, tempRight);  // R uses both inputs
}
```

## Basic Filters

### Simple Low-Pass Filter
```impala
global int lastOutputLeft = 0;
global int lastOutputRight = 0;

function lowPassFilter(int input, int lastOutput) 
returns int filtered {
    // Simple RC-style low-pass: Y[n] = Y[n-1] + (X[n] - Y[n-1]) * cutoff
    int cutoffAmount = (int)params[OPERAND_1_HIGH_PARAM_INDEX];  // 0-255
    
    // Scale cutoff (0-255 → 0-32 for stability)
    int scaledCutoff = cutoffAmount >> 3;  // Divide by 8
    
    // Filter calculation
    int difference = input - lastOutput;
    filtered = lastOutput + ((difference * scaledCutoff) >> 8);
}

function process() {
    lastOutputLeft = lowPassFilter(signal[0], lastOutputLeft);
    lastOutputRight = lowPassFilter(signal[1], lastOutputRight);
    
    signal[0] = lastOutputLeft;
    signal[1] = lastOutputRight;
    
    yield();
}
```

### Simple High-Pass Filter
```impala
global int lastInputLeft = 0;
global int lastInputRight = 0;
global int lastOutputLeft = 0;
global int lastOutputRight = 0;

function highPassFilter(int input, int lastInput, int lastOutput)
returns int filtered {
    // High-pass: Y[n] = X[n] - X[n-1] + 0.95 * Y[n-1]
    int cutoffAmount = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    // Scale for stability (0-255 → 0.7-0.99)
    int feedback = 180 + (cutoffAmount >> 2);  // 180-243 = ~0.7-0.95 when /256
    
    int difference = input - lastInput;
    filtered = difference + ((lastOutput * feedback) >> 8);
}

function process() {
    lastOutputLeft = highPassFilter(signal[0], lastInputLeft, lastOutputLeft);
    lastOutputRight = highPassFilter(signal[1], lastInputRight, lastOutputRight);
    
    lastInputLeft = signal[0];
    lastInputRight = signal[1];
    
    signal[0] = lastOutputLeft;
    signal[1] = lastOutputRight;
    
    yield();
}
```

### State Variable Filter
```impala
global int svf_low = 0;
global int svf_band = 0;
global int svf_high = 0;

function stateVariableFilter(int input) {
    // Get parameters
    int frequency = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int resonance = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    
    // Scale frequency (avoid overflow)
    int f = frequency >> 2;  // 0-63 range
    int q = 256 - resonance; // Inverse Q for stability
    
    // State variable equations
    svf_low = svf_low + ((svf_band * f) >> 8);
    svf_high = input - svf_low - ((svf_band * q) >> 8);
    svf_band = svf_band + ((svf_high * f) >> 8);
    
    // Clip internal states
    if (svf_low > AUDIO_MAX) svf_low = AUDIO_MAX;
    else if (svf_low < AUDIO_MIN) svf_low = AUDIO_MIN;
    if (svf_band > AUDIO_MAX) svf_band = AUDIO_MAX;
    else if (svf_band < AUDIO_MIN) svf_band = AUDIO_MIN;
    if (svf_high > AUDIO_MAX) svf_high = AUDIO_MAX;
    else if (svf_high < AUDIO_MIN) svf_high = AUDIO_MIN;
}

function process() {
    stateVariableFilter(signal[0]);
    
    // Choose filter output type
    int filterType = (int)params[SWITCHES_PARAM_INDEX] & 3;  // 2 bits = 4 types
    
    if (filterType == 0) signal[0] = svf_low;       // Low-pass
    else if (filterType == 1) signal[0] = svf_band; // Band-pass  
    else if (filterType == 2) signal[0] = svf_high; // High-pass
    else signal[0] = svf_low + svf_high;             // Notch (low+high)
    
    signal[1] = signal[0];  // Mono output
    
    yield();
}
```

## Distortion and Waveshaping

### Hard Clipping
```impala
function hardClip(int input, int threshold) 
returns int clipped {
    if (input > threshold) clipped = threshold;
    else if (input < -threshold) clipped = -threshold;
    else clipped = input;
}

function process() {
    // Clip threshold from knob (100-2047)
    int clipLevel = 100 + ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 7);
    
    signal[0] = hardClip(signal[0], clipLevel);
    signal[1] = hardClip(signal[1], clipLevel);
    
    yield();
}
```

### Soft Clipping (Tanh Approximation)
```impala
function softClip(int input) 
returns int clipped {
    // Approximate tanh using polynomial
    // tanh(x) ≈ x - x³/3 for small x
    
    if (input > 1500 || input < -1500) {
        // Hard limit for extreme values
        if (input > 0) {
            return 1500;
        } else {
            return -1500;
        }
    }
    
    // Soft clipping calculation
    int x = input >> 2;           // Scale down to prevent overflow
    int x_cubed = ((x * x) >> 8) * x >> 8;  // x³ approximation
    int soft = x - (x_cubed / 3);
    
    return soft << 2;  // Scale back up
}

function process() {
    signal[0] = softClip(signal[0]);
    signal[1] = softClip(signal[1]);
    
    yield();
}
```

### Bit Crushing
```impala
function bitCrush(int input, int bits) 
returns int crushed {
    // Reduce bit depth by masking lower bits
    if (bits >= 12) return input;  // No crushing
    if (bits <= 1) bits = 1;       // Minimum 1 bit
    
    // Create mask: keep top 'bits' bits, zero the rest
    int shiftAmount = 12 - bits;
    int mask = 0xFFF << shiftAmount;  // Mask for top bits
    
    // Apply bit reduction
    crushed = input & mask;
}

function process() {
    // Bit depth from knob (1-12 bits)
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int bitDepth = 1 + (knobValue * 11 / 255);
    
    signal[0] = bitCrush(signal[0], bitDepth);
    signal[1] = bitCrush(signal[1], bitDepth);
    
    // LED feedback shows bit depth
    displayLEDs[0] = bitDepth;
    
    yield();
}
```

### Sample Rate Reduction
```impala
global int sampleHold = 0;
global int holdCounter = 0;

function sampleRateReduce(int input, int reductionFactor) 
returns int reduced {
    holdCounter++;
    
    if (holdCounter >= reductionFactor) {
        sampleHold = input;      // Update held sample
        holdCounter = 0;
    }
    
    return sampleHold;          // Output held sample
}

function process() {
    // Reduction factor from knob (1-32)
    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int reduction = 1 + (knobValue >> 3);  // 1-32 range
    
    signal[0] = sampleRateReduce(signal[0], reduction);
    signal[1] = signal[0];  // Mono effect
    
    yield();
}
```

## Modulation Effects

### Tremolo (Amplitude Modulation)
```impala
global int tremoloPhase = 0;

function process() {
    // Tremolo rate from knob (0.1-10 Hz scaled)
    int rateKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int phaseInc = 1 + (rateKnob >> 4);  // 1-17 phase increment
    
    // Tremolo depth from knob (0-100%)
    int depthKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    
    // Update phase
    tremoloPhase += phaseInc;
    if (tremoloPhase >= 1000) tremoloPhase -= 1000;
    
    // Generate LFO using lookup table or approximation
    int lfoValue = (tremoloPhase * 2047) / 500 - 1023;  // Triangle wave approximation
    
    // Calculate amplitude multiplier (fixed-point)
    int amplifier = 256 - ((depthKnob * lfoValue) >> 8);
    
    // Apply to signal
    signal[0] = (signal[0] * amplifier) >> 8;
    signal[1] = (signal[1] * amplifier) >> 8;
    
    yield();
}
```

### Ring Modulation
```impala
global int carrierPhase = 0;

function process() {
    // Carrier frequency from knob (scaled for integer math)
    int freqKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int phaseInc = 1 + (freqKnob >> 2);  // 1-65 phase increment
    
    // Ring modulation depth
    int depthKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    
    // Update carrier phase
    carrierPhase += phaseInc;
    if (carrierPhase >= 1000) carrierPhase -= 1000;
    
    // Generate carrier (triangle wave approximation)
    int carrier = (carrierPhase * 2047) / 500 - 1023;
    
    // Apply ring modulation (fixed-point)
    int modAmount = (depthKnob * carrier) >> 8;
    signal[0] = (signal[0] * (256 + modAmount)) >> 8;
    signal[1] = (signal[1] * (256 + modAmount)) >> 8;
    
    yield();
}
```

### Chorus (Modulated Delay)
```impala
global int chorusPhase = 0;
global int delayBuffer[4000];  // ~80ms at 48kHz
global int writePos = 0;

function process() {
    // Write input to delay buffer
    delayBuffer[writePos] = signal[0];
    
    // Chorus parameters
    int rateKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int phaseInc = 1 + (rateKnob >> 5);  // 1-9 phase increment
    
    int depthKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    int chorusDepth = 5 + (depthKnob >> 3);  // 5-37 samples variation
    
    // Update LFO phase (integer)
    chorusPhase += phaseInc;
    if (chorusPhase >= 1000) chorusPhase -= 1000;
    
    // Calculate modulated delay time (triangle LFO)
    int lfo = (chorusPhase * chorusDepth) / 500 - (chorusDepth >> 1);
    int modulatedDelay = 1000 + lfo;  // Base 1000 samples
    
    // Read from modulated position
    int readPos = writePos - modulatedDelay;
    if (readPos < 0) readPos += 4000;
    
    int delayedSample = delayBuffer[readPos];
    
    // Mix wet/dry
    signal[0] = (signal[0] + delayedSample) >> 1;
    signal[1] = signal[0];  // Mono effect
    
    // Advance write position
    writePos = (writePos + 1) % 4000;
    
    yield();
}
```

## Dynamic Processing

### Simple Compressor
```impala
global int compressorGain = 256;  // 1.0 in 8.8 fixed point

function process() {
    // Threshold and ratio from knobs
    int thresholdKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int threshold = 500 + (thresholdKnob * 6);  // 500-2030 range
    
    int ratioKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    int ratio = 2 + (ratioKnob >> 6);  // 2:1 to 6:1 compression
    
    // Calculate input level (simplified peak detection)
    int inputLevel = signal[0];
    if (inputLevel < 0) inputLevel = -inputLevel;  // Absolute value
    
    // Compression calculation
    if (inputLevel > threshold) {
        // Signal is above threshold, apply compression
        int excess = inputLevel - threshold;
        int compressedExcess = excess / ratio;
        int targetLevel = threshold + compressedExcess;
        
        // Calculate gain reduction needed
        int targetGain = (targetLevel << 8) / inputLevel;  // 8.8 fixed point
        
        // Smooth gain changes (simple envelope follower)
        if (targetGain < compressorGain) {
            compressorGain = compressorGain - ((compressorGain - targetGain) >> 3);  // Fast attack
        } else {
            compressorGain = compressorGain + ((targetGain - compressorGain) >> 6);  // Slow release
        }
    } else {
        // Below threshold, return to unity gain slowly
        compressorGain = compressorGain + ((256 - compressorGain) >> 6);
    }
    
    // Apply gain
    signal[0] = (signal[0] * compressorGain) >> 8;
    signal[1] = (signal[1] * compressorGain) >> 8;
    
    // LED shows gain reduction
    displayLEDs[0] = 255 - (compressorGain >> 0);
    
    yield();
}
```

### Gate/Expander
```impala
global int gateGain = 0;

function process() {
    // Gate threshold from knob
    int thresholdKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int gateThreshold = thresholdKnob * 8;  // 0-2040 range
    
    // Calculate signal level
    int signalLevel = signal[0];
    if (signalLevel < 0) signalLevel = -signalLevel;
    
    // Gate logic
    if (signalLevel > gateThreshold) {
        // Above threshold - open gate quickly
        gateGain = gateGain + ((256 - gateGain) >> 2);  // Fast open
    } else {
        // Below threshold - close gate slowly
        gateGain = gateGain - (gateGain >> 4);  // Slow close
    }
    
    // Apply gate
    signal[0] = (signal[0] * gateGain) >> 8;
    signal[1] = (signal[1] * gateGain) >> 8;
    
    yield();
}
```

## Advanced Techniques

### Spectral Processing (Simple)
```impala
// Simple spectral-like processing using delay lines
global int spectralDelays[8] = {100, 150, 200, 300, 450, 600, 800, 1200};
global int spectralGains[8] = {256, 256, 256, 256, 256, 256, 256, 256};

function processSpectralBand(int input, int delayTime, int gain) 
returns int processed {
    array delayBuffer[2];
    
    // Read delayed signal (represents frequency band)
    read(clock - delayTime, 1, delayBuffer);
    
    // Apply gain to this "band"
    int bandSignal = (delayBuffer[0] * gain) >> 8;
    
    // Write current input for future processing
    array inputArray[2] = {input, input};
    write(clock, 1, inputArray);
    
    return bandSignal;
}

function process() {
    int output = 0;
    
    // Process multiple "bands" with different delay times
    int band;
    for (band = 0 to 8) {
        // Get gain for this band from parameters
        int bandGain = spectralGains[band];
        
        // Process band and accumulate
        int bandOutput = processSpectralBand(signal[0], spectralDelays[band], bandGain);
        output += bandOutput >> 3;  // Mix bands (divide by 8)
    }
    
    signal[0] = output;
    signal[1] = output;
    
    yield();
}
```

### Granular Processing
```impala
global int grainPos = 0;
global int grainSize = 1000;
global int grainStep = 500;
global int windowPos = 0;

function process() {
    // Granular parameters
    int sizeKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    grainSize = 200 + (sizeKnob * 8);  // 200-2240 samples
    
    int stepKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    grainStep = 100 + (stepKnob * 4);  // 100-1120 samples
    
    // Write input to delay line
    array input[2] = {signal[0], signal[1]};
    write(clock, 1, input);
    
    // Read grain from delay line
    array grain[2];
    read(clock - 5000 - grainPos, 1, grain);
    
    // Apply window function (triangular)
    int window = 255;
    if (windowPos < grainSize / 4) {
        window = (windowPos * 255) / (grainSize / 4);  // Attack
    } else if (windowPos > grainSize * 3 / 4) {
        window = ((grainSize - windowPos) * 255) / (grainSize / 4);  // Release
    }
    
    // Apply windowing
    signal[0] = (grain[0] * window) >> 8;
    signal[1] = (grain[1] * window) >> 8;
    
    // Advance grain position
    windowPos++;
    if (windowPos >= grainSize) {
        windowPos = 0;
        grainPos += grainStep;
        if (grainPos >= 10000) grainPos = 0;  // Wrap grain position
    }
    
    yield();
}
```

## Performance Optimization

### Fixed-Point Arithmetic
```impala
// Avoid floating point when possible
// Use shifts instead of division/multiplication by powers of 2

// Bad: slow floating point
float result = input * 0.5;

// Good: fast integer shift
int result = input >> 1;  // Divide by 2

// For other fractions, use fixed-point
// Example: multiply by 0.75 = multiply by 3, then divide by 4
int result = (input * 3) >> 2;
```

### Look-Up Tables
```impala
// Pre-computed sine table for fast oscillators
const int SINE_TABLE[256] = {
    0, 50, 100, 150, 199, 247, 295, 342, 389, 435,
    // ... full sine table
};

function fastSine(int phase) 
returns int sineValue {
    // Phase is 0-255 for one cycle
    return SINE_TABLE[phase & 255];
}
```

### Memory Access Optimization
```impala
// Batch processing when possible
function efficientDelayRead() {
    const int BATCH_SIZE = 16;
    array delayBatch[BATCH_SIZE * 2];
    
    // Read many samples at once
    read(clock - 1000, BATCH_SIZE, delayBatch);
    
    // Process batch
    int i;
    for (i = 0 to BATCH_SIZE) {
        // Process delayBatch[i*2] and delayBatch[i*2+1]
    }
}
```

## Common Audio Pitfalls

### Avoiding Clicks and Pops
```impala
// Always smooth parameter changes
global int lastGainValue = 0;

function smoothParameterChange() {
    int newGain = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    // Smooth transition to new value
    lastGainValue = lastGainValue + ((newGain - lastGainValue) >> 3);
    
    // Use smoothed value
    signal[0] = (signal[0] * lastGainValue) >> 8;
}
```

### Preventing Overflow
```impala
// Always check for overflow in feedback systems
function safeProcessing(int input, int gain) returns int result {
    // Use careful intermediate calculations to prevent overflow
    // Scale inputs to prevent overflow during multiplication
    int scaledInput = input >> 2;  // Reduce by 4
    int scaledGain = gain >> 2;    // Reduce by 4
    
    int temp = scaledInput * scaledGain;
    temp = temp << 2;  // Scale back up
    
    // Check bounds before returning
    if (temp > 2047) temp = 2047;
    else if (temp < -2047) temp = -2047;
    
    result = temp;
}
```

### DC Offset Prevention
```impala
// High-pass filter to remove DC
global int dcBlockerInput = 0;
global int dcBlockerOutput = 0;

function dcBlocker(int input) 
returns int blocked {
    // Y[n] = X[n] - X[n-1] + 0.995 * Y[n-1]
    blocked = input - dcBlockerInput + ((dcBlockerOutput * 254) >> 8);
    dcBlockerInput = input;
    dcBlockerOutput = blocked;
}
```

## Best Practices

1. **Always clip outputs**: Prevent overflow with proper limiting
2. **Smooth parameter changes**: Avoid clicks from sudden control jumps  
3. **Use appropriate data types**: int for samples, float for calculations when needed
4. **Plan memory usage**: Consider delay buffer sizes and access patterns
5. **Test edge cases**: Extreme parameter values, silence, full-scale signals
6. **Profile performance**: Monitor CPU usage with complex algorithms
7. **Maintain DC stability**: Use high-pass filtering when needed

---
*See also: [Memory Management](memory_management.md), [Timing Reference](timing_reference.md)*