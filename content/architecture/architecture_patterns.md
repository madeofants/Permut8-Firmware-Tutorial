# Architecture Patterns

## What This Is
Architectural design patterns, lifecycle management, and performance strategies for Permut8 firmware development. Essential concepts for building robust, efficient audio processing systems.

## Patch Architecture Overview

### Full Patch Architecture
**Purpose**: Complete audio processing replacement  
**Control**: Total control over audio signal chain  
**Complexity**: Higher - must handle all audio processing  
**Performance**: Higher CPU usage, but maximum flexibility

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]      // Direct audio I/O
global array params[8]      // Parameter control
global array displayLEDs[4] // Visual feedback

function process() {
    loop {
        // Complete signal processing chain
        int inputLeft = signal[0];
        int inputRight = signal[1];
        
        // Your complete DSP algorithm here
        signal[0] = processedLeft;
        signal[1] = processedRight;
        
        yield();  // Essential - return control
    }
}
```

**When to Use Full Patches**:
- Complex multi-stage effects (reverb, vocoder, granular)
- Real-time analysis and resynthesis
- Complete signal replacement needed
- Custom envelope followers or dynamics
- Advanced modulation routing

### Mod Patch Architecture  
**Purpose**: Modify existing operators  
**Control**: Indirect via memory position manipulation  
**Complexity**: Lower - Permut8 handles audio processing  
**Performance**: Lower CPU usage, leverages hardware optimizations

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array positions[2]   // Memory position control
global array params[8]      // Parameter control
global array displayLEDs[4] // Visual feedback

function operate1() returns int processed {
    // Modify delay line positions
    int delayOffset = calculateDelay();
    
    positions[0] += delayOffset;  // Left channel
    positions[1] += delayOffset;  // Right channel
    
    return 1;  // Signal that we processed the positions
}

function operate2() returns int processed {
    // Second operator can do different processing
    // Often used for stereo effects or parallel processing
    return 1;
}
```

**When to Use Mod Patches**:
- Simple delays and modulation
- Stereo imaging effects  
- Tempo-synced delays
- Position-based effects (flanging, chorusing)
- Lower CPU usage requirements

## Lifecycle Management

### Initialization Phase
```impala
// Called once when firmware loads
function init() {
    // Initialize lookup tables
    buildSineTable();
    buildFilterCoefficients();
    
    // Set initial state
    resetDelayBuffers();
    initializeFilters();
    
    // Configure defaults
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
// Called when parameters change
global int lastParamValues[8] = {-1, -1, -1, -1, -1, -1, -1, -1};

function update() {
    // Check which parameters changed
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
        // Recalculate filter frequency
        updateFilterFrequency(newValue);
    } else if (index == OPERAND_1_LOW_PARAM_INDEX) {
        // Recalculate resonance
        updateFilterResonance(newValue);
    }
    // ... handle other parameters
}
```

**Update Optimization Strategies**:
- Only recalculate when parameters actually change
- Use incremental updates instead of full recalculation
- Cache intermediate calculations
- Smooth parameter changes to avoid artifacts

### Reset Phase
```impala
// Called when reset button pressed or DAW restarts
function reset() {
    // Clear all delay buffers
    clearAllBuffers();
    
    // Reset filter states
    resetFilterMemory();
    
    // Reset phase accumulators
    resetOscillatorPhases();
    
    // Clear any accumulated state
    resetEnvelopeFollowers();
    
    // Re-initialize critical state
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
// Efficient processing loop structure
function process() {
    loop {
        // 1. Read inputs efficiently
        int inputL = signal[0];
        int inputR = signal[1];
        
        // 2. Update time-based state
        updateTimeState();
        
        // 3. Process audio
        processAudioSample(inputL, inputR);
        
        // 4. Update displays (not every sample)
        if (shouldUpdateDisplay()) {
            updateLEDDisplays();
        }
        
        // 5. Essential - return control
        yield();
    }
}

int displayUpdateCounter = 0;
function shouldUpdateDisplay() returns int update {
    displayUpdateCounter++;
    if (displayUpdateCounter >= 1000) {  // Update every 1000 samples
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
// Pure functions - no global state modification
function pureProcessor(int input, int param1, int param2) 
returns int output {
    // All state passed as parameters
    // No side effects
    // Predictable and testable
    
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
// State encapsulation pattern
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
    // Process with encapsulated state
    // All filter state kept together
    // Easier to manage multiple instances
}
```

### Ring Buffer Management
```impala
// Efficient circular buffer pattern
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
    
    // Clear buffer
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
// Avoid per-sample floating point when possible
// Bad: floating point per sample
function inefficientGain(int input) {
    float gain = itof((int)params[3]) / 255.0;
    return ftoi(itof(input) * gain);
}

// Good: pre-calculate in update()
global int precalculatedGain = 256;

function update() {
    // Calculate once when parameter changes
    precalculatedGain = (int)params[3];
}

function efficientGain(int input) {
    // Fast integer multiply and shift
    return (input * precalculatedGain) >> 8;
}
```

#### 2. Use Lookup Tables
```impala
// Pre-computed lookup tables for expensive functions
const int SINE_TABLE_SIZE = 1024;
global int sineTable[SINE_TABLE_SIZE];

function init() {
    // Build table once at startup
    int i;
    for (i = 0 to SINE_TABLE_SIZE) {
        float angle = itof(i) * TWO_PI / itof(SINE_TABLE_SIZE);
        sineTable[i] = ftoi(sin(angle) * 2047.0);
    }
}

function fastSine(int phase) returns int value {
    // Fast table lookup instead of sin() calculation
    int index = (phase >> 6) & (SINE_TABLE_SIZE - 1);  // Scale and wrap
    value = sineTable[index];
}
```

#### 3. Batch Processing
```impala
// Process multiple samples efficiently
const int BATCH_SIZE = 32;
global int processingBatch[BATCH_SIZE];
global int batchIndex = 0;

function process() {
    loop {
        // Collect samples in batch
        processingBatch[batchIndex] = signal[0];
        batchIndex++;
        
        if (batchIndex >= BATCH_SIZE) {
            // Process entire batch at once
            processBatch(processingBatch, BATCH_SIZE);
            batchIndex = 0;
        }
        
        yield();
    }
}
```

#### 4. Memory Access Optimization
```impala
// Sequential memory access pattern
function efficientMemoryAccess() {
    const int BLOCK_SIZE = 16;
    array audioBlock[BLOCK_SIZE * 2];  // Stereo interleaved
    
    // Read block sequentially
    read(clock - 1000, BLOCK_SIZE, audioBlock);
    
    // Process block
    int i;
    for (i = 0 to BLOCK_SIZE) {
        int leftSample = audioBlock[i * 2];
        int rightSample = audioBlock[i * 2 + 1];
        // Process samples...
    }
}
```

### Memory Optimization Patterns

#### 1. Memory Pool Management
```impala
// Pre-allocate memory pools
const int MAX_DELAYS = 8;
const int DELAY_SIZE = 4096;

global array delayPool[MAX_DELAYS * DELAY_SIZE];
global int delayAllocator = 0;

function allocateDelay(int requestedSize) returns int offset {
    if (delayAllocator + requestedSize <= MAX_DELAYS * DELAY_SIZE) {
        offset = delayAllocator;
        delayAllocator += requestedSize;
    } else {
        offset = -1;  // Allocation failed
    }
}
```

#### 2. Stack-Based Temporary Storage
```impala
// Use local arrays for temporary calculations
function processWithTempStorage() {
    array tempBuffer[64];  // Local stack allocation
    array workspace[32];   // Another temporary buffer
    
    // Use for intermediate calculations
    // Automatically freed when function exits
}
```

#### 3. Memory Layout Optimization
```impala
// Group related data for cache efficiency
struct ProcessingState {
    // Frequently accessed together
    int sampleRate;
    int bufferSize;
    int currentSample;
    
    // Audio buffers
    array leftBuffer[1024];
    array rightBuffer[1024];
    
    // Less frequently accessed
    int debugFlags;
    array tempStorage[512];
}
```

## Error Handling Patterns

### Defensive Programming
```impala
// Parameter validation
function safeParameterAccess(int paramIndex) returns int value {
    if (paramIndex < 0 || paramIndex >= 8) {
        trace("Invalid parameter index");
        return 0;  // Safe default
    }
    value = params[paramIndex];
}

// Audio range validation
function safeAudioOutput(int sample) returns int safeSample {
    if (sample > 2047) {
        safeSample = 2047;
    } else if (sample < -2047) {
        safeSample = -2047;
    } else {
        safeSample = sample;
    }
}

// Division by zero protection
function safeDivide(int numerator, int denominator) returns int result {
    if (denominator == 0) {
        result = 0;  // Or some other safe value
    } else {
        result = numerator / denominator;
    }
}
```

### Graceful Degradation
```impala
// Fallback processing when resources limited
function adaptiveProcessing() {
    int cpuUsage = estimateCPULoad();
    
    if (cpuUsage > 80) {
        // Reduce quality to maintain real-time performance
        processLowQuality();
    } else if (cpuUsage > 60) {
        // Medium quality
        processMediumQuality();
    } else {
        // Full quality
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
    // Check for audio overflow
    if (signal[0] > 3000 || signal[0] < -3000) {
        errorState = ERROR_OVERFLOW;
        signal[0] = 0;  // Mute to prevent speaker damage
        signal[1] = 0;
        trace("Audio overflow detected - muting");
    }
    
    // Recovery after some time
    if (errorState != ERROR_NONE) {
        // Gradually unmute after error condition clears
        recoverFromError();
    }
}
```

## Debugging Strategies

### Trace-Based Debugging
```impala
// Conditional debug output
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
        
        // Your processing...
        
        if (errorCondition) {
            debugTrace(DEBUG_LEVEL_ERROR, "Error in processing");
        }
        
        yield();
    }
}
```

### State Inspection
```impala
// Periodic state dumps
global int debugCounter = 0;

function process() {
    loop {
        // Process audio...
        
        debugCounter++;
        if (debugCounter >= 48000) {  // Once per second at 48kHz
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
// Use LEDs for real-time debugging
function debugWithLEDs() {
    // Show parameter values
    displayLEDs[0] = params[3];  // Show knob position
    
    // Show processing state
    if (isClipping) {
        displayLEDs[1] = 0xFF;  // All LEDs for clipping
    } else {
        displayLEDs[1] = currentLevel >> 3;  // Level meter
    }
    
    // Show error conditions
    if (errorState != 0) {
        displayLEDs[2] = 0xAA;  // Alternating pattern for errors
    }
}
```

### Performance Monitoring
```impala
// Simple performance measurement
global int processStartTime = 0;
global int maxProcessTime = 0;

function process() {
    loop {
        processStartTime = getSampleTime();
        
        // Your processing here...
        
        int processTime = getSampleTime() - processStartTime;
        if (processTime > maxProcessTime) {
            maxProcessTime = processTime;
        }
        
        // Report if processing takes too long
        if (processTime > 100) {  // Threshold in samples
            trace("Processing overrun detected");
        }
        
        yield();
    }
}
```

## Common Architecture Pitfalls

### 1. State Corruption
```impala
// Problem: Uncontrolled global state modification
global int sharedCounter = 0;

function badFunction1() {
    sharedCounter++;  // Can conflict with other functions
}

// Solution: Controlled state access
function goodFunction1() {
    int newValue = getSharedCounter() + 1;
    setSharedCounter(newValue);
}
```

### 2. Resource Leaks
```impala
// Problem: Unbounded memory growth
global int bufferAllocated = 0;

function badAllocation() {
    // Keeps allocating without freeing
    bufferAllocated += 1024;
}

// Solution: Bounded resource management
const int MAX_BUFFER_SIZE = 65536;

function goodAllocation(int requestedSize) returns int success {
    if (bufferAllocated + requestedSize <= MAX_BUFFER_SIZE) {
        bufferAllocated += requestedSize;
        success = 1;
    } else {
        success = 0;  // Allocation denied
    }
}
```

### 3. Timing Assumptions
```impala
// Problem: Assuming fixed timing relationships
global int sampleCounter = 0;

function badTiming() {
    sampleCounter++;
    if (sampleCounter == 48000) {  // Assumes 48kHz!
        // Do something once per second
        sampleCounter = 0;
    }
}

// Solution: Sample-rate independent timing
function goodTiming() {
    float samplesPerSecond = getSampleRate();
    if (sampleCounter >= ftoi(samplesPerSecond)) {
        // Correctly handles any sample rate
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
*See also: [Audio Processing Reference](audio_processing_reference.md), [Core Language Reference](core_language_reference.md)*