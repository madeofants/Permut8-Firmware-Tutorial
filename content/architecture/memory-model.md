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

global array delayBuffer[1024];
global array filterCoefficients[128];
global array lookupTable[256];


global int sampleRate = 48000;
global int bufferIndex = 0;
global int currentGain = 128;
```

### Static Array Management

**Fixed-Size Arrays (Recommended):**
```impala

global array delayLine[2048];
global array windowFunction[512];
global array frequencyBins[256];

function initializeArrays() {

    int i;
    for (i = 0 to 2048) {
        delayLine[i] = 0;
    }
    

    for (i = 0 to 512) {
        int n = i;
        int N = 512;

        int angle = (n * 6283) / (N - 1);
        int cosValue = fastCos(angle);
        windowFunction[i] = 500 - (cosValue >> 1);
    }
}


readonly array cosineTable[360] = {
    1000, 999, 996, 991, 985, 978, 970, 961, 951, 940,

};

function fastCos(int scaledAngle) returns int result {
    int degrees = (scaledAngle * 360) / 6283;
    degrees = degrees % 360;
    if (degrees < 0) degrees = degrees + 360;
    result = cosineTable[degrees];
}
```

**Pre-allocated Buffers (Best Practice):**
```impala

global array maxTempBuffer[4096];
global int tempBufferInUse = 0;

function getTempBuffer(int neededSize) returns array result[4096] {
    if (neededSize <= 4096 && tempBufferInUse == 0) {
        tempBufferInUse = 1;
        return maxTempBuffer;
    }

    return maxTempBuffer;
}

function releaseTempBuffer() {
    tempBufferInUse = 0;
}
```

## Stack Memory Management

### Function Parameter Handling

Impala manages function parameters efficiently on the stack:

```impala

function processSample(int input, int gain) returns int result {
    int processed = (input * gain) >> 8;
    result = processed;
}


function processBuffer(array buffer[1024], int length) {
    int i;
    for (i = 0 to length) {
        buffer[i] = applyFilter(buffer[i]);
    }
}


function processSection(array samples[512], int startIndex, int endIndex) {
    int i;
    for (i = startIndex to endIndex) {
        samples[i] = saturate(samples[i] * 3 >> 1);
    }
}
```

### Local Variable Optimization

**Stack-Friendly Patterns:**
```impala
function efficientProcessing() {

    int gain = (int)params[OPERAND_1_HIGH_PARAM_INDEX];
    int feedback = (int)params[OPERAND_1_LOW_PARAM_INDEX];
    int mix = (int)params[SWITCHES_PARAM_INDEX];
    

    array tempCoeffs[8];
    calculateFilterCoeffs(tempCoeffs, gain);
    

    int i;
    for (i = 0 to 2) {
        int input = signal[i];
        int filtered = applyBiquad(input, tempCoeffs);
        signal[i] = (input * (255 - mix) + filtered * mix) >> 8;
    }
}
```

**Stack Overflow Prevention:**
```impala

function badStackUsage() {

    array hugeBuffer[4096];

}


global array largeWorkBuffer[4096];

function goodStackUsage() {

    clearBuffer(largeWorkBuffer);

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

    delayBuffer[512] = signal[0];

    

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

function safeArrayAccess(array buffer[1024], int index, int value) {

    if (index >= 0 && index < 1024) {
        buffer[index] = value;
    } else {
        trace("ERROR: Array index out of bounds");

    }
}


function circularBufferAccess(array buffer[512], int index, int value) {

    int safeIndex = index % 512;
    if (safeIndex < 0) safeIndex = safeIndex + 512;
    buffer[safeIndex] = value;
}
```

## Memory Layout Optimization

### Cache-Friendly Data Structures

**Structure of Arrays (SoA) Pattern:**
```impala

global array leftSamples[512];
global array rightSamples[512];
global array leftHistory[64];
global array rightHistory[64];

function processStereoSoA() {

    int i;
    for (i = 0 to 512) {
        leftSamples[i] = applyFilter(leftSamples[i], leftHistory);
    }
    

    for (i = 0 to 512) {
        rightSamples[i] = applyFilter(rightSamples[i], rightHistory);
    }
}
```

**Interleaved Stereo Processing:**
```impala

global array stereoBuffer[1024];

function processStereoInterleaved() {
    int frameCount = 512;
    int i;
    for (i = 0 to frameCount) {
        int leftIndex = i * 2;
        int rightIndex = i * 2 + 1;
        

        int processedLeft = applyLeftEffect(stereoBuffer[leftIndex]);
        int processedRight = applyRightEffect(stereoBuffer[rightIndex]);
        

        stereoBuffer[leftIndex] = processedLeft + (processedRight >> 4);
        stereoBuffer[rightIndex] = processedRight + (processedLeft >> 4);
    }
}
```

### Memory Alignment and Access Patterns

```impala

function sequentialProcessing(array buffer[1024]) {

    int i;
    for (i = 0 to 1024) {
        buffer[i] = applyProcessing(buffer[i]);
    }
}


function blockProcessing(array buffer[1024]) {
    const int BLOCK_SIZE = 64;
    int blockCount = 1024 / BLOCK_SIZE;
    
    int blockIdx;
    for (blockIdx = 0 to blockCount) {
        int blockStart = blockIdx * BLOCK_SIZE;
        

        applyComplexProcessing(buffer, blockStart, BLOCK_SIZE);
    }
}

function applyComplexProcessing(array buffer[1024], int start, int length) {
    int i;
    for (i = start to start + length) {

        buffer[i] = complexAlgorithm(buffer[i]);
    }
}
```

## Performance Optimization Patterns

### Memory Pool Implementation

```impala

global array memoryPool[8192];
global array freeBlocks[32];
global int blockSize = 256;
global int blockCount = 32;

function initMemoryPool() {
    int i;

    for (i = 0 to 32) {
        freeBlocks[i] = 1;
    }
}

function allocateFromPool() returns int blockIndex {

    int i;
    for (i = 0 to 32) {
        if (freeBlocks[i] == 1) {
            freeBlocks[i] = 0;
            return i;
        }
    }
    return -1;
}

function freeToPool(int blockIndex) {
    if (blockIndex >= 0 && blockIndex < 32) {
        freeBlocks[blockIndex] = 1;
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

global array circularData[2048];
global int writeIndex = 0;
global int readIndex = 0;

function writeSample(int sample) returns int success {
    int nextWrite = (writeIndex + 1) % 2048;
    

    if (nextWrite == readIndex) {
        return 0;
    }
    
    circularData[writeIndex] = sample;
    writeIndex = nextWrite;
    return 1;
}

function readSample() returns int sample {

    if (readIndex == writeIndex) {
        return 0;
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

global array inputBuffer[512];
global array outputBuffer[512];
global int processingComplete = 0;

function setupZeroCopy() {

    processingComplete = 0;
}

function processZeroCopy() {

    int i;
    for (i = 0 to 512) {
        outputBuffer[i] = applyEffect(inputBuffer[i]);
    }
    processingComplete = 1;
}

function swapBuffers() {

    array tempBuffer[512];
    int i;
    

    for (i = 0 to 512) {
        tempBuffer[i] = outputBuffer[i];
    }
    

    for (i = 0 to 512) {
        outputBuffer[i] = inputBuffer[i];
    }
    

    for (i = 0 to 512) {
        inputBuffer[i] = tempBuffer[i];
    }
}
```

## Debugging Memory Issues

### Memory Usage Monitoring

```impala

global int stackHighWaterMark = 0;
global int poolAllocations = 0;
global int poolDeallocations = 0;
global int bufferOverrunCount = 0;

function checkStackUsage() returns int usage {

    int currentUsage = getApproximateStackUsage();
    
    if (currentUsage > stackHighWaterMark) {
        stackHighWaterMark = currentUsage;
    }
    

    if (currentUsage > 3276) {
        displayLEDs[0] = 0xFF;
        trace("WARNING: High stack usage detected");
    }
    
    return currentUsage;
}


function getApproximateStackUsage() returns int estimation {


    return 1024;
}
```

### Buffer Overflow Detection

```impala

global int guardPrefix = 0xDEAD;
global array protectedData[1024];
global int guardSuffix = 0xBEEF;

function initGuardedBuffer() {
    guardPrefix = 0xDEAD;
    guardSuffix = 0xBEEF;
    

    int i;
    for (i = 0 to 1024) {
        protectedData[i] = 0;
    }
}

function checkBufferIntegrity() returns int isValid {
    if (guardPrefix != 0xDEAD) {
        bufferOverrunCount = bufferOverrunCount + 1;
        displayLEDs[1] = 0xFF;
        trace("ERROR: Buffer prefix corrupted");
        return 0;
    }
    
    if (guardSuffix != 0xBEEF) {
        bufferOverrunCount = bufferOverrunCount + 1;
        displayLEDs[2] = 0xFF;
        trace("ERROR: Buffer suffix corrupted");
        return 0;
    }
    
    return 1;
}
```

### Memory Leak Detection

```impala

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
        return 1;
    }
    
    return 0;
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