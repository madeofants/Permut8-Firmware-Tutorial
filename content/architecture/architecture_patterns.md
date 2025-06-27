# Architecture Patterns

## What This Is
Architectural design patterns, lifecycle management, and performance strategies for Permut8 firmware development. Essential concepts for building robust, efficient audio processing systems.

## Permut8's Three-Approach Architecture

### **Understanding Permut8's Core System**

Permut8 has **128 kilowords of 12-bit delay memory** with moving read/write heads. All effects come from manipulating where and how audio is read from this memory buffer. There are **three distinct approaches** to working with this system:

### **Approach 1: Original Operator System**
```
Audio Input → 128k Delay Memory → [Operators manipulate read positions] → Audio Output
```

**How It Works**:
- Audio is continuously written to delay memory
- **Eight operators** (AND, MUL, OSC, RND, OR, XOR, MSK, SUB, NOP) manipulate read positions  
- **Two instructions** process sequentially to create complex effects
- **Operands** (0-255 values) control operator behavior

**Effects Created**: Delays, pitch shifting, modulation, granular textures, rhythmic patterns

**Interface**: Operators selected via presets, operands controlled via switches/LED displays

### **Approach 2: Custom Firmware (Full Patches)**
```
Audio Input → [Your code processes samples directly] → Audio Output
```

**How It Works**:
- **Completely bypass** the delay memory system
- **Direct sample processing** with your own algorithms
- **Total control** over every aspect of audio processing
- **Parameter override** - same `params[]` array, custom meanings

**Effects Created**: Distortion, filtering, compression, bit crushing, any algorithm you can code

**Interface**: Custom knob labels via `panelTextRows`, direct parameter mapping

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "CUSTOM |------ EFFECT CONTROL (KNOB) ------|",

};

function process() {
    loop {

        int inputLeft = signal[0];
        int inputRight = signal[1];
        

        signal[0] = processedLeft;
        signal[1] = processedRight;
        
        yield();
    }
}
```

### **Approach 3: Operator Modification (Mod Patches)**  
```
Audio Input → 128k Delay Memory → [Modified operators] → Audio Output
```

**How It Works**:
- **Replace specific operators** with custom code
- **Keep delay memory system** but customize how read positions are calculated
- **Hybrid approach** - leverage hardware efficiency with custom logic
- **Work within operator framework** but with custom behavior

**Effects Created**: Custom delays, unique modulation patterns, novel position-based effects

**Interface**: Standard operator interface, but with custom operator behavior

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array positions[2]
global array params[8]
global array displayLEDs[4]

function operate1() returns int processed {

    int delayOffset = calculateCustomDelay();
    
    positions[0] = positions[0] + delayOffset;
    positions[1] = positions[1] + delayOffset;
    
    return 1;
}

function operate2() returns int processed {

    return 1;
}
```

## **Choosing the Right Approach**

### **Use Original Operators When**:
- Building standard delays, modulation, or pitch effects
- Want maximum efficiency and hardware optimization
- Learning how Permut8 naturally creates effects
- Need familiar interface for users

### **Use Custom Firmware When**:
- Creating distortion, filtering, or mathematical effects
- Need algorithms that don't fit the memory manipulation model
- Want complete control over parameter interface
- Building novel effects that require sample-by-sample processing

### **Use Operator Modification When**:
- Want to customize delay/modulation behavior
- Need efficiency of hardware delay system with custom logic
- Creating variations on standard operator types
- Bridging between original system and custom approaches

## Lifecycle Management

### Initialization Phase
```impala

function init() {

    buildSineTable();
    buildFilterCoefficients();
    

    resetDelayBuffers();
    initializeFilters();
    

    setDefaultParameters();
    
    trace("Firmware initialized successfully");
}
```

**Best Practices for Initialization**:
- Compute expensive lookup tables once
- Initialize all global state variables
- Set safe default parameter values
- Pre-allocate any dynamic structures
- Validate critical system state

### Update Phase
```impala

global int lastParamValues[8] = {-1, -1, -1, -1, -1, -1, -1, -1};

function update() {

    int paramIndex;
    for (paramIndex = 0 to 8) {
        if (params[paramIndex] != lastParamValues[paramIndex]) {
            handleParameterChange(paramIndex, params[paramIndex]);
            lastParamValues[paramIndex] = params[paramIndex];
        }
    }
}

function handleParameterChange(int index, int newValue) {
    if (index == OPERAND_1_HIGH_PARAM_INDEX) {

        updateFilterFrequency(newValue);
    } else if (index == OPERAND_1_LOW_PARAM_INDEX) {

        updateFilterResonance(newValue);
    }

}
```

**Update Optimization Strategies**:
- Only recalculate when parameters actually change
- Use incremental updates instead of full recalculation
- Cache intermediate calculations
- Smooth parameter changes to avoid artifacts

### Reset Phase
```impala

function reset() {

    clearAllBuffers();
    

    resetFilterMemory();
    

    resetOscillatorPhases();
    

    resetEnvelopeFollowers();
    

    initializeProcessingState();
    
    trace("System reset completed");
}
```

**Reset Considerations**:
- Clear all audio memory to prevent artifacts
- Reset time-based accumulators (phases, counters)
- Preserve parameter settings
- Initialize to known good state
- Consider gradual reset to avoid clicks

### Processing Phase Management
```impala

function process() {
    loop {

        int inputL = signal[0];
        int inputR = signal[1];
        

        updateTimeState();
        

        processAudioSample(inputL, inputR);
        

        if (shouldUpdateDisplay()) {
            updateLEDDisplays();
        }
        

        yield();
    }
}

int displayUpdateCounter = 0;
function shouldUpdateDisplay() returns int update {
    displayUpdateCounter++;
    if (displayUpdateCounter >= 1000) {
        displayUpdateCounter = 0;
        update = 1;
    } else {
        update = 0;
    }
}
```

## State Management Patterns

### Stateless Processing
```impala

function pureProcessor(int input, int param1, int param2) 
returns int output {



    
    int processed = applyGain(input, param1);
    processed = applyFilter(processed, param2);
    return processed;
}
```

**Benefits**:
- Easy to test and debug
- No state corruption issues
- Thread-safe by design
- Composable and reusable

### Managed State Objects
```impala

struct FilterState {
    int lowpass;
    int bandpass;
    int highpass;
    int frequency;
    int resonance;
}

global FilterState leftFilter;
global FilterState rightFilter;

function initFilter(pointer filter) {
    filter->lowpass = 0;
    filter->bandpass = 0;
    filter->highpass = 0;
    filter->frequency = 1000;
    filter->resonance = 100;
}

function processFilter(pointer filter, int input) 
returns int output {



}
```

### Ring Buffer Management
```impala

struct RingBuffer {
    array data[8192];
    int writePos;
    int readPos;
    int size;
}

global RingBuffer delayBuffer;

function initRingBuffer(pointer buffer, int bufferSize) {
    buffer->writePos = 0;
    buffer->readPos = 0;
    buffer->size = bufferSize;
    

    int i;
    for (i = 0 to bufferSize) {
        buffer->data[i] = 0;
    }
}

function writeToBuffer(pointer buffer, int sample) {
    buffer->data[buffer->writePos] = sample;
    buffer->writePos = (buffer->writePos + 1) % buffer->size;
}

function readFromBuffer(pointer buffer, int delayTime) 
returns int sample {
    int readPos = buffer->writePos - delayTime;
    if (readPos < 0) readPos += buffer->size;
    sample = buffer->data[readPos];
}
```

## Performance Optimization Patterns

### CPU Optimization Strategies

#### 1. Minimize Expensive Operations
```impala


function inefficientGain(int input) {
    float gain = itof((int)params[3]) / 255.0;
    return ftoi(itof(input) * gain);
}


global int precalculatedGain = 256;

function update() {

    precalculatedGain = (int)params[3];
}

function efficientGain(int input) {

    return (input * precalculatedGain) >> 8;
}
```

#### 2. Use Lookup Tables
```impala

const int SINE_TABLE_SIZE = 1024;
global int sineTable[SINE_TABLE_SIZE];

function init() {

    int i;
    for (i = 0 to SINE_TABLE_SIZE) {
        float angle = itof(i) * TWO_PI / itof(SINE_TABLE_SIZE);
        sineTable[i] = ftoi(sin(angle) * 2047.0);
    }
}

function fastSine(int phase) returns int value {

    int index = (phase >> 6) & (SINE_TABLE_SIZE - 1);
    value = sineTable[index];
}
```

#### 3. Batch Processing
```impala

const int BATCH_SIZE = 32;
global int processingBatch[BATCH_SIZE];
global int batchIndex = 0;

function process() {
    loop {

        processingBatch[batchIndex] = signal[0];
        batchIndex++;
        
        if (batchIndex >= BATCH_SIZE) {

            processBatch(processingBatch, BATCH_SIZE);
            batchIndex = 0;
        }
        
        yield();
    }
}
```

#### 4. Memory Access Optimization
```impala

function efficientMemoryAccess() {
    const int BLOCK_SIZE = 16;
    array audioBlock[BLOCK_SIZE * 2];
    

    read(clock - 1000, BLOCK_SIZE, audioBlock);
    

    int i;
    for (i = 0 to BLOCK_SIZE) {
        int leftSample = audioBlock[i * 2];
        int rightSample = audioBlock[i * 2 + 1];

    }
}
```

### Memory Optimization Patterns

#### 1. Memory Pool Management
```impala

const int MAX_DELAYS = 8;
const int DELAY_SIZE = 4096;

global array delayPool[MAX_DELAYS * DELAY_SIZE];
global int delayAllocator = 0;

function allocateDelay(int requestedSize) returns int offset {
    if (delayAllocator + requestedSize <= MAX_DELAYS * DELAY_SIZE) {
        offset = delayAllocator;
        delayAllocator += requestedSize;
    } else {
        offset = -1;
    }
}
```

#### 2. Stack-Based Temporary Storage
```impala

function processWithTempStorage() {
    array tempBuffer[64];
    array workspace[32];
    


}
```

#### 3. Memory Layout Optimization
```impala

struct ProcessingState {

    int sampleRate;
    int bufferSize;
    int currentSample;
    

    array leftBuffer[1024];
    array rightBuffer[1024];
    

    int debugFlags;
    array tempStorage[512];
}
```

## Error Handling Patterns

### Defensive Programming
```impala

function safeParameterAccess(int paramIndex) returns int value {
    if (paramIndex < 0 || paramIndex >= 8) {
        trace("Invalid parameter index");
        return 0;
    }
    value = params[paramIndex];
}


function safeAudioOutput(int sample) returns int safeSample {
    if (sample > 2047) {
        safeSample = 2047;
    } else if (sample < -2047) {
        safeSample = -2047;
    } else {
        safeSample = sample;
    }
}


function safeDivide(int numerator, int denominator) returns int result {
    if (denominator == 0) {
        result = 0;
    } else {
        result = numerator / denominator;
    }
}
```

### Graceful Degradation
```impala

function adaptiveProcessing() {
    int cpuUsage = estimateCPULoad();
    
    if (cpuUsage > 80) {

        processLowQuality();
    } else if (cpuUsage > 60) {

        processMediumQuality();
    } else {

        processHighQuality();
    }
}
```

### Error Recovery
```impala
global int errorState = 0;
const int ERROR_NONE = 0;
const int ERROR_OVERFLOW = 1;
const int ERROR_UNDERFLOW = 2;

function detectAndRecoverFromError() {

    if (signal[0] > 3000 || signal[0] < -3000) {
        errorState = ERROR_OVERFLOW;
        signal[0] = 0;
        signal[1] = 0;
        trace("Audio overflow detected - muting");
    }
    

    if (errorState != ERROR_NONE) {

        recoverFromError();
    }
}
```

## Debugging Strategies

### Trace-Based Debugging
```impala

const int DEBUG_LEVEL_NONE = 0;
const int DEBUG_LEVEL_ERROR = 1;
const int DEBUG_LEVEL_INFO = 2;
const int DEBUG_LEVEL_VERBOSE = 3;

global int debugLevel = DEBUG_LEVEL_ERROR;

function debugTrace(int level, string message) {
    if (level <= debugLevel) {
        trace(message);
    }
}

function process() {
    loop {
        debugTrace(DEBUG_LEVEL_VERBOSE, "Processing sample");
        

        
        if (errorCondition) {
            debugTrace(DEBUG_LEVEL_ERROR, "Error in processing");
        }
        
        yield();
    }
}
```

### State Inspection
```impala

global int debugCounter = 0;

function process() {
    loop {

        
        debugCounter++;
        if (debugCounter >= 48000) {
            debugDumpState();
            debugCounter = 0;
        }
        
        yield();
    }
}

function debugDumpState() {
    array buffer[256];
    sprintf(buffer, "State: gain=%d, freq=%d, phase=%d", 
            currentGain, currentFreq, currentPhase);
    trace(buffer);
}
```

### Visual Debugging with LEDs
```impala

function debugWithLEDs() {

    displayLEDs[0] = params[3];
    

    if (isClipping) {
        displayLEDs[1] = 0xFF;
    } else {
        displayLEDs[1] = currentLevel >> 3;
    }
    

    if (errorState != 0) {
        displayLEDs[2] = 0xAA;
    }
}
```

### Performance Monitoring
```impala

global int processStartTime = 0;
global int maxProcessTime = 0;

function process() {
    loop {
        processStartTime = getSampleTime();
        

        
        int processTime = getSampleTime() - processStartTime;
        if (processTime > maxProcessTime) {
            maxProcessTime = processTime;
        }
        

        if (processTime > 100) {
            trace("Processing overrun detected");
        }
        
        yield();
    }
}
```

## Common Architecture Pitfalls

### 1. State Corruption
```impala

global int sharedCounter = 0;

function badFunction1() {
    sharedCounter++;
}


function goodFunction1() {
    int newValue = getSharedCounter() + 1;
    setSharedCounter(newValue);
}
```

### 2. Resource Leaks
```impala

global int bufferAllocated = 0;

function badAllocation() {

    bufferAllocated += 1024;
}


const int MAX_BUFFER_SIZE = 65536;

function goodAllocation(int requestedSize) returns int success {
    if (bufferAllocated + requestedSize <= MAX_BUFFER_SIZE) {
        bufferAllocated += requestedSize;
        success = 1;
    } else {
        success = 0;
    }
}
```

### 3. Timing Assumptions
```impala

global int sampleCounter = 0;

function badTiming() {
    sampleCounter++;
    if (sampleCounter == 48000) {

        sampleCounter = 0;
    }
}


function goodTiming() {
    float samplesPerSecond = getSampleRate();
    if (sampleCounter >= ftoi(samplesPerSecond)) {

        sampleCounter = 0;
    }
}
```

## Best Practices Summary

### Architecture Design
1. **Choose the right patch type**: Full patches for complex processing, mod patches for simple position effects
2. **Separate concerns**: Keep audio processing, parameter handling, and UI updates distinct
3. **Plan state management**: Use clear ownership patterns for global state
4. **Design for testability**: Make functions pure when possible

### Performance
1. **Measure first**: Profile before optimizing
2. **Optimize hot paths**: Focus on per-sample processing loops
3. **Use appropriate data types**: Prefer integers for audio samples, use floating point judiciously
4. **Leverage hardware**: Let Permut8 handle what it does well

### Reliability
1. **Validate inputs**: Check parameter ranges and audio bounds
2. **Handle errors gracefully**: Prefer degraded operation over crashes
3. **Test edge cases**: Zero inputs, extreme parameters, rapid changes
4. **Monitor resource usage**: Track memory and CPU consumption

---
*See also: [Audio Processing Reference](../reference/audio_processing_reference.md), [Core Language Reference](../language/core_language_reference.md)*