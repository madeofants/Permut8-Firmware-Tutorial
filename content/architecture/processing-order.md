# Processing Order - Signal Flow in Permut8 Firmware

Understanding how audio flows through your Permut8 firmware is essential for building effective DSP algorithms. The processing order determines how samples move through your code and when different operations occur.

## Two Processing Models

Permut8 supports two distinct processing approaches that handle signal flow differently:

### Mod Patches: operate1() and operate2()

Mod patches process individual operators within the existing engine. Your code runs once per sample for each active operator:

```impala
function operate1(int inSample) returns int result {
    // Process one sample through operator 1
    int delayed = delayLine[delayPos];
    delayLine[delayPos] = inSample;
    delayPos = (delayPos + 1) % DELAY_LENGTH;
    
    result = (inSample + delayed) >> 1;  // Simple echo (divide by 2)
}

function operate2(int inSample) returns int result {
    // Process one sample through operator 2
    // Runs independently from operate1()
    result = (inSample * feedbackAmount) >> 8;  // Fixed-point multiplication
}
```

**Signal Flow**: Input → operate1() → operate2() → Output

Each function receives the processed output from the previous stage. This creates a serial processing chain where order matters.

### Full Patches: process()

Full patches replace the entire audio engine. Your code controls the complete signal path:

```impala
function process() {
    loop {
        // Read input sample
        int input = signal[0];
        
        // Your complete DSP algorithm here
        int filtered = applyLowpass(input);
        int delayed = addDelay(filtered);
        int finalOutput = applyDynamics(delayed);
        
        // Write output sample
        signal[0] = finalOutput;
        
        yield();  // Process next sample
    }
}
```

**Signal Flow**: Raw Input → Your Complete Algorithm → Raw Output

You control every aspect of processing, from input to output.

## Processing Timing

### Sample-Rate Processing

Both models process at audio sample rate (approximately 48kHz). Each function call processes exactly one sample:

```impala
// This runs 48,000 times per second
function operate1(int inSample) returns int result {
    // Keep processing lightweight!
    result = applySimpleFilter(inSample);
}
```

### Cooperative Multitasking

In full patches, `yield()` is crucial for proper timing:

```impala
function process() {
    loop {
        // Process one sample
        int result = complexAlgorithm(signal[0]);
        signal[0] = result;
        
        yield();  // REQUIRED: Let system process next sample
    }
}
```

Forgetting `yield()` breaks real-time processing.

## Practical Processing Patterns

### Sequential Effects Chain

```impala
function operate1(int input) returns int result {
    // Stage 1: Filter
    result = lowpassFilter(input);
}

function operate2(int filtered) returns int result {
    // Stage 2: Distortion
    result = waveshape(filtered);
}
```

### Parallel Processing

```impala
function process() {
    loop {
        int input = signal[0];
        
        // Split signal for parallel processing
        int dry = input;
        int wet = applyReverb(input);
        
        // Mix parallel paths
        signal[0] = (dry + wet) >> 1;  // Divide by 2
        yield();
    }
}
```

### State Management Between Samples

```impala
global int filterState = 0;

function operate1(int input) returns int result {
    // State persists between samples
    filterState = (filterState + input) >> 1;  // Simple low-pass
    result = filterState;
}
```

### Parameter Integration

```impala
function operate1(int input) returns int result {
    // Use parameter values in processing
    int gain = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int feedback = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    
    // Apply parameter-controlled processing
    int amplified = (input * gain) >> 8;
    result = (amplified * feedback) >> 8;
}
```

### Error Handling and Safety

```impala
function operate1(int input) returns int result {
    // Clip input to valid range
    if (input > 2047) input = 2047;
    else if (input < -2047) input = -2047;
    
    // Process safely
    result = processWithSafety(input);
    
    // Clip output to valid range
    if (result > 2047) result = 2047;
    else if (result < -2047) result = -2047;
}

function processWithSafety(int input) returns int result {
    // Prevent overflow in calculations
    int scaled = input >> 2;  // Scale down to prevent overflow
    int processed = scaled * 3;  // Safe multiplication
    result = processed << 2;  // Scale back up
}
```

### Memory Management in Processing

```impala
// Pre-allocated buffers for processing
global array delayLine[1024];
global int delayPos = 0;
global array tempBuffer[64];

function operate1(int input) returns int result {
    // Use pre-allocated memory efficiently
    delayLine[delayPos] = input;
    
    // Calculate delay output
    int delayedPos = (delayPos - 500) % 1024;
    if (delayedPos < 0) delayedPos = delayedPos + 1024;
    
    int delayed = delayLine[delayedPos];
    delayPos = (delayPos + 1) % 1024;
    
    result = (input + delayed) >> 1;
}
```

### Advanced Routing Patterns

```impala
function process() {
    loop {
        int input = signal[0];
        
        // Multi-tap delay with different processing
        int tap1 = getTapDelay(input, 250);   // 250 samples delay
        int tap2 = getTapDelay(input, 500);   // 500 samples delay
        int tap3 = getTapDelay(input, 1000);  // 1000 samples delay
        
        // Process each tap differently
        int processed1 = applyFilter(tap1);
        int processed2 = applyDistortion(tap2);
        int processed3 = applyModulation(tap3);
        
        // Mix all taps with original
        signal[0] = (input + processed1 + processed2 + processed3) >> 2;
        
        yield();
    }
}

function getTapDelay(int input, int delaySamples) returns int delayed {
    // Implementation would use appropriate delay buffer management
    // This is a conceptual example
    delayed = readDelayLine(delaySamples);
    writeDelayLine(input);
}
```

### Debugging Processing Flow

```impala
global int debugCounter = 0;

function operate1(int input) returns int result {
    // Debug processing every 4800 samples (10x per second at 48kHz)
    debugCounter++;
    if ((debugCounter % 4800) == 0) {
        array debugMsg[64];
        strcpy(debugMsg, "Op1 In: ");
        strcat(debugMsg, intToString(input, 10, 1, tempBuffer));
        trace(debugMsg);
    }
    
    result = processFunction(input);
    
    if ((debugCounter % 4800) == 0) {
        array debugMsg2[64];
        strcpy(debugMsg2, "Op1 Out: ");
        strcat(debugMsg2, intToString(result, 10, 1, tempBuffer));
        trace(debugMsg2);
    }
}
```

## Performance Considerations

### Mod Patches
- **Optimized**: Engine handles complex routing and parameter management
- **Efficient**: Minimal overhead for simple processing
- **Limited**: Restricted to operator-based processing model
- **Reliable**: Engine provides stability and error handling

### Full Patches  
- **Flexible**: Complete control over signal path and processing
- **Powerful**: Can implement any algorithm within timing constraints
- **Responsible**: You must handle all optimizations and error cases
- **Demanding**: Must maintain real-time performance guarantees

### Performance Guidelines
1. **Keep operate1/operate2 lightweight** - Simple operations only
2. **Use pre-allocated memory** - Avoid dynamic allocation in process()
3. **Monitor CPU usage** - Complex algorithms may exceed timing budget
4. **Test edge cases** - Verify performance with extreme parameter values
5. **Profile regularly** - Use trace() to monitor processing times

### Memory Usage Patterns
- **Static allocation**: Pre-allocate all buffers at startup
- **Circular buffers**: Efficient for delay lines and history
- **State variables**: Minimize global state for better cache performance
- **Parameter caching**: Copy frequently-used parameters to locals

## Best Practices Summary

### Signal Flow Design
1. **Plan your processing chain** - Know your signal path before coding
2. **Consider parameter integration** - How controls affect processing
3. **Design for real-time** - Keep algorithms deterministic
4. **Test signal flow** - Verify audio path with known test signals

### Code Organization
1. **Separate concerns** - Different processing stages in different functions
2. **Use clear naming** - Function and variable names reflect purpose
3. **Document signal flow** - Comment the audio path through your code
4. **Handle edge cases** - Plan for silence, full-scale, and parameter extremes

### Debugging Strategies
1. **Use trace() judiciously** - Monitor key processing points
2. **Test incrementally** - Build processing chain step by step
3. **Verify timing** - Ensure yield() placement maintains real-time
4. **Monitor resources** - Track memory and CPU usage

Understanding these processing patterns helps you choose the right approach and structure your code for optimal audio quality and performance. The key is matching your processing requirements to the appropriate model while maintaining real-time constraints.