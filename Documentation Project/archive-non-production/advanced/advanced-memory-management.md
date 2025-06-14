# Advanced Memory Management in Permut8 Firmware

## Overview

Advanced memory management is critical for real-time audio processing on the Permut8 platform. This document covers sophisticated memory allocation strategies, optimization techniques, and debugging approaches that enable professional-grade firmware development.

Unlike general-purpose applications, Permut8 firmware operates under strict real-time constraints where memory allocation failures or fragmentation can cause audio dropouts. This guide provides battle-tested patterns for managing memory efficiently in resource-constrained, real-time environments.

## Dynamic Memory Allocation Strategies

### Real-Time Safe Allocation

Traditional `malloc()` and `free()` are unsuitable for real-time audio code due to unpredictable timing. Instead, use pre-allocated memory pools:

```impala
// Memory pool for dynamic objects
static u8 audioObjectPool[MAX_OBJECTS * sizeof(AudioObject)];
static bool poolSlots[MAX_OBJECTS];
static int poolNextFree = 0;

AudioObject* allocateAudioObject() {
    // O(1) allocation - no malloc
    for (int i = 0; i < MAX_OBJECTS; i++) {
        int slot = (poolNextFree + i) % MAX_OBJECTS;
        if (!poolSlots[slot]) {
            poolSlots[slot] = true;
            poolNextFree = (slot + 1) % MAX_OBJECTS;
            return (AudioObject*)&audioObjectPool[slot * sizeof(AudioObject)];
        }
    }
    return null; // Pool exhausted
}

void freeAudioObject(AudioObject* obj) {
    // Calculate slot index
    int slot = ((u8*)obj - audioObjectPool) / sizeof(AudioObject);
    if (slot >= 0 && slot < MAX_OBJECTS) {
        poolSlots[slot] = false;
    }
}
```

### Stack-Based Allocation

For temporary objects with predictable lifetimes, use stack-based allocation:

```impala
struct StackAllocator {
    u8* memory;
    int size;
    int used;
};

static StackAllocator frameAllocator;

void initFrameAllocator() {
    static u8 frameMemory[FRAME_MEMORY_SIZE];
    frameAllocator.memory = frameMemory;
    frameAllocator.size = FRAME_MEMORY_SIZE;
    frameAllocator.used = 0;
}

void* allocateFrame(int bytes) {
    if (frameAllocator.used + bytes > frameAllocator.size) {
        return null; // Out of frame memory
    }
    void* result = &frameAllocator.memory[frameAllocator.used];
    frameAllocator.used += bytes;
    return result;
}

void resetFrameAllocator() {
    frameAllocator.used = 0; // Reset for next frame
}

// Usage in process() function
void process() {
    resetFrameAllocator(); // Start fresh each frame
    
    // Allocate temporary buffers
    f32* tempBuffer = (f32*)allocateFrame(BLOCK_SIZE * sizeof(f32));
    
    // Use tempBuffer for processing...
    
    // Memory automatically freed at next resetFrameAllocator()
}
```

## Memory Pool Management

### Typed Memory Pools

Create specialized pools for different object types to eliminate fragmentation:

```impala
// Delay line pool
struct DelayLinePool {
    DelayLine lines[MAX_DELAY_LINES];
    bool allocated[MAX_DELAY_LINES];
    int count;
};

static DelayLinePool delayPool;

DelayLine* allocateDelayLine(int length) {
    if (delayPool.count >= MAX_DELAY_LINES) return null;
    
    for (int i = 0; i < MAX_DELAY_LINES; i++) {
        if (!delayPool.allocated[i]) {
            delayPool.allocated[i] = true;
            delayPool.count++;
            
            // Initialize delay line
            DelayLine* line = &delayPool.lines[i];
            initDelayLine(line, length);
            return line;
        }
    }
    return null;
}

void freeDelayLine(DelayLine* line) {
    int index = line - delayPool.lines;
    if (index >= 0 && index < MAX_DELAY_LINES && delayPool.allocated[index]) {
        delayPool.allocated[index] = false;
        delayPool.count--;
        cleanupDelayLine(line);
    }
}
```

### Multi-Size Pool System

Handle varying allocation sizes with multiple fixed-size pools:

```impala
struct MultiPool {
    // Small allocations (8-32 bytes)
    u8 smallPool[SMALL_POOL_COUNT][32];
    bool smallAllocated[SMALL_POOL_COUNT];
    
    // Medium allocations (64-256 bytes)
    u8 mediumPool[MEDIUM_POOL_COUNT][256];
    bool mediumAllocated[MEDIUM_POOL_COUNT];
    
    // Large allocations (512+ bytes)
    u8 largePool[LARGE_POOL_COUNT][1024];
    bool largeAllocated[LARGE_POOL_COUNT];
};

static MultiPool globalPool;

void* allocateFromMultiPool(int size) {
    if (size <= 32) {
        return allocateFromPool(globalPool.smallPool, globalPool.smallAllocated, 
                               SMALL_POOL_COUNT, 32);
    } else if (size <= 256) {
        return allocateFromPool(globalPool.mediumPool, globalPool.mediumAllocated,
                               MEDIUM_POOL_COUNT, 256);
    } else if (size <= 1024) {
        return allocateFromPool(globalPool.largePool, globalPool.largeAllocated,
                               LARGE_POOL_COUNT, 1024);
    }
    return null; // Size too large
}

void* allocateFromPool(void* pool, bool* allocated, int count, int itemSize) {
    for (int i = 0; i < count; i++) {
        if (!allocated[i]) {
            allocated[i] = true;
            return (u8*)pool + (i * itemSize);
        }
    }
    return null;
}
```

## Advanced Buffer Management

### Circular Buffer Optimization

Optimize circular buffers for cache efficiency and prevent false sharing:

```impala
// Cache-line aligned circular buffer
struct alignas(64) CircularBuffer {
    f32* data;
    int size;
    int readPos;
    int writePos;
    int padding[12]; // Pad to cache line size
};

// Initialize with power-of-2 size for fast modulo
void initCircularBuffer(CircularBuffer* buf, int size) {
    // Ensure size is power of 2
    buf->size = 1;
    while (buf->size < size) buf->size <<= 1;
    
    buf->data = (f32*)allocateAligned(buf->size * sizeof(f32), 64);
    buf->readPos = 0;
    buf->writePos = 0;
}

// Fast write with power-of-2 modulo
void writeToBuffer(CircularBuffer* buf, f32 sample) {
    buf->data[buf->writePos & (buf->size - 1)] = sample;
    buf->writePos++;
}

// Fast read with bounds checking
f32 readFromBuffer(CircularBuffer* buf, int delay) {
    int pos = (buf->writePos - delay - 1) & (buf->size - 1);
    return buf->data[pos];
}
```

### Lock-Free Buffer Operations

Implement lock-free operations for multi-threaded scenarios:

```impala
struct LockFreeBuffer {
    volatile f32* data;
    volatile int writePos;
    volatile int readPos;
    int size;
};

// Single writer, single reader safe
void writeLockFree(LockFreeBuffer* buf, f32 sample) {
    int nextWrite = (buf->writePos + 1) % buf->size;
    if (nextWrite != buf->readPos) { // Not full
        buf->data[buf->writePos] = sample;
        // Memory barrier ensures data written before position update
        __sync_synchronize();
        buf->writePos = nextWrite;
    }
}

bool readLockFree(LockFreeBuffer* buf, f32* sample) {
    if (buf->readPos == buf->writePos) return false; // Empty
    
    *sample = buf->data[buf->readPos];
    // Memory barrier ensures data read before position update
    __sync_synchronize();
    buf->readPos = (buf->readPos + 1) % buf->size;
    return true;
}
```

## Memory-Mapped I/O Patterns

### Hardware Register Access

Structure memory-mapped hardware access for type safety and clarity:

```impala
// Memory-mapped register structure
struct PermutHardware {
    volatile u32 audioInput;      // 0x1000
    volatile u32 audioOutput;     // 0x1004
    volatile u32 parameterBank[8]; // 0x1008-0x1024
    volatile u32 ledControl;      // 0x1028
    volatile u32 clockControl;    // 0x102C
    volatile u32 statusRegister;  // 0x1030
};

// Safe hardware access macros
#define HW ((PermutHardware*)0x40000000)
#define WRITE_REG(reg, value) do { \
    __sync_synchronize(); \
    (reg) = (value); \
    __sync_synchronize(); \
} while(0)

#define READ_REG(reg) ({ \
    __sync_synchronize(); \
    volatile u32 _val = (reg); \
    __sync_synchronize(); \
    _val; \
})

// Usage
void updateLEDs(u32 ledPattern) {
    WRITE_REG(HW->ledControl, ledPattern);
}

u32 readAudioInput() {
    return READ_REG(HW->audioInput);
}
```

### DMA Buffer Management

Manage DMA buffers with proper cache coherency:

```impala
struct DMABuffer {
    f32* data;
    int size;
    volatile bool ready;
    volatile int position;
};

// Allocate cache-coherent DMA buffer
DMABuffer* allocateDMABuffer(int samples) {
    DMABuffer* buf = (DMABuffer*)allocateAligned(sizeof(DMABuffer), 64);
    
    // Allocate non-cached memory for DMA
    buf->data = (f32*)allocateUncached(samples * sizeof(f32));
    buf->size = samples;
    buf->ready = false;
    buf->position = 0;
    
    return buf;
}

// Cache coherency operations
void flushDMABuffer(DMABuffer* buf) {
    // Flush CPU cache to ensure DMA sees latest data
    __builtin_dcache_flush_range(buf->data, buf->size * sizeof(f32));
}

void invalidateDMABuffer(DMABuffer* buf) {
    // Invalidate CPU cache to see DMA updates
    __builtin_dcache_invalidate_range(buf->data, buf->size * sizeof(f32));
}
```

## Cache Optimization Techniques

### Data Structure Layout

Organize data structures for optimal cache behavior:

```impala
// Cache-friendly vs cache-hostile layouts

// BAD: Array of structures (AoS) - poor cache locality
struct BadVoice {
    f32 frequency;
    f32 amplitude;
    f32 phase;
    f32 filterCutoff;
    f32 filterResonance;
    bool active;
    int noteNumber;
    // ... more fields
};
BadVoice voices[MAX_VOICES]; // Each voice access loads unrelated data

// GOOD: Structure of arrays (SoA) - excellent cache locality
struct GoodVoiceBank {
    f32 frequencies[MAX_VOICES];
    f32 amplitudes[MAX_VOICES];
    f32 phases[MAX_VOICES];
    f32 filterCutoffs[MAX_VOICES];
    f32 filterResonances[MAX_VOICES];
    bool active[MAX_VOICES];
    int noteNumbers[MAX_VOICES];
};
GoodVoiceBank voiceBank; // Processing frequencies loads related data
```

### Loop Optimization

Structure loops for optimal cache and prefetch behavior:

```impala
// Cache-friendly processing patterns
void processVoicesOptimized(GoodVoiceBank* voices, f32* output, int samples) {
    // Process all frequencies together (cache-friendly)
    for (int v = 0; v < MAX_VOICES; v++) {
        if (!voices->active[v]) continue;
        
        // Update all frequency-related calculations
        voices->phases[v] += voices->frequencies[v] * PHASE_INCREMENT;
        if (voices->phases[v] >= TWO_PI) {
            voices->phases[v] -= TWO_PI;
        }
    }
    
    // Process all amplitudes together
    for (int v = 0; v < MAX_VOICES; v++) {
        if (!voices->active[v]) continue;
        voices->amplitudes[v] = updateEnvelope(voices->amplitudes[v]);
    }
    
    // Generate output samples
    for (int s = 0; s < samples; s++) {
        f32 sample = 0.0f;
        for (int v = 0; v < MAX_VOICES; v++) {
            if (!voices->active[v]) continue;
            sample += sin(voices->phases[v]) * voices->amplitudes[v];
        }
        output[s] = sample;
    }
}
```

### Memory Prefetching

Use explicit prefetching for predictable access patterns:

```impala
// Manual prefetching for large arrays
void processDelayLineWithPrefetch(DelayLine* delay, f32* input, f32* output, int samples) {
    for (int i = 0; i < samples; i++) {
        // Prefetch future samples
        if (i + 8 < samples) {
            __builtin_prefetch(&delay->buffer[(delay->writePos + 8) & delay->mask], 1, 3);
        }
        
        // Current processing
        delay->buffer[delay->writePos & delay->mask] = input[i];
        output[i] = delay->buffer[(delay->writePos - delay->length) & delay->mask];
        delay->writePos++;
    }
}

// Streaming prefetch for large data processing
void streamProcessWithPrefetch(f32* data, int count) {
    const int PREFETCH_DISTANCE = 64; // Cache lines ahead
    
    for (int i = 0; i < count; i++) {
        // Prefetch future data
        if (i + PREFETCH_DISTANCE < count) {
            __builtin_prefetch(&data[i + PREFETCH_DISTANCE], 0, 0);
        }
        
        // Process current data
        data[i] = processample(data[i]);
    }
}
```

## Memory Debugging Techniques

### Allocation Tracking

Implement comprehensive allocation tracking for debugging:

```impala
struct AllocationInfo {
    void* address;
    int size;
    const char* file;
    int line;
    u32 checksum;
    bool active;
};

static AllocationInfo allocations[MAX_TRACKED_ALLOCATIONS];
static int allocationCount = 0;

#ifdef DEBUG_MEMORY
#define DEBUG_ALLOC(ptr, size) trackAllocation(ptr, size, __FILE__, __LINE__)
#define DEBUG_FREE(ptr) trackDeallocation(ptr)
#else
#define DEBUG_ALLOC(ptr, size)
#define DEBUG_FREE(ptr)
#endif

void* debugAllocate(int size, const char* file, int line) {
    void* ptr = regularAllocate(size);
    if (ptr) {
        DEBUG_ALLOC(ptr, size);
    }
    return ptr;
}

void debugFree(void* ptr, const char* file, int line) {
    DEBUG_FREE(ptr);
    regularFree(ptr);
}

void trackAllocation(void* ptr, int size, const char* file, int line) {
    if (allocationCount < MAX_TRACKED_ALLOCATIONS) {
        AllocationInfo* info = &allocations[allocationCount++];
        info->address = ptr;
        info->size = size;
        info->file = file;
        info->line = line;
        info->checksum = calculateChecksum(ptr, size);
        info->active = true;
    }
}
```

### Heap Corruption Detection

Implement guard bytes and corruption detection:

```impala
struct GuardedAllocation {
    u32 frontGuard[4];  // 16 bytes
    // User data goes here
    // Back guard follows user data
};

#define GUARD_PATTERN 0xDEADBEEF
#define GUARD_SIZE 16

void* guardedAllocate(int size) {
    int totalSize = size + 2 * GUARD_SIZE + sizeof(int); // Size stored before front guard
    u8* raw = (u8*)regularAllocate(totalSize);
    
    if (!raw) return null;
    
    // Store size
    *(int*)raw = size;
    
    // Setup front guard
    u32* frontGuard = (u32*)(raw + sizeof(int));
    for (int i = 0; i < 4; i++) {
        frontGuard[i] = GUARD_PATTERN;
    }
    
    // User data starts after front guard
    u8* userData = raw + sizeof(int) + GUARD_SIZE;
    
    // Setup back guard
    u32* backGuard = (u32*)(userData + size);
    for (int i = 0; i < 4; i++) {
        backGuard[i] = GUARD_PATTERN;
    }
    
    return userData;
}

bool checkGuards(void* ptr) {
    u8* userData = (u8*)ptr;
    u8* raw = userData - sizeof(int) - GUARD_SIZE;
    int size = *(int*)raw;
    
    // Check front guard
    u32* frontGuard = (u32*)(raw + sizeof(int));
    for (int i = 0; i < 4; i++) {
        if (frontGuard[i] != GUARD_PATTERN) {
            logError("Front guard corruption at %p", ptr);
            return false;
        }
    }
    
    // Check back guard
    u32* backGuard = (u32*)(userData + size);
    for (int i = 0; i < 4; i++) {
        if (backGuard[i] != GUARD_PATTERN) {
            logError("Back guard corruption at %p", ptr);
            return false;
        }
    }
    
    return true;
}
```

### Memory Leak Detection

Track object lifetimes and detect leaks:

```impala
struct ObjectTracker {
    const char* typeName;
    int created;
    int destroyed;
    int peakCount;
    int currentCount;
};

static ObjectTracker trackers[MAX_OBJECT_TYPES];
static int trackerCount = 0;

int registerObjectType(const char* typeName) {
    if (trackerCount >= MAX_OBJECT_TYPES) return -1;
    
    ObjectTracker* tracker = &trackers[trackerCount];
    tracker->typeName = typeName;
    tracker->created = 0;
    tracker->destroyed = 0;
    tracker->peakCount = 0;
    tracker->currentCount = 0;
    
    return trackerCount++;
}

void trackObjectCreation(int typeId) {
    if (typeId >= 0 && typeId < trackerCount) {
        ObjectTracker* tracker = &trackers[typeId];
        tracker->created++;
        tracker->currentCount++;
        if (tracker->currentCount > tracker->peakCount) {
            tracker->peakCount = tracker->currentCount;
        }
    }
}

void trackObjectDestruction(int typeId) {
    if (typeId >= 0 && typeId < trackerCount) {
        ObjectTracker* tracker = &trackers[typeId];
        tracker->destroyed++;
        tracker->currentCount--;
    }
}

void reportMemoryLeaks() {
    bool foundLeaks = false;
    for (int i = 0; i < trackerCount; i++) {
        ObjectTracker* tracker = &trackers[i];
        if (tracker->currentCount > 0) {
            logError("LEAK: %s - %d objects not freed (peak: %d)",
                    tracker->typeName, tracker->currentCount, tracker->peakCount);
            foundLeaks = true;
        }
    }
    if (!foundLeaks) {
        logInfo("No memory leaks detected");
    }
}
```

## Advanced Pointer Arithmetic

### Safe Pointer Operations

Implement bounds-checked pointer arithmetic:

```impala
struct BoundedBuffer {
    u8* start;
    u8* end;
    u8* current;
};

bool advancePointer(BoundedBuffer* buf, int bytes) {
    if (buf->current + bytes > buf->end) {
        return false; // Would overflow
    }
    buf->current += bytes;
    return true;
}

bool retreatPointer(BoundedBuffer* buf, int bytes) {
    if (buf->current - bytes < buf->start) {
        return false; // Would underflow
    }
    buf->current -= bytes;
    return true;
}

void* safeRead(BoundedBuffer* buf, int size) {
    if (buf->current + size > buf->end) {
        return null; // Not enough data
    }
    void* result = buf->current;
    buf->current += size;
    return result;
}
```

### Memory Layout Calculations

Calculate complex memory layouts with proper alignment:

```impala
struct LayoutCalculator {
    u8* base;
    int offset;
    int totalSize;
    int alignment;
};

void initLayout(LayoutCalculator* calc, void* base, int alignment) {
    calc->base = (u8*)base;
    calc->offset = 0;
    calc->totalSize = 0;
    calc->alignment = alignment;
}

void* allocateInLayout(LayoutCalculator* calc, int size, int align) {
    // Align current offset
    int alignedOffset = (calc->offset + align - 1) & ~(align - 1);
    
    void* result = calc->base + alignedOffset;
    calc->offset = alignedOffset + size;
    
    if (calc->offset > calc->totalSize) {
        calc->totalSize = calc->offset;
    }
    
    return result;
}

// Usage for complex data structure layout
void layoutAudioEngine(LayoutCalculator* calc) {
    // Align large arrays to cache boundaries
    f32* sampleBuffer = (f32*)allocateInLayout(calc, BUFFER_SIZE * sizeof(f32), 64);
    f32* delayBuffer = (f32*)allocateInLayout(calc, DELAY_SIZE * sizeof(f32), 64);
    
    // Control data can be less aligned
    ParamState* params = (ParamState*)allocateInLayout(calc, sizeof(ParamState), 16);
    
    // Small frequently accessed data together
    EngineState* state = (EngineState*)allocateInLayout(calc, sizeof(EngineState), 8);
    
    logInfo("Audio engine layout: %d bytes total", calc->totalSize);
}
```

## Performance Monitoring

### Memory Usage Profiling

Track memory usage patterns for optimization:

```impala
struct MemoryProfiler {
    int totalAllocations;
    int totalFrees;
    int peakUsage;
    int currentUsage;
    int allocationSizes[16]; // Histogram of allocation sizes
    u64 allocationTimes[MAX_TIMING_SAMPLES];
    int timingIndex;
};

static MemoryProfiler profiler;

void profileAllocation(int size, u64 time) {
    profiler.totalAllocations++;
    profiler.currentUsage += size;
    
    if (profiler.currentUsage > profiler.peakUsage) {
        profiler.peakUsage = profiler.currentUsage;
    }
    
    // Update size histogram
    int bucket = 0;
    int bucketSize = size;
    while (bucketSize > 32 && bucket < 15) {
        bucketSize >>= 1;
        bucket++;
    }
    profiler.allocationSizes[bucket]++;
    
    // Track timing
    profiler.allocationTimes[profiler.timingIndex] = time;
    profiler.timingIndex = (profiler.timingIndex + 1) % MAX_TIMING_SAMPLES;
}

void printMemoryProfile() {
    logInfo("Memory Profile:");
    logInfo("  Total allocations: %d", profiler.totalAllocations);
    logInfo("  Total frees: %d", profiler.totalFrees);
    logInfo("  Peak usage: %d bytes", profiler.peakUsage);
    logInfo("  Current usage: %d bytes", profiler.currentUsage);
    
    logInfo("Allocation size distribution:");
    for (int i = 0; i < 16; i++) {
        if (profiler.allocationSizes[i] > 0) {
            int minSize = 32 << i;
            int maxSize = (32 << (i + 1)) - 1;
            logInfo("  %d-%d bytes: %d allocations", 
                   minSize, maxSize, profiler.allocationSizes[i]);
        }
    }
}
```

## Best Practices Summary

### Real-Time Memory Management Rules

1. **Pre-allocate everything possible** - No runtime allocation in audio callbacks
2. **Use fixed-size pools** - Eliminates fragmentation and provides predictable timing
3. **Align data structures** - Cache line alignment for performance-critical data
4. **Minimize pointer chasing** - Use arrays instead of linked structures
5. **Track everything in debug builds** - Comprehensive debugging in development

### Memory Layout Guidelines

1. **Group related data** - Spatial locality improves cache performance
2. **Separate hot and cold data** - Frequently accessed data together
3. **Use power-of-2 sizes** - Enables fast modulo operations
4. **Pad to cache lines** - Prevent false sharing in multi-threaded code
5. **Consider memory hierarchy** - L1/L2 cache sizes affect access patterns

### Debugging Recommendations

1. **Always use guards in debug** - Catch buffer overruns immediately
2. **Track object lifetimes** - Detect leaks and use-after-free
3. **Profile memory patterns** - Understand allocation behavior
4. **Test with memory pressure** - Simulate low-memory conditions
5. **Validate assumptions** - Regular consistency checks

Advanced memory management on Permut8 requires careful planning and disciplined execution. The techniques in this document provide the foundation for building robust, high-performance audio firmware that meets real-time constraints while maintaining reliable operation.

These patterns have been battle-tested in professional audio applications and provide the building blocks for sophisticated memory management strategies. Remember that premature optimization is harmful - profile first, then optimize the proven bottlenecks using these techniques.
