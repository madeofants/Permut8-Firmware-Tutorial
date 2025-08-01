# Utility Functions and Development Aids

## Overview
Essential utility functions for mathematical operations, data conversions, debugging, and development support that accelerate firmware development and improve code reliability.

## Mathematical Utilities

### Fast Math Approximations
```impala

namespace FastMath {
    

    float fastReciprocal(float x) {

        int i = *(int*)&x;
        i = 0x7F000000 - i;
        float r = *(float*)&i;
        

        return r * (2.0 - x * r);
    }
    

    float fastSqrt(float x) {
        if (x <= 0.0) return 0.0;
        

        float xhalf = 0.5 * x;
        int i = *(int*)&x;
        i = 0x5f3759df - (i >> 1);
        x = *(float*)&i;
        

        x = x * (1.5 - xhalf * x * x);
        x = x * (1.5 - xhalf * x * x);
        
        return 1.0 / x;
    }
    

    float fastPow(float base, int exponent) {
        if (exponent == 0) return 1.0;
        if (exponent == 1) return base;
        if (exponent == 2) return base * base;
        
        float result = 1.0;
        float currentPower = base;
        int exp = abs(exponent);
        

        while (exp > 0) {
            if (exp & 1) result *= currentPower;
            currentPower *= currentPower;
            exp >>= 1;
        }
        
        return exponent < 0 ? 1.0 / result : result;
    }
}
```

### Trigonometric Functions
```impala

namespace TrigLookup {
    

    static float sineTable[256];
    static bool tablesInitialized = false;
    
    void initializeTables() {
        if (tablesInitialized) return;
        
        for (int i = 0; i < 256; i++) {
            sineTable[i] = sin(2.0 * M_PI * i / 256.0);
        }
        tablesInitialized = true;
    }
    

    float fastSin(float angle) {
        if (!tablesInitialized) initializeTables();
        

        angle = angle / (2.0 * M_PI);
        angle = angle - floor(angle);
        

        float indexFloat = angle * 256.0;
        int index = (int)indexFloat;
        float fraction = indexFloat - index;
        

        int nextIndex = (index + 1) % 256;
        return sineTable[index] + fraction * (sineTable[nextIndex] - sineTable[index]);
    }
    

    float fastCos(float angle) {
        return fastSin(angle + M_PI * 0.5);
    }
    

    float fastTan(float angle) {

        float x2 = angle * angle;
        return angle * (1.0 + x2 * (1.0/3.0 + x2 * 2.0/15.0));
    }
}
```

### Interpolation Functions
```impala

namespace Interpolation {
    

    float lerp(float a, float b, float t) {
        return a + t * (b - a);
    }
    

    float cubicInterp(float y0, float y1, float y2, float y3, float t) {
        float a0 = y3 - y2 - y0 + y1;
        float a1 = y0 - y1 - a0;
        float a2 = y2 - y0;
        float a3 = y1;
        
        return a0 * t * t * t + a1 * t * t + a2 * t + a3;
    }
    

    float hermiteInterp(float y0, float y1, float y2, float y3, float t) {
        float c0 = y1;
        float c1 = 0.5 * (y2 - y0);
        float c2 = y0 - 2.5 * y1 + 2.0 * y2 - 0.5 * y3;
        float c3 = 0.5 * (y3 - y0) + 1.5 * (y1 - y2);
        
        return ((c3 * t + c2) * t + c1) * t + c0;
    }
    

    float smoothStep(float edge0, float edge1, float x) {
        float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
        return t * t * (3.0 - 2.0 * t);
    }
    

    float smootherStep(float edge0, float edge1, float x) {
        float t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
    }
}
```

## Data Conversion Utilities

### Audio Format Conversions
```impala

namespace AudioConversion {
    

    float toNormalizedFloat(int sample) {
        return (float)sample / 2047.0;
    }
    

    int fromNormalizedFloat(float sample) {
        return (int)(clamp(sample, -1.0, 1.0) * 2047.0);
    }
    

    float dbToLinear(float db) {
        return pow(10.0, db / 20.0);
    }
    

    float linearToDb(float linear) {
        if (linear <= 0.0) return -96.0;
        return 20.0 * log10(linear);
    }
    

    float midiToFreq(float midiNote) {
        return 440.0 * pow(2.0, (midiNote - 69.0) / 12.0);
    }
    

    float freqToMidi(float frequency) {
        if (frequency <= 0.0) return 0.0;
        return 69.0 + 12.0 * log2(frequency / 440.0);
    }
}
```

### Parameter Mapping
```impala

namespace ParameterMapping {
    

    float expCurve(float input, float minVal, float maxVal, float curve) {

        float normalized = pow(input, curve);
        return minVal + normalized * (maxVal - minVal);
    }
    

    float logCurve(float input, float minVal, float maxVal) {
        if (input <= 0.0) return minVal;
        float logInput = log(1.0 + input * (M_E - 1.0));
        return minVal + logInput * (maxVal - minVal);
    }
    

    float sCurve(float input, float sharpness) {

        float x = input * 2.0 - 1.0;
        float result = x / (1.0 + sharpness * abs(x));
        return (result + 1.0) * 0.5;
    }
    

    float quantize(float input, int steps) {
        if (steps <= 1) return input;
        float stepSize = 1.0 / (steps - 1);
        return round(input / stepSize) * stepSize;
    }
    

    float hysteresis(float input, float threshold, float* state) {
        if (input > threshold + 0.05) {
            *state = 1.0;
        } else if (input < threshold - 0.05) {
            *state = 0.0;
        }
        return *state;
    }
}
```

### Data Structure Utilities
```impala

namespace DataStructures {
    

    struct CircularBuffer {
        float* data;
        int size;
        int writeIndex;
        int readIndex;
        bool full;
    };
    
    void initCircularBuffer(CircularBuffer* buf, float* memory, int size) {
        buf->data = memory;
        buf->size = size;
        buf->writeIndex = 0;
        buf->readIndex = 0;
        buf->full = false;
    }
    
    void writeCircularBuffer(CircularBuffer* buf, float value) {
        buf->data[buf->writeIndex] = value;
        buf->writeIndex = (buf->writeIndex + 1) % buf->size;
        
        if (buf->writeIndex == buf->readIndex) {
            buf->full = true;
            buf->readIndex = (buf->readIndex + 1) % buf->size;
        }
    }
    
    float readCircularBuffer(CircularBuffer* buf) {
        if (!buf->full && buf->readIndex == buf->writeIndex) {
            return 0.0;
        }
        
        float value = buf->data[buf->readIndex];
        buf->readIndex = (buf->readIndex + 1) % buf->size;
        buf->full = false;
        return value;
    }
    

    float readDelayTap(CircularBuffer* buf, int delaySamples) {
        int tapIndex = (buf->writeIndex - delaySamples - 1 + buf->size) % buf->size;
        return buf->data[tapIndex];
    }
}
```

## Debugging and Development Utilities

### Performance Profiling
```impala

namespace Profiler {
    
    struct PerformanceCounter {
        int startTime;
        int totalTime;
        int callCount;
        int maxTime;
        const char* name;
    };
    

    void startTimer(PerformanceCounter* counter) {
        counter->startTime = getCurrentCycles();
    }
    

    void endTimer(PerformanceCounter* counter) {
        int elapsed = getCurrentCycles() - counter->startTime;
        counter->totalTime = counter->totalTime + elapsed;
        counter->callCount = counter->callCount + 1;
        if (elapsed > counter->maxTime) {
            counter->maxTime = elapsed;
        }
    }
    

    float getAverageTime(PerformanceCounter* counter) {
        if (counter->callCount == 0) return 0.0;
        return (float)counter->totalTime / counter->callCount;
    }
    

    void resetCounter(PerformanceCounter* counter) {
        counter->totalTime = 0;
        counter->callCount = 0;
        counter->maxTime = 0;
    }
    

    PerformanceCounter delayCounter = {0, 0, 0, 0, "Delay Processing"};
    
    void profiledDelayProcessing() {
        startTimer(&delayCounter);

        endTimer(&delayCounter);
    }
}
```

### Memory Debugging
```impala

namespace MemoryDebug {
    
    struct MemoryStats {
        int totalAllocated;
        int currentUsage;
        int peakUsage;
        int allocationCount;
        int freeCount;
    };
    
    static MemoryStats memStats = {0, 0, 0, 0, 0};
    

    void* debugMalloc(int size, const char* file, int line) {
        void* ptr = malloc(size);
        if (ptr) {
            memStats.totalAllocated = memStats.totalAllocated + size;
            memStats.currentUsage = memStats.currentUsage + size;
            memStats.allocationCount = memStats.allocationCount + 1;
            
            if (memStats.currentUsage > memStats.peakUsage) {
                memStats.peakUsage = memStats.currentUsage;
            }
            
            #ifdef DEBUG
                printf("ALLOC: %p, size=%d, %s:%d\n", ptr, size, file, line);
            #endif
        }
        return ptr;
    }
    

    void debugFree(void* ptr, int size, const char* file, int line) {
        if (ptr) {
            free(ptr);
            memStats.currentUsage = memStats.currentUsage - size;
            memStats.freeCount = memStats.freeCount + 1;
            
            #ifdef DEBUG
                printf("FREE: %p, size=%d, %s:%d\n", ptr, size, file, line);
            #endif
        }
    }
    

    #define DEBUG_MALLOC(size) debugMalloc(size, __FILE__, __LINE__)
    #define DEBUG_FREE(ptr, size) debugFree(ptr, size, __FILE__, __LINE__)
    

    void checkMemoryLeaks() {
        if (memStats.allocationCount != memStats.freeCount) {
            printf("MEMORY LEAK: %d allocations, %d frees\n", 
                   memStats.allocationCount, memStats.freeCount);
        }
        if (memStats.currentUsage != 0) {
            printf("MEMORY LEAK: %d bytes still allocated\n", memStats.currentUsage);
        }
    }
}
```

### Assertion and Validation
```impala

namespace Debug {
    

    #ifdef DEBUG
        #define ASSERT(condition, message) \
            do { \
                if (!(condition)) { \
                    printf("ASSERTION FAILED: %s at %s:%d\n", message, __FILE__, __LINE__); \
                    while(1); /* Stop execution */ \
                } \
            } while(0)
    #else
        #define ASSERT(condition, message) ((void)0)
    #endif
    

    bool validateRange(float value, float min, float max, const char* name) {
        if (value < min || value > max) {
            #ifdef DEBUG
                printf("RANGE ERROR: %s = %f, expected [%f, %f]\n", name, value, min, max);
            #endif
            return false;
        }
        return true;
    }
    

    bool validateAudioSample(float sample) {
        if (isnan(sample) || isinf(sample)) {
            #ifdef DEBUG
                printf("INVALID AUDIO: NaN or Inf detected\n");
            #endif
            return false;
        }
        return validateRange(sample, -10.0, 10.0, "audio_sample");
    }
    

    void checkBufferBounds(int index, int bufferSize, const char* bufferName) {
        ASSERT(index >= 0 && index < bufferSize, 
               "Buffer index out of bounds");
        
        #ifdef DEBUG
            if (index < 0 || index >= bufferSize) {
                printf("BUFFER OVERFLOW: %s[%d], size=%d\n", 
                       bufferName, index, bufferSize);
            }
        #endif
    }
}
```

### Diagnostic Output
```impala

namespace Diagnostics {
    
    enum LogLevel {
        LOG_ERROR = 0,
        LOG_WARNING = 1,
        LOG_INFO = 2,
        LOG_DEBUG = 3
    };
    
    static LogLevel currentLogLevel = LOG_INFO;
    

    void logMessage(LogLevel level, const char* format, ...) {
        if (level <= currentLogLevel) {
            const char* levelNames[] = {"ERROR", "WARN", "INFO", "DEBUG"};
            printf("[%s] ", levelNames[level]);
            
            va_list args;
            va_start(args, format);
            vprintf(format, args);
            va_end(args);
            printf("\n");
        }
    }
    

    void analyzeSignal(float* buffer, int size, const char* name) {
        float min = buffer[0], max = buffer[0];
        float sum = 0.0, sumSquares = 0.0;
        
        for (int i = 0; i < size; i++) {
            float sample = buffer[i];
            if (sample < min) min = sample;
            if (sample > max) max = sample;
            sum = sum + sample;
            sumSquares = sumSquares + (sample * sample);
        }
        
        float mean = sum / size;
        float rms = sqrt(sumSquares / size);
        
        logMessage(LOG_INFO, "%s: min=%.3f max=%.3f mean=%.3f rms=%.3f", 
                   name, min, max, mean, rms);
    }
    

    void dumpParameters() {
        logMessage(LOG_DEBUG, "Parameter dump:");
        for (int i = 0; i < PARAM_COUNT; i++) {
            logMessage(LOG_DEBUG, "  params[%d] = %.3f", i, params[i]);
        }
    }
    

    void visualizeLEDs() {
        printf("LEDs: ");
        for (int i = 0; i < LED_COUNT; i++) {
            printf("%3d ", displayLEDs[i]);
        }
        printf("\n");
    }
}
```

## Testing and Validation Utilities

### Unit Testing Framework
```impala

namespace UnitTest {
    
    struct TestStats {
        int totalTests;
        int passedTests;
        int failedTests;
    };
    
    static TestStats testStats = {0, 0, 0};
    

    void testAssert(bool condition, const char* testName) {
        testStats.totalTests = testStats.totalTests + 1;
        if (condition) {
            testStats.passedTests = testStats.passedTests + 1;
            printf("PASS: %s\n", testName);
        } else {
            testStats.failedTests = testStats.failedTests + 1;
            printf("FAIL: %s\n", testName);
        }
    }
    

    void testFloatEqual(float actual, float expected, float tolerance, const char* testName) {
        bool equal = abs(actual - expected) <= tolerance;
        testAssert(equal, testName);
        if (!equal) {
            printf("  Expected: %.6f, Actual: %.6f, Diff: %.6f\n", 
                   expected, actual, abs(actual - expected));
        }
    }
    

    void runTests() {
        printf("Running unit tests...\n");
        testStats = {0, 0, 0};
        

        testMathFunctions();
        testAudioProcessing();
        testParameterMapping();
        
        printf("\nTest Results: %d/%d passed (%d failed)\n", 
               testStats.passedTests, testStats.totalTests, testStats.failedTests);
    }
    

    void testMathFunctions() {
        testFloatEqual(FastMath::fastSqrt(4.0), 2.0, 0.01, "FastMath sqrt");
        testFloatEqual(TrigLookup::fastSin(0.0), 0.0, 0.01, "TrigLookup sin(0)");
        testFloatEqual(TrigLookup::fastSin(M_PI/2), 1.0, 0.01, "TrigLookup sin(π/2)");
    }
}
```

### Performance Benchmarking
```impala

namespace Benchmark {
    

    float benchmarkFunction(void (*func)(), int iterations) {
        int startTime = getCurrentCycles();
        
        for (int i = 0; i < iterations; i++) {
            func();
        }
        
        int endTime = getCurrentCycles();
        return (float)(endTime - startTime) / iterations;
    }
    

    void compareImplementations(void (*func1)(), void (*func2)(), 
                               const char* name1, const char* name2) {
        const int iterations = 1000;
        
        float time1 = benchmarkFunction(func1, iterations);
        float time2 = benchmarkFunction(func2, iterations);
        
        printf("Performance comparison:\n");
        printf("  %s: %.2f cycles/call\n", name1, time1);
        printf("  %s: %.2f cycles/call\n", name2, time2);
        printf("  Speedup: %.2fx\n", time1 / time2);
    }
}
```

## Integration Examples

### Complete Utility Usage
```impala

void advancedFirmware() {

    Profiler::PerformanceCounter mainCounter = {0, 0, 0, 0, "Main Process"};
    Profiler::startTimer(&mainCounter);
    

    Debug::validateRange(params[CUTOFF], 0.0, 1.0, "cutoff");
    

    TrigLookup::initializeTables();
    float lfoValue = TrigLookup::fastSin(getCurrentPhase());
    

    float cutoffFreq = ParameterMapping::expCurve(params[CUTOFF], 20.0, 20000.0, 2.0);
    

    float processedSample = applyFilter(signal[2], cutoffFreq);
    Debug::validateAudioSample(processedSample);
    signal[2] = processedSample;
    

    Profiler::endTimer(&mainCounter);
    

    #ifdef DEBUG
        static int debugCounter = 0;
        debugCounter = debugCounter + 1;
        if (debugCounter % 48000 == 0) {
            Diagnostics::logMessage(LOG_INFO, "Average processing time: %.2f cycles", 
                                   Profiler::getAverageTime(&mainCounter));
        }
    #endif
}
```

## Key Benefits

**Development Speed**: Pre-built utilities eliminate repetitive coding and reduce development time.

**Performance Optimization**: Fast math approximations and optimized algorithms maintain real-time performance.

**Reliability**: Comprehensive validation and debugging tools catch errors early in development.

**Professional Quality**: Standardized utilities ensure consistent behavior across different firmware projects.

**Maintainability**: Well-tested utility functions reduce bugs and simplify code maintenance.

Use these utilities as building blocks for robust, efficient firmware development, enabling focus on creative audio processing while maintaining professional development standards.
