# Impala Memory Model for Real-Time Audio Processing

## Introduction

Impala's memory model is specifically designed for real-time audio processing on resource-constrained hardware. Understanding how Impala manages memory is crucial for developing efficient, reliable, and performant firmware for the Permut8 platform.

**Core Philosophy**: Predictable, deterministic memory behavior with zero-overhead abstractions for real-time audio requirements.

### **Permut8's Unique Memory Architecture**

Beyond standard memory management, Permut8 provides a specialized **128-kiloword delay memory system** that is central to its audio processing capabilities:

**128k Delay Memory**:
- **Dedicated audio buffer** separate from program memory
- **Hardware-managed write position** (red dot) - where incoming audio is stored
- **Operator-controlled read positions** (green dots) - where audio is played back from  
- **Foundation of all effects** - delays, pitch shifting, modulation, granular processing

**Two Approaches to Memory**:
1. **Original Operator System**: Use hardware-managed delay memory with built-in operators
2. **Custom Firmware**: Manage your own memory regions with manual allocation

This document covers general Impala memory management. For delay memory specifics, see [Understanding Permut8 Operators](../user-guides/tutorials/understanding-permut8-operators.md).

## Memory Architecture Overview

### Impala Memory Regions

Impala organizes memory into distinct regions, each optimized for specific usage patterns in real-time audio processing:

```
┌─────────────────────────────────────┐
│          Program Memory             │ ← Code, constants, string literals
│        (Read-Only Flash)            │
├─────────────────────────────────────┤
│        Global Data Region           │ ← Global variables, static arrays
│      (Static Allocation)            │
├─────────────────────────────────────┤
│         Stack Region                │ ← Function parameters, local variables
│     (Automatic Management)          │
├─────────────────────────────────────┤
│        Audio Buffer Region          │ ← signal[], delay memory
│    (Hardware-Mapped Memory)         │
├─────────────────────────────────────┤
│      Parameter Region               │ ← params[] array, control values
│   (Live Hardware Interface)         │
├─────────────────────────────────────┤
│       Display Region                │ ← displayLEDs[] array
│    (Output Hardware Interface)      │
└─────────────────────────────────────┘
```

### Memory Region Characteristics

| Region | Allocation Type | Access Speed | Typical Use | Size Limit |
|--------|----------------|--------------|-------------|-------------|
| **Program** | Compile-time | Fast | Code, constants | 32KB |
| **Global** | Compile-time | Fast | Static data, lookup tables | 8KB |
| **Stack** | Runtime (automatic) | Very Fast | Local variables, parameters | 4KB |
| **Audio Buffer** | Hardware-mapped | Ultra Fast | Real-time audio processing | 2KB |
| **Parameter** | Hardware-mapped | Medium | Control interface | 512B |
| **Display** | Hardware-mapped | Slow | Visual feedback | 256B |

## Static Memory Management

### Global Variable Allocation

Impala allocates global variables in the Global Data Region at compile time, ensuring predictable memory layout:

```impala
// Global arrays - allocated at compile time in Global Data Region
global array delayBuffer[1024];
global array filterCoefficients[128];
global array lookupTable[256];

// Global state variables
global int sampleRate = 48000;
global int bufferIndex = 0;
global int currentGain = 128;
```

### Static Array Management

**Fixed-Size Arrays (Recommended):**
```impala
// Compile-time size determination - optimal for real-time audio
global array delayLine[2048];
global array windowFunction[512];
global array frequencyBins[256];

function initializeArrays() {
    // Initialize delay line to zero
    int i;
    for (i = 0 to 2048) {
        delayLine[i] = 0;
    }
    
    // Pre-calculate window function (Hanning window)
    for (i = 0 to 512) {
        int n = i;
        int N = 512;
        // Fixed-point calculation: 0.5 * (1 - cos(2*pi*n/(N-1)))
        int angle = (n * 6283) / (N - 1);  // 2*pi scaled by 1000
        int cosValue = fastCos(angle);     // Returns -1000 to 1000
        windowFunction[i] = 500 - (cosValue >> 1);  // Scale to 0-1000
    }
}

// Fast cosine approximation using lookup table
readonly array cosineTable[360] = {
    1000, 999, 996, 991, 985, 978, 970, 961, 951, 940,
    // ... complete 360-value cosine table scaled by 1000
};

function fastCos(int scaledAngle) returns int result {
    int degrees = (scaledAngle * 360) / 6283;  // Convert to degrees
    degrees = degrees % 360;  // Wrap to 0-359
    if (degrees < 0) degrees += 360;
    result = cosineTable[degrees];
}
```

**Pre-allocated Buffers (Best Practice):**
```impala
// Pre-allocated with maximum expected size
global array maxTempBuffer[4096];
global int tempBufferInUse = 0;

function getTempBuffer(int neededSize) returns array result[4096] {
    if (neededSize <= 4096 && tempBufferInUse == 0) {
        tempBufferInUse = 1;  // Mark as in use
        return maxTempBuffer;
    }
    // Handle error case - return smaller safe buffer
    return maxTempBuffer;  // Caller must check size
}

function releaseTempBuffer() {
    tempBufferInUse = 0;  // Mark as available
}
```

## Stack Memory Management

### Function Parameter Handling

Impala manages function parameters efficiently on the stack:

```impala
// Pass by value - copies data to stack (fast for small types)
function processSample(int input, int gain) returns int result {
    int processed = (input * gain) >> 8;  // Fixed-point multiplication
    result = processed;
}

// Pass arrays by reference - efficient for large data
function processBuffer(array buffer[1024], int length) {
    int i;
    for (i = 0 to length) {
        buffer[i] = applyFilter(buffer[i]);
    }
}

// Process array sections efficiently
function processSection(array samples[512], int startIndex, int endIndex) {
    int i;
    for (i = startIndex to endIndex) {
        samples[i] = saturate(samples[i] * 3 >> 1);  // 1.5x gain
    }
}
```

### Local Variable Optimization

**Stack-Friendly Patterns:**
```impala
function efficientProcessing() {
    // Small local variables - minimal stack impact
    int gain = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int feedback = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    int mix = (int)params[SWITCHES_PARAM_INDEX];
    
    // Local arrays - use sparingly, prefer global allocation
    array tempCoeffs[8];
    calculateFilterCoeffs(tempCoeffs, gain);
    
    // Process using efficient local variables
    int i;
    for (i = 0 to 2) {  // Process stereo
        int input = signal[i];
        int filtered = applyBiquad(input, tempCoeffs);
        signal[i] = (input * (255 - mix) + filtered * mix) >> 8;
    }
}
```

**Stack Overflow Prevention:**
```impala
// Avoid large local arrays - causes stack overflow
function badStackUsage() {
    // DON'T DO THIS - 8KB array overflows 4KB stack
    array hugeBuffer[4096];  // STACK OVERFLOW!
    // ... processing
}

// Instead, use global allocation
global array largeWorkBuffer[4096];

function goodStackUsage() {
    // Use pre-allocated global buffer
    clearBuffer(largeWorkBuffer);
    // ... processing using largeWorkBuffer
}

function clearBuffer(array buffer[4096]) {
    int i;
    for (i = 0 to 4096) {
        buffer[i] = 0;
    }
}
```

## Memory Safety Mechanisms

### Bounds Checking

Impala provides compile-time and runtime bounds checking for memory safety:

```impala
global array delayBuffer[1024];
global int delayIndex = 0;

function safeDelayAccess() {
    // Compile-time bounds checking - array size known
    delayBuffer[512] = signal[0];  // OK - within bounds
    // delayBuffer[1024] = signal[0];  // COMPILE ERROR - out of bounds
    
    // Runtime bounds checking for dynamic indices
    if (delayIndex < 1024) {
        int delayedSample = delayBuffer[delayIndex];
        delayBuffer[delayIndex] = signal[0];
        delayIndex = (delayIndex + 1) % 1024;
        signal[0] = delayedSample;
    }
}
```

### Safe Array Access Patterns

```impala
// Safe array access with bounds validation
function safeArrayAccess(array buffer[1024], int index, int value) {
    // Always validate index before access
    if (index >= 0 && index < 1024) {
        buffer[index] = value;
    } else {
        trace("ERROR: Array index out of bounds");
        // Handle error gracefully
    }
}

// Circular buffer with automatic wrapping
function circularBufferAccess(array buffer[512], int index, int value) {
    // Ensure positive index and wrap
    int safeIndex = index % 512;
    if (safeIndex < 0) safeIndex += 512;
    buffer[safeIndex] = value;
}
```

## Memory Layout Optimization

### Cache-Friendly Data Structures

**Structure of Arrays (SoA) Pattern:**
```impala
// Efficient for sequential processing and cache locality
global array leftSamples[512];
global array rightSamples[512];
global array leftHistory[64];
global array rightHistory[64];

function processStereoSoA() {
    // Process left channel with good cache locality
    int i;
    for (i = 0 to 512) {
        leftSamples[i] = applyFilter(leftSamples[i], leftHistory);
    }
    
    // Process right channel with good cache locality
    for (i = 0 to 512) {
        rightSamples[i] = applyFilter(rightSamples[i], rightHistory);
    }
}
```

**Interleaved Stereo Processing:**
```impala
// Efficient when processing samples together
global array stereoBuffer[1024];  // Interleaved L,R,L,R...

function processStereoInterleaved() {
    int frameCount = 512;  // 512 stereo frames = 1024 samples
    int i;
    for (i = 0 to frameCount) {
        int leftIndex = i * 2;
        int rightIndex = i * 2 + 1;
        
        // Process left and right together
        int processedLeft = applyLeftEffect(stereoBuffer[leftIndex]);
        int processedRight = applyRightEffect(stereoBuffer[rightIndex]);
        
        // Apply cross-channel effects
        stereoBuffer[leftIndex] = processedLeft + (processedRight >> 4);  // 6% crosstalk
        stereoBuffer[rightIndex] = processedRight + (processedLeft >> 4);
    }
}
```

### Memory Alignment and Access Patterns

```impala
// Sequential Access (Fastest)
function sequentialProcessing(array buffer[1024]) {
    // Optimal memory access pattern
    int i;
    for (i = 0 to 1024) {
        buffer[i] = applyProcessing(buffer[i]);
    }
}

// Block Processing (Optimal for Complex Operations)
function blockProcessing(array buffer[1024]) {
    const int BLOCK_SIZE = 64;
    int blockCount = 1024 / BLOCK_SIZE;  // 16 blocks
    
    int blockIdx;
    for (blockIdx = 0 to blockCount) {
        int blockStart = blockIdx * BLOCK_SIZE;
        
        // Process entire block with good cache locality
        applyComplexProcessing(buffer, blockStart, BLOCK_SIZE);
    }
}

function applyComplexProcessing(array buffer[1024], int start, int length) {
    int i;
    for (i = start to start + length) {
        // Complex processing on contiguous memory block
        buffer[i] = complexAlgorithm(buffer[i]);
    }
}
```

## Performance Optimization Patterns

### Memory Pool Implementation

```impala
// Custom memory pool for temporary allocations
global array memoryPool[8192];
global array freeBlocks[32];  // Track which blocks are free
global int blockSize = 256;   // Each block is 256 bytes
global int blockCount = 32;   // 8192 / 256 = 32 blocks

function initMemoryPool() {
    int i;
    // Mark all blocks as free
    for (i = 0 to 32) {
        freeBlocks[i] = 1;  // 1 = free, 0 = allocated
    }
}

function allocateFromPool() returns int blockIndex {
    // Find first free block
    int i;
    for (i = 0 to 32) {
        if (freeBlocks[i] == 1) {
            freeBlocks[i] = 0;  // Mark as allocated
            return i;
        }
    }
    return -1;  // Pool exhausted
}

function freeToPool(int blockIndex) {
    if (blockIndex >= 0 && blockIndex < 32) {
        freeBlocks[blockIndex] = 1;  // Mark as free
    }
}

function getPoolBlock(int blockIndex, array result[256]) {
    if (blockIndex >= 0 && blockIndex < 32) {
        int startOffset = blockIndex * blockSize;
        int i;
        for (i = 0 to 256) {
            result[i] = memoryPool[startOffset + i];
        }
    }
}
```

## Real-Time Memory Patterns

### Lock-Free Circular Buffers

```impala
// Single-producer, single-consumer lock-free buffer
global array circularData[2048];
global int writeIndex = 0;
global int readIndex = 0;

function writeSample(int sample) returns int success {
    int nextWrite = (writeIndex + 1) % 2048;
    
    // Check if buffer is full (would overwrite unread data)
    if (nextWrite == readIndex) {
        return 0;  // Buffer full
    }
    
    circularData[writeIndex] = sample;
    writeIndex = nextWrite;  // Atomic on Permut8
    return 1;  // Success
}

function readSample() returns int sample {
    // Check if buffer is empty
    if (readIndex == writeIndex) {
        return 0;  // Buffer empty - return silence
    }
    
    int sample = circularData[readIndex];
    readIndex = (readIndex + 1) % 2048;
    return sample;
}

function getBufferLevel() returns int level {
    if (writeIndex >= readIndex) {
        return writeIndex - readIndex;
    } else {
        return (2048 - readIndex) + writeIndex;
    }
}
```

### Zero-Copy Buffer Management

```impala
// Efficient buffer passing without copying
global array inputBuffer[512];
global array outputBuffer[512];
global int processingComplete = 0;

function setupZeroCopy() {
    // Just mark buffers as ready - no data copying
    processingComplete = 0;
}

function processZeroCopy() {
    // Process directly from input to output
    int i;
    for (i = 0 to 512) {
        outputBuffer[i] = applyEffect(inputBuffer[i]);
    }
    processingComplete = 1;
}

function swapBuffers() {
    // Swap input and output for ping-pong processing
    array tempBuffer[512];
    int i;
    
    // Copy output to temp
    for (i = 0 to 512) {
        tempBuffer[i] = outputBuffer[i];
    }
    
    // Copy input to output
    for (i = 0 to 512) {
        outputBuffer[i] = inputBuffer[i];
    }
    
    // Copy temp to input
    for (i = 0 to 512) {
        inputBuffer[i] = tempBuffer[i];
    }
}
```

## Debugging Memory Issues

### Memory Usage Monitoring

```impala
// Runtime memory usage tracking
global int stackHighWaterMark = 0;
global int poolAllocations = 0;
global int poolDeallocations = 0;
global int bufferOverrunCount = 0;

function checkStackUsage() returns int usage {
    // Estimate stack usage (platform-specific implementation)
    int currentUsage = getApproximateStackUsage();
    
    if (currentUsage > stackHighWaterMark) {
        stackHighWaterMark = currentUsage;
    }
    
    // Alert if approaching stack limit (4KB = 4096 bytes)
    if (currentUsage > 3276) {  // 80% usage warning
        displayLEDs[0] = 0xFF;  // Red LED warning
        trace("WARNING: High stack usage detected");
    }
    
    return currentUsage;
}

// Platform-specific stack usage estimation
function getApproximateStackUsage() returns int estimation {
    // This is a simplified estimation
    // Actual implementation would use platform-specific methods
    return 1024;  // Placeholder value
}
```

### Buffer Overflow Detection

```impala
// Guard pattern implementation
global int guardPrefix = 0xDEAD;
global array protectedData[1024];
global int guardSuffix = 0xBEEF;

function initGuardedBuffer() {
    guardPrefix = 0xDEAD;
    guardSuffix = 0xBEEF;
    
    // Initialize data to zero
    int i;
    for (i = 0 to 1024) {
        protectedData[i] = 0;
    }
}

function checkBufferIntegrity() returns int isValid {
    if (guardPrefix != 0xDEAD) {
        bufferOverrunCount = bufferOverrunCount + 1;
        displayLEDs[1] = 0xFF;  // Orange LED - prefix corruption
        trace("ERROR: Buffer prefix corrupted");
        return 0;
    }
    
    if (guardSuffix != 0xBEEF) {
        bufferOverrunCount = bufferOverrunCount + 1;
        displayLEDs[2] = 0xFF;  // Yellow LED - suffix corruption
        trace("ERROR: Buffer suffix corrupted");
        return 0;
    }
    
    return 1;  // Buffer is intact
}
```

### Memory Leak Detection

```impala
// Allocation tracking for debugging
global int totalAllocations = 0;
global int totalDeallocations = 0;
global int currentAllocations = 0;
global int peakAllocations = 0;

function trackAllocation() {
    totalAllocations = totalAllocations + 1;
    currentAllocations = currentAllocations + 1;
    
    if (currentAllocations > peakAllocations) {
        peakAllocations = currentAllocations;
    }
    
    // Update LED display with allocation count
    displayLEDs[3] = currentAllocations;
}

function trackDeallocation() {
    totalDeallocations = totalDeallocations + 1;
    if (currentAllocations > 0) {
        currentAllocations = currentAllocations - 1;
    }
}

function checkMemoryLeaks() returns int hasLeaks {
    int leakedAllocations = totalAllocations - totalDeallocations;
    
    if (leakedAllocations > 0) {
        trace("WARNING: Memory leaks detected");
        return 1;  // Has leaks
    }
    
    return 0;  // No leaks
}
```

## Best Practices Summary

### Memory Allocation Guidelines

1. **Prefer Static Allocation**: Use global arrays and compile-time sizing for predictable memory usage
2. **Minimize Stack Usage**: Keep local variables small, avoid large local arrays  
3. **Use Memory Pools**: For occasional dynamic needs, implement custom pools rather than general allocation
4. **Plan Memory Layout**: Organize data by access patterns and frequency
5. **Validate Array Access**: Always check bounds for dynamic indices

### Performance Optimization Rules

1. **Sequential Access First**: Design algorithms around linear memory access when possible
2. **Cache-Friendly Patterns**: Group related data together, process in blocks
3. **Minimize Indirection**: Avoid complex pointer arithmetic in audio processing loops
4. **Pre-calculate Addresses**: Cache frequently-used array indices
5. **Zero-Copy Techniques**: Process data in-place when safe

### Safety and Debugging Practices

1. **Enable Bounds Checking**: Validate array indices in debug builds
2. **Implement Guard Patterns**: Detect buffer overflows with guard values
3. **Monitor Resource Usage**: Track stack, pool, and buffer usage
4. **Test Memory Limits**: Validate behavior under maximum memory load conditions
5. **Profile Memory Access**: Identify and optimize memory hotspots

### Real-Time Constraints

1. **No Dynamic Allocation**: Avoid runtime memory allocation in audio processing code
2. **Predictable Access Patterns**: Use consistent memory access patterns for deterministic timing
3. **Lock-Free Data Structures**: Use atomic operations and careful ordering for thread safety
4. **Pre-allocated Buffers**: Size all buffers for worst-case scenarios at compile time
5. **Efficient Buffer Management**: Implement circular buffers for real-time data flow

## Conclusion

Impala's memory model provides the foundation for building efficient, safe, and predictable real-time audio processing systems. By understanding and following these memory management principles, developers can create firmware that maximizes the Permut8's capabilities while maintaining the strict timing requirements of professional audio applications.

The key to successful memory management in Impala is embracing the constraints of real-time audio processing: predictable allocation, efficient access patterns, and robust safety mechanisms. These constraints, rather than limiting creativity, provide the structure needed to build reliable, high-performance audio processing systems.