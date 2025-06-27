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

int value = (int)params[OPERAND_1_HIGH_PARAM_INDEX];





displayLEDs[0] = someCalculation;
```

## Signal Flow Fundamentals

### Constants and Definitions
```impala

const int TWO_PI_SCALED = 6283


const int AUDIO_MIN = -2047
const int AUDIO_MAX = 2047
const int AUDIO_ZERO = 0
```

### Audio Signal Range
```impala








```

### Signal Processing Chain
```impala
function process() {

    int inputLeft = signal[0];
    int inputRight = signal[1];
    

    int processedLeft = audioProcess(inputLeft);
    int processedRight = audioProcess(inputRight);
    

    if (processedLeft > AUDIO_MAX) processedLeft = AUDIO_MAX;
    else if (processedLeft < AUDIO_MIN) processedLeft = AUDIO_MIN;
    if (processedRight > AUDIO_MAX) processedRight = AUDIO_MAX;
    else if (processedRight < AUDIO_MIN) processedRight = AUDIO_MIN;
    

    signal[0] = processedLeft;
    signal[1] = processedRight;
    
    yield();
}
```

### Stereo Processing Patterns
```impala

function processMonoStereo(int input) returns int {

    signal[0] = audioEffect(input);
    signal[1] = signal[0];
}


function processStereo() {
    signal[0] = leftChannelEffect(signal[0]);
    signal[1] = rightChannelEffect(signal[1]);
}


function processCrossed() {
    int tempLeft = signal[0];
    int tempRight = signal[1];
    
    signal[0] = leftEffect(tempLeft, tempRight);
    signal[1] = rightEffect(tempLeft, tempRight);
}
```

## Basic Filters

### Simple Low-Pass Filter
```impala
global int lastOutputLeft = 0;
global int lastOutputRight = 0;

function lowPassFilter(int input, int lastOutput) 
returns int filtered {

    int cutoffAmount = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    

    int scaledCutoff = cutoffAmount >> 3;
    

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

    int cutoffAmount = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    

    int feedback = 180 + (cutoffAmount >> 2);
    
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

    int frequency = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int resonance = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    

    int f = frequency >> 2;
    int q = 256 - resonance;
    

    svf_low = svf_low + ((svf_band * f) >> 8);
    svf_high = input - svf_low - ((svf_band * q) >> 8);
    svf_band = svf_band + ((svf_high * f) >> 8);
    

    if (svf_low > AUDIO_MAX) svf_low = AUDIO_MAX;
    else if (svf_low < AUDIO_MIN) svf_low = AUDIO_MIN;
    if (svf_band > AUDIO_MAX) svf_band = AUDIO_MAX;
    else if (svf_band < AUDIO_MIN) svf_band = AUDIO_MIN;
    if (svf_high > AUDIO_MAX) svf_high = AUDIO_MAX;
    else if (svf_high < AUDIO_MIN) svf_high = AUDIO_MIN;
}

function process() {
    stateVariableFilter(signal[0]);
    

    int filterType = (int)params[SWITCHES_PARAM_INDEX] & 3;
    
    if (filterType == 0) signal[0] = svf_low;
    else if (filterType == 1) signal[0] = svf_band;
    else if (filterType == 2) signal[0] = svf_high;
    else signal[0] = svf_low + svf_high;
    
    signal[1] = signal[0];
    
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


    
    if (input > 1500 || input < -1500) {

        if (input > 0) {
            return 1500;
        } else {
            return -1500;
        }
    }
    

    int x = input >> 2;
    int x_cubed = ((x * x) >> 8) * x >> 8;
    int soft = x - (x_cubed / 3);
    
    return soft << 2;
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

    if (bits >= 12) return input;
    if (bits <= 1) bits = 1;
    

    int shiftAmount = 12 - bits;
    int mask = 0xFFF << shiftAmount;
    

    crushed = input & mask;
}

function process() {

    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int bitDepth = 1 + (knobValue * 11 / 255);
    
    signal[0] = bitCrush(signal[0], bitDepth);
    signal[1] = bitCrush(signal[1], bitDepth);
    

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
        sampleHold = input;
        holdCounter = 0;
    }
    
    return sampleHold;
}

function process() {

    int knobValue = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int reduction = 1 + (knobValue >> 3);
    
    signal[0] = sampleRateReduce(signal[0], reduction);
    signal[1] = signal[0];
    
    yield();
}
```

## Modulation Effects

### Tremolo (Amplitude Modulation)
```impala
global int tremoloPhase = 0;

function process() {

    int rateKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int phaseInc = 1 + (rateKnob >> 4);
    

    int depthKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    

    tremoloPhase += phaseInc;
    if (tremoloPhase >= 1000) tremoloPhase -= 1000;
    

    int lfoValue = (tremoloPhase * 2047) / 500 - 1023;
    

    int amplifier = 256 - ((depthKnob * lfoValue) >> 8);
    

    signal[0] = (signal[0] * amplifier) >> 8;
    signal[1] = (signal[1] * amplifier) >> 8;
    
    yield();
}
```

### Ring Modulation
```impala
global int carrierPhase = 0;

function process() {

    int freqKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int phaseInc = 1 + (freqKnob >> 2);
    

    int depthKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    

    carrierPhase += phaseInc;
    if (carrierPhase >= 1000) carrierPhase -= 1000;
    

    int carrier = (carrierPhase * 2047) / 500 - 1023;
    

    int modAmount = (depthKnob * carrier) >> 8;
    signal[0] = (signal[0] * (256 + modAmount)) >> 8;
    signal[1] = (signal[1] * (256 + modAmount)) >> 8;
    
    yield();
}
```

### Chorus (Modulated Delay)
```impala
global int chorusPhase = 0;
global int delayBuffer[4000];
global int writePos = 0;

function process() {

    delayBuffer[writePos] = signal[0];
    

    int rateKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int phaseInc = 1 + (rateKnob >> 5);
    
    int depthKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    int chorusDepth = 5 + (depthKnob >> 3);
    

    chorusPhase += phaseInc;
    if (chorusPhase >= 1000) chorusPhase -= 1000;
    

    int lfo = (chorusPhase * chorusDepth) / 500 - (chorusDepth >> 1);
    int modulatedDelay = 1000 + lfo;
    

    int readPos = writePos - modulatedDelay;
    if (readPos < 0) readPos += 4000;
    
    int delayedSample = delayBuffer[readPos];
    

    signal[0] = (signal[0] + delayedSample) >> 1;
    signal[1] = signal[0];
    

    writePos = (writePos + 1) % 4000;
    
    yield();
}
```

## Dynamic Processing

### Simple Compressor
```impala
global int compressorGain = 256;

function process() {

    int thresholdKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int threshold = 500 + (thresholdKnob * 6);
    
    int ratioKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    int ratio = 2 + (ratioKnob >> 6);
    

    int inputLevel = signal[0];
    if (inputLevel < 0) inputLevel = -inputLevel;
    

    if (inputLevel > threshold) {

        int excess = inputLevel - threshold;
        int compressedExcess = excess / ratio;
        int targetLevel = threshold + compressedExcess;
        

        int targetGain = (targetLevel << 8) / inputLevel;
        

        if (targetGain < compressorGain) {
            compressorGain = compressorGain - ((compressorGain - targetGain) >> 3);
        } else {
            compressorGain = compressorGain + ((targetGain - compressorGain) >> 6);
        }
    } else {

        compressorGain = compressorGain + ((256 - compressorGain) >> 6);
    }
    

    signal[0] = (signal[0] * compressorGain) >> 8;
    signal[1] = (signal[1] * compressorGain) >> 8;
    

    displayLEDs[0] = 255 - (compressorGain >> 0);
    
    yield();
}
```

### Gate/Expander
```impala
global int gateGain = 0;

function process() {

    int thresholdKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int gateThreshold = thresholdKnob * 8;
    

    int signalLevel = signal[0];
    if (signalLevel < 0) signalLevel = -signalLevel;
    

    if (signalLevel > gateThreshold) {

        gateGain = gateGain + ((256 - gateGain) >> 2);
    } else {

        gateGain = gateGain - (gateGain >> 4);
    }
    

    signal[0] = (signal[0] * gateGain) >> 8;
    signal[1] = (signal[1] * gateGain) >> 8;
    
    yield();
}
```

## Advanced Techniques

### Spectral Processing (Simple)
```impala

global int spectralDelays[8] = {100, 150, 200, 300, 450, 600, 800, 1200};
global int spectralGains[8] = {256, 256, 256, 256, 256, 256, 256, 256};

function processSpectralBand(int input, int delayTime, int gain) 
returns int processed {
    array delayBuffer[2];
    

    read(clock - delayTime, 1, delayBuffer);
    

    int bandSignal = (delayBuffer[0] * gain) >> 8;
    

    array inputArray[2] = {input, input};
    write(clock, 1, inputArray);
    
    return bandSignal;
}

function process() {
    int output = 0;
    

    int band;
    for (band = 0 to 8) {

        int bandGain = spectralGains[band];
        

        int bandOutput = processSpectralBand(signal[0], spectralDelays[band], bandGain);
        output += bandOutput >> 3;
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

    int sizeKnob = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    grainSize = 200 + (sizeKnob * 8);
    
    int stepKnob = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    grainStep = 100 + (stepKnob * 4);
    

    array input[2] = {signal[0], signal[1]};
    write(clock, 1, input);
    

    array grain[2];
    read(clock - 5000 - grainPos, 1, grain);
    

    int window = 255;
    if (windowPos < grainSize / 4) {
        window = (windowPos * 255) / (grainSize / 4);
    } else if (windowPos > grainSize * 3 / 4) {
        window = ((grainSize - windowPos) * 255) / (grainSize / 4);
    }
    

    signal[0] = (grain[0] * window) >> 8;
    signal[1] = (grain[1] * window) >> 8;
    

    windowPos++;
    if (windowPos >= grainSize) {
        windowPos = 0;
        grainPos += grainStep;
        if (grainPos >= 10000) grainPos = 0;
    }
    
    yield();
}
```

## Performance Optimization

### Fixed-Point Arithmetic
```impala




float result = input * 0.5;


int result = input >> 1;



int result = (input * 3) >> 2;
```

### Look-Up Tables
```impala

const int SINE_TABLE[256] = {
    0, 50, 100, 150, 199, 247, 295, 342, 389, 435,

};

function fastSine(int phase) 
returns int sineValue {

    return SINE_TABLE[phase & 255];
}
```

### Memory Access Optimization
```impala

function efficientDelayRead() {
    const int BATCH_SIZE = 16;
    array delayBatch[BATCH_SIZE * 2];
    

    read(clock - 1000, BATCH_SIZE, delayBatch);
    

    int i;
    for (i = 0 to BATCH_SIZE) {

    }
}
```

## Common Audio Pitfalls

### Avoiding Clicks and Pops
```impala

global int lastGainValue = 0;

function smoothParameterChange() {
    int newGain = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    

    lastGainValue = lastGainValue + ((newGain - lastGainValue) >> 3);
    

    signal[0] = (signal[0] * lastGainValue) >> 8;
}
```

### Preventing Overflow
```impala

function safeProcessing(int input, int gain) returns int result {


    int scaledInput = input >> 2;
    int scaledGain = gain >> 2;
    
    int temp = scaledInput * scaledGain;
    temp = temp << 2;
    

    if (temp > 2047) temp = 2047;
    else if (temp < -2047) temp = -2047;
    
    result = temp;
}
```

### DC Offset Prevention
```impala

global int dcBlockerInput = 0;
global int dcBlockerOutput = 0;

function dcBlocker(int input) 
returns int blocked {

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