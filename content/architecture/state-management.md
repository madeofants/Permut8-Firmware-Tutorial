# State Management - Persistent Data in Permut8 Firmware

Effective state management is crucial for building DSP algorithms that remember information between audio samples. Permut8 firmware processes thousands of samples per second, and your code needs to maintain state efficiently across these rapid function calls.

## Global Variables for Persistence

Use `global` variables to store data that persists between function calls:

```impala
global array delayBuffer[1024];
global int writePos = 0;
global int feedbackLevel = 128;

function operate1(int input) returns int result {
    // State persists between samples
    int delayed = delayBuffer[writePos];
    delayBuffer[writePos] = input + ((delayed * feedbackLevel) >> 8);
    
    writePos = (writePos + 1) % 1024;
    result = delayed;
}
```

**Key Point**: Global variables maintain their values across all function calls, making them perfect for delay lines, filter states, and accumulators.

## Initialization Patterns

### Simple Initialization

For basic state, direct assignment and first-call initialization work well:

```impala
global int initialized = 0;
global int filterState = 0;

function operate1(int input) returns int result {
    if (initialized == 0) {
        filterState = input;  // Initialize to first sample
        initialized = 1;
    }
    
    // Simple lowpass filter using fixed-point math
    filterState = ((filterState * 7) + input) >> 3;  // Divide by 8
    result = filterState;
}
```

### Complex State Setup

For larger state structures, use initialization functions:

```impala
global array reverbTaps[8];
global array tapDelays[8] = {47, 97, 149, 211, 281, 359, 443, 541};
global int reverbPos = 0;
global int setupDone = 0;

function setupReverb() {
    // Initialize complex state once
    int i;
    for (i = 0 to 8) {
        reverbTaps[i] = 0;
    }
    setupDone = 1;
}

function operate1(int input) returns int result {
    if (setupDone == 0) {
        setupReverb();
    }
    
    // Use initialized state
    result = processReverb(input);
}

function processReverb(int input) returns int result {
    // Simple reverb implementation using taps
    int output = input;
    int i;
    
    for (i = 0 to 8) {
        int tapIndex = (reverbPos - tapDelays[i]) % 1024;
        if (tapIndex < 0) tapIndex += 1024;
        output += reverbTaps[tapIndex] >> 2;  // Mix in reverb taps
    }
    
    // Store input in reverb buffer
    reverbTaps[reverbPos] = input;
    reverbPos = (reverbPos + 1) % 1024;
    
    result = output >> 1;  // Scale output
}
```

## State Reset and Cleanup

### Parameter-Triggered Reset

Reset state when parameters change significantly:

```impala
global int lastDelayTime = 0;
global array delayBuffer[2048];

function operate1(int input) returns int result {
    int currentDelay = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    // Clear buffer if delay time changed dramatically
    int delayDiff = currentDelay - lastDelayTime;
    if (delayDiff < 0) delayDiff = -delayDiff;  // Absolute value
    
    if (delayDiff > 32) {
        int i;
        for (i = 0 to 2048) {
            delayBuffer[i] = 0;
        }
        lastDelayTime = currentDelay;
        trace("Delay buffer cleared due to parameter change");
    }
    
    // Continue with clean state
    result = applyDelay(input, currentDelay);
}

function applyDelay(int input, int delayTime) returns int result {
    // Simple delay implementation
    int delayIndex = (writePos - delayTime) % 2048;
    if (delayIndex < 0) delayIndex += 2048;
    
    result = delayBuffer[delayIndex];
    delayBuffer[writePos] = input;
    writePos = (writePos + 1) % 2048;
}
```

### Graceful State Transitions

Avoid audio clicks when changing state:

```impala
global int targetGain = 255;
global int currentGain = 255;
global int gainTransitionRate = 1;

function operate1(int input) returns int result {
    // Smooth parameter changes
    targetGain = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    
    if (currentGain != targetGain) {
        // Gradual transition prevents clicks
        int diff = targetGain - currentGain;
        if (diff > gainTransitionRate) {
            currentGain += gainTransitionRate;
        } else if (diff < -gainTransitionRate) {
            currentGain -= gainTransitionRate;
        } else {
            currentGain = targetGain;  // Close enough, snap to target
        }
    }
    
    result = (input * currentGain) >> 8;  // Fixed-point multiplication
}
```

### State Validation and Safety

Ensure state remains within valid bounds:

```impala
global int oscPhase = 0;
global int oscFreq = 440;

function operate1(int input) returns int result {
    // Validate and clamp state variables
    if (oscPhase < 0 || oscPhase >= 1000) {
        oscPhase = 0;  // Reset to safe value
        trace("Oscillator phase reset to safe range");
    }
    
    if (oscFreq < 1 || oscFreq > 1000) {
        oscFreq = 440;  // Reset to safe frequency
        trace("Oscillator frequency reset to safe range");
    }
    
    // Generate oscillator output
    int oscOutput = generateTriangleWave(oscPhase);
    oscPhase = (oscPhase + oscFreq) % 1000;
    
    result = (input + oscOutput) >> 1;  // Mix oscillator with input
}

function generateTriangleWave(int phase) returns int result {
    // Triangle wave: 0-500 rise, 500-1000 fall
    if (phase < 500) {
        result = (phase * 4094) / 500 - 2047;  // Rising edge
    } else {
        result = 2047 - ((phase - 500) * 4094) / 500;  // Falling edge
    }
}
```

## Memory-Efficient State

### Circular Buffers

Manage large state efficiently with wraparound indexing:

```impala
global array buffer[512];
global int readPos = 0;
global int writePos = 256;  // Half buffer delay

function operate1(int input) returns int result {
    // Write new sample
    buffer[writePos] = input;
    
    // Read delayed sample
    int output = buffer[readPos];
    
    // Advance pointers with wraparound
    readPos = (readPos + 1) % 512;
    writePos = (writePos + 1) % 512;
    
    result = output;
}
```

### Variable Delay with Interpolation

Implement smooth delay time changes:

```impala
global array delayLine[1024];
global int writeIndex = 0;

function operate1(int input) returns int result {
    // Write input to delay line
    delayLine[writeIndex] = input;
    
    // Get delay time from parameter (0-1023 samples)
    int delayTime = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 1023) >> 8;
    
    // Calculate read position with fractional part
    int readPos = writeIndex - delayTime;
    if (readPos < 0) readPos += 1024;
    
    // Linear interpolation for smooth delay changes
    int nextPos = (readPos + 1) % 1024;
    int sample1 = delayLine[readPos];
    int sample2 = delayLine[nextPos];
    
    // Simple interpolation (could be enhanced with fractional delay)
    result = (sample1 + sample2) >> 1;
    
    writeIndex = (writeIndex + 1) % 1024;
}
```

### Packed State

Use bit manipulation to store multiple values efficiently:

```impala
global int packedState = 0;

function storePhase(int phase) {
    // Store 16-bit phase in upper bits (limit to 16-bit range)
    if (phase > 65535) phase = 65535;
    if (phase < 0) phase = 0;
    packedState = (packedState & 0xFFFF) | (phase << 16);
}

function storeAmplitude(int amp) {
    // Store 16-bit amplitude in lower bits
    if (amp > 65535) amp = 65535;
    if (amp < 0) amp = 0;
    packedState = (packedState & 0xFFFF0000) | (amp & 0xFFFF);
}

function getPhase() returns int phase {
    phase = (packedState >> 16) & 0xFFFF;
}

function getAmplitude() returns int amplitude {
    amplitude = packedState & 0xFFFF;
}

function operate1(int input) returns int result {
    // Use packed state for oscillator
    int phase = getPhase();
    int amplitude = getAmplitude();
    
    // Update amplitude based on parameter
    amplitude = (int)params[OPERAND_1_HIGH_PARAM_INDEX] << 8;  // Scale to 16-bit
    storeAmplitude(amplitude);
    
    // Generate output and advance phase
    int oscOutput = (generateSineApprox(phase) * amplitude) >> 16;
    phase = (phase + 100) % 65536;  // Advance phase
    storePhase(phase);
    
    result = (input + oscOutput) >> 1;
}

function generateSineApprox(int phase) returns int result {
    // Simple sine approximation using triangle wave
    int scaled = (phase * 1000) / 65536;  // Scale to 0-999
    if (scaled < 250) {
        result = (scaled * 4000) / 250;  // 0 to 1000
    } else if (scaled < 750) {
        result = 1000 - ((scaled - 250) * 4000) / 500;  // 1000 to -1000
    } else {
        result = -1000 + ((scaled - 750) * 4000) / 250;  // -1000 to 0
    }
}
```

## Multi-Stage State Management

### Filter Chains with State

Manage state across multiple processing stages:

```impala
// Filter chain state
global int lpfState1 = 0;
global int lpfState2 = 0;
global int hpfState1 = 0;
global int hpfStateInput = 0;

function operate1(int input) returns int result {
    // Multi-stage filter with state management
    int stage1 = lowpassFilter(input, &lpfState1);
    int stage2 = lowpassFilter(stage1, &lpfState2);
    int stage3 = highpassFilter(stage2, &hpfState1, &hpfStateInput);
    
    result = stage3;
}

function lowpassFilter(int input, int state) returns int result {
    // Simple lowpass with state update
    int newState = (state * 7 + input) >> 3;  // Update state
    // Note: In real implementation, would need to update global state
    result = newState;
}

function highpassFilter(int input, int lastOutput, int lastInput) returns int result {
    // Highpass filter: output = input - lastInput + 0.95 * lastOutput
    int diff = input - lastInput;
    result = diff + ((lastOutput * 243) >> 8);  // 0.95 ≈ 243/256
    
    // Note: In real implementation, would update global state variables
}
```

### State Debugging and Monitoring

Debug state changes effectively:

```impala
global int debugCounter = 0;
global int stateChangeCount = 0;

function operate1(int input) returns int result {
    int oldState = filterState;
    
    // Process with state change
    filterState = updateFilterState(input);
    
    // Monitor state changes for debugging
    if (filterState != oldState) {
        stateChangeCount++;
    }
    
    // Debug output every second (48000 samples)
    debugCounter++;
    if ((debugCounter % 48000) == 0) {
        array debugMsg[128];
        array tempBuf[32];
        
        strcpy(debugMsg, "State changes: ");
        strcat(debugMsg, intToString(stateChangeCount, 10, 1, tempBuf));
        strcat(debugMsg, " Filter: ");
        strcat(debugMsg, intToString(filterState, 10, 1, tempBuf));
        
        trace(debugMsg);
        stateChangeCount = 0;  // Reset counter
    }
    
    result = filterState;
}
```

## Best Practices

### Memory Management
- **Pre-allocate state**: Use global arrays sized for worst-case scenarios
- **Minimize state size**: Large arrays consume limited firmware memory
- **Use circular buffers**: Efficient for delay lines and history buffers
- **Pack related data**: Combine small state variables when possible

### Performance Optimization
- **Initialize once**: Set up complex state only when needed, not every sample
- **Cache frequently accessed state**: Copy global state to locals in tight loops
- **Use efficient data types**: Prefer int over float for state variables
- **Minimize state updates**: Only update state when values actually change

### Audio Quality
- **Smooth transitions**: Always interpolate when changing significant state to avoid audio artifacts
- **Validate state bounds**: Ensure state variables remain within valid ranges
- **Handle parameter changes gracefully**: Reset or transition state appropriately when parameters change
- **Test edge cases**: Verify state behavior with extreme parameter values

### Debugging and Maintenance
- **Add state validation**: Check for invalid state values and reset safely
- **Include debug monitoring**: Track state changes for troubleshooting
- **Document state relationships**: Comment how state variables interact
- **Plan reset strategies**: Define when and how to reset state cleanly

### Real-Time Constraints
- **Avoid complex initialization**: Keep per-sample state updates lightweight
- **Use deterministic algorithms**: Ensure state updates don't vary in execution time
- **Plan for interruption**: State should remain valid if processing is interrupted
- **Consider memory alignment**: Organize state for efficient memory access

## Common State Management Patterns

### Delay Line State
```impala
global array delayMem[2048];
global int delayWrite = 0;

function delayReadWrite(int input, int delayTime) returns int output {
    int readPos = (delayWrite - delayTime) % 2048;
    if (readPos < 0) readPos += 2048;
    
    output = delayMem[readPos];
    delayMem[delayWrite] = input;
    delayWrite = (delayWrite + 1) % 2048;
}
```

### Filter State
```impala
global int filter1State = 0;
global int filter2State = 0;

function biquadChain(int input) returns int output {
    filter1State = ((filter1State * 15) + input) >> 4;  // Lowpass
    filter2State = input - filter1State + ((filter2State * 15) >> 4);  // Highpass
    output = filter2State;
}
```

### Oscillator State
```impala
global int oscPhase = 0;
global int oscRate = 100;

function oscillatorStep() returns int output {
    output = generateWave(oscPhase);
    oscPhase = (oscPhase + oscRate) % 1000;
}
```

Proper state management ensures your DSP algorithms sound smooth, respond predictably to parameter changes, and maintain stable operation across millions of samples processed per second.