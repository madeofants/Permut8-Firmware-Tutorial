# Metaprogramming Constructs in Permut8 Firmware

## Overview

Metaprogramming in Permut8 firmware enables the creation of flexible, reusable, and efficient code through advanced language constructs and code generation techniques. This document explores sophisticated approaches to template-like programming, dynamic dispatch, and build-time code generation that allow developers to write more maintainable and performant firmware.

Unlike traditional metaprogramming in higher-level languages, Permut8 metaprogramming focuses on compile-time code generation and pattern-based programming that maintains real-time performance guarantees while reducing code duplication and improving maintainability.

## Advanced Preprocessor Techniques

### Macro-Based Generic Programming

Create type-generic data structures and algorithms using advanced macro techniques:

```impala
// Generic array implementation
#define DECLARE_ARRAY(TYPE, NAME) \
    struct NAME##Array { \
        TYPE* data; \
        int size; \
        int capacity; \
    }; \
    \
    bool init##NAME##Array(struct NAME##Array* arr, int capacity) { \
        arr->data = (TYPE*)allocate(capacity * sizeof(TYPE)); \
        arr->size = 0; \
        arr->capacity = capacity; \
        return arr->data != null; \
    } \
    \
    bool push##NAME##Array(struct NAME##Array* arr, TYPE value) { \
        if (arr->size >= arr->capacity) return false; \
        arr->data[arr->size++] = value; \
        return true; \
    } \
    \
    TYPE get##NAME##Array(struct NAME##Array* arr, int index) { \
        return (index >= 0 && index < arr->size) ? arr->data[index] : (TYPE)0; \
    } \
    \
    void clear##NAME##Array(struct NAME##Array* arr) { \
        arr->size = 0; \
    }

// Usage: Create specific array types
DECLARE_ARRAY(f32, Sample)     // Creates SampleArray type
DECLARE_ARRAY(int, Parameter)  // Creates ParameterArray type
DECLARE_ARRAY(bool, Gate)      // Creates GateArray type

// Now use the generated types and functions
void processAudioWithArrays() {
    struct SampleArray samples;
    struct ParameterArray params;
    
    if (initSampleArray(&samples, 1024) && initParameterArray(&params, 16)) {
        pushSampleArray(&samples, 0.5f);
        pushParameterArray(&params, 440);
        
        f32 sample = getSampleArray(&samples, 0);
        int param = getParameterArray(&params, 0);
    }
}
```

### X-Macro Pattern Implementation

Use X-macros for maintainable enumeration and dispatch:

```impala
// Define all audio effects in one place
#define AUDIO_EFFECTS_LIST \
    X(REVERB, "Reverb", processReverb, initReverb, cleanupReverb) \
    X(DELAY, "Delay", processDelay, initDelay, cleanupDelay) \
    X(FILTER, "Filter", processFilter, initFilter, cleanupFilter) \
    X(DISTORTION, "Distortion", processDistortion, initDistortion, cleanupDistortion) \
    X(CHORUS, "Chorus", processChorus, initChorus, cleanupChorus) \
    X(FLANGER, "Flanger", processFlanger, initFlanger, cleanupFlanger)

// Generate enum
#define X(id, name, process, init, cleanup) EFFECT_##id,
enum EffectType {
    AUDIO_EFFECTS_LIST
    EFFECT_COUNT
};
#undef X

// Generate name array
#define X(id, name, process, init, cleanup) name,
static const char* effectNames[EFFECT_COUNT] = {
    AUDIO_EFFECTS_LIST
};
#undef X

// Generate function pointer arrays
#define X(id, name, process, init, cleanup) process,
static ProcessFunc processFunctions[EFFECT_COUNT] = {
    AUDIO_EFFECTS_LIST
};
#undef X

#define X(id, name, process, init, cleanup) init,
static InitFunc initFunctions[EFFECT_COUNT] = {
    AUDIO_EFFECTS_LIST
};
#undef X

#define X(id, name, process, init, cleanup) cleanup,
static CleanupFunc cleanupFunctions[EFFECT_COUNT] = {
    AUDIO_EFFECTS_LIST
};
#undef X

// Generated dispatch functions
void processEffect(enum EffectType type, f32* input, f32* output, int samples) {
    if (type >= 0 && type < EFFECT_COUNT) {
        processFunctions[type](input, output, samples);
    }
}

bool initEffect(enum EffectType type, void* state) {
    if (type >= 0 && type < EFFECT_COUNT) {
        return initFunctions[type](state);
    }
    return false;
}

const char* getEffectName(enum EffectType type) {
    if (type >= 0 && type < EFFECT_COUNT) {
        return effectNames[type];
    }
    return "Unknown";
}
```

### Complex Macro Programming

Build sophisticated macro systems for code generation:

```impala
// Macro for creating DSP filter implementations
#define DECLARE_FILTER(NAME, COEFFS, ORDER) \
    struct NAME##Filter { \
        f32 x[ORDER + 1]; \
        f32 y[ORDER + 1]; \
        int pos; \
    }; \
    \
    void init##NAME##Filter(struct NAME##Filter* filter) { \
        for (int i = 0; i <= ORDER; i++) { \
            filter->x[i] = 0.0f; \
            filter->y[i] = 0.0f; \
        } \
        filter->pos = 0; \
    } \
    \
    f32 process##NAME##Filter(struct NAME##Filter* filter, f32 input) { \
        filter->pos = (filter->pos + 1) % (ORDER + 1); \
        filter->x[filter->pos] = input; \
        \
        f32 output = 0.0f; \
        static const f32 coefficients[][ORDER + 1] = COEFFS; \
        \
        for (int i = 0; i <= ORDER; i++) { \
            int xIndex = (filter->pos - i + ORDER + 1) % (ORDER + 1); \
            int yIndex = (filter->pos - i + ORDER + 1) % (ORDER + 1); \
            output += coefficients[0][i] * filter->x[xIndex]; \
            if (i > 0) { \
                output -= coefficients[1][i] * filter->y[yIndex]; \
            } \
        } \
        \
        filter->y[filter->pos] = output; \
        return output; \
    }

// Create specific filter types with coefficients
DECLARE_FILTER(Lowpass, 
    {{0.2929f, 0.5858f, 0.2929f}, {1.0f, -0.0f, 0.1716f}}, 2)

DECLARE_FILTER(Highpass,
    {{0.9150f, -1.8299f, 0.9150f}, {1.0f, -1.8227f, 0.8372f}}, 2)

DECLARE_FILTER(Bandpass,
    {{0.0176f, 0.0f, -0.0176f}, {1.0f, -1.8405f, 0.9648f}}, 2)

// Usage
void setupFilters() {
    struct LowpassFilter lpf;
    struct HighpassFilter hpf;
    struct BandpassFilter bpf;
    
    initLowpassFilter(&lpf);
    initHighpassFilter(&hpf);
    initBandpassFilter(&bpf);
    
    // Process audio through filter chain
    f32 sample = 0.8f;
    sample = processLowpassFilter(&lpf, sample);
    sample = processHighpassFilter(&hpf, sample);
    sample = processBandpassFilter(&bpf, sample);
}
```

## Template-Like Pattern Implementation

### Generic Data Structure Patterns

Implement container-like patterns with type safety:

```impala
// Generic linked list pattern
#define DECLARE_LIST(TYPE, NAME) \
    struct NAME##Node { \
        TYPE data; \
        struct NAME##Node* next; \
    }; \
    \
    struct NAME##List { \
        struct NAME##Node* head; \
        struct NAME##Node* tail; \
        int count; \
    }; \
    \
    void init##NAME##List(struct NAME##List* list) { \
        list->head = null; \
        list->tail = null; \
        list->count = 0; \
    } \
    \
    bool add##NAME##List(struct NAME##List* list, TYPE value) { \
        struct NAME##Node* node = (struct NAME##Node*)allocate(sizeof(struct NAME##Node)); \
        if (!node) return false; \
        \
        node->data = value; \
        node->next = null; \
        \
        if (list->tail) { \
            list->tail->next = node; \
        } else { \
            list->head = node; \
        } \
        list->tail = node; \
        list->count++; \
        return true; \
    } \
    \
    bool remove##NAME##List(struct NAME##List* list, TYPE value, bool (*equals)(TYPE a, TYPE b)) { \
        struct NAME##Node** current = &list->head; \
        while (*current) { \
            if (equals((*current)->data, value)) { \
                struct NAME##Node* toDelete = *current; \
                *current = (*current)->next; \
                if (toDelete == list->tail) { \
                    list->tail = (list->head == toDelete) ? null : list->head; \
                } \
                deallocate(toDelete); \
                list->count--; \
                return true; \
            } \
            current = &(*current)->next; \
        } \
        return false; \
    } \
    \
    void forEach##NAME##List(struct NAME##List* list, void (*callback)(TYPE value, void* userdata), void* userdata) { \
        struct NAME##Node* current = list->head; \
        while (current) { \
            callback(current->data, userdata); \
            current = current->next; \
        } \
    }

// Create specific list types
DECLARE_LIST(f32, Sample)
DECLARE_LIST(int, Event)

// Comparison functions for different types
bool floatEquals(f32 a, f32 b) {
    return fabs(a - b) < 0.0001f;
}

bool intEquals(int a, int b) {
    return a == b;
}

// Usage
void useLists() {
    struct SampleList samples;
    struct EventList events;
    
    initSampleList(&samples);
    initEventList(&events);
    
    addSampleList(&samples, 0.5f);
    addSampleList(&samples, 0.8f);
    addEventList(&events, 440);
    addEventList(&events, 880);
    
    removeSampleList(&samples, 0.5f, floatEquals);
    removeEventList(&events, 440, intEquals);
}
```

### Function Template Patterns

Create function templates using macro-based approaches:

```impala
// Generic sorting algorithm
#define DECLARE_SORT(TYPE, NAME, COMPARE_FUNC) \
    void sort##NAME(TYPE* array, int size) { \
        for (int i = 1; i < size; i++) { \
            TYPE key = array[i]; \
            int j = i - 1; \
            \
            while (j >= 0 && COMPARE_FUNC(array[j], key) > 0) { \
                array[j + 1] = array[j]; \
                j = j - 1; \
            } \
            array[j + 1] = key; \
        } \
    } \
    \
    int binarySearch##NAME(TYPE* array, int size, TYPE target) { \
        int left = 0; \
        int right = size - 1; \
        \
        while (left <= right) { \
            int mid = left + (right - left) / 2; \
            int cmp = COMPARE_FUNC(array[mid], target); \
            \
            if (cmp == 0) return mid; \
            if (cmp < 0) left = mid + 1; \
            else right = mid - 1; \
        } \
        return -1; \
    }

// Comparison functions
int compareFloat(f32 a, f32 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

int compareInt(int a, int b) {
    return a - b;
}

// Generate sort functions for different types
DECLARE_SORT(f32, Float, compareFloat)
DECLARE_SORT(int, Int, compareInt)

// Usage
void sortingExample() {
    f32 samples[] = {0.8f, 0.2f, 0.9f, 0.1f, 0.5f};
    int frequencies[] = {880, 220, 440, 110, 660};
    
    sortFloat(samples, 5);
    sortInt(frequencies, 5);
    
    int index = binarySearchFloat(samples, 5, 0.5f);
    int freqIndex = binarySearchInt(frequencies, 5, 440);
}
```

## Conditional Compilation Strategies

### Feature Flag System

Implement comprehensive feature flag management:

```impala
// Feature configuration header
#ifndef PERMUT8_FEATURES_H
#define PERMUT8_FEATURES_H

// Audio processing features
#define FEATURE_REVERB_ENABLED    1
#define FEATURE_DELAY_ENABLED     1
#define FEATURE_FILTER_ENABLED    1
#define FEATURE_DISTORTION_ENABLED 0  // Disabled for space
#define FEATURE_MODULATION_ENABLED 1

// Hardware features
#define FEATURE_MIDI_ENABLED      1
#define FEATURE_USB_ENABLED       0  // No USB support
#define FEATURE_SD_CARD_ENABLED   1

// Debug features (only in debug builds)
#ifdef DEBUG
#define FEATURE_MEMORY_DEBUG      1
#define FEATURE_PERFORMANCE_STATS 1
#define FEATURE_AUDIO_SCOPE       1
#else
#define FEATURE_MEMORY_DEBUG      0
#define FEATURE_PERFORMANCE_STATS 0
#define FEATURE_AUDIO_SCOPE       0
#endif

// Platform-specific features
#ifdef PERMUT8_V2
#define FEATURE_ENHANCED_DAC      1
#define FEATURE_EXTRA_MEMORY      1
#else
#define FEATURE_ENHANCED_DAC      0
#define FEATURE_EXTRA_MEMORY      0
#endif

#endif // PERMUT8_FEATURES_H

// Conditional code inclusion
#if FEATURE_REVERB_ENABLED
#include "reverb.h"
#endif

#if FEATURE_DELAY_ENABLED
#include "delay.h"
#endif

#if FEATURE_MEMORY_DEBUG
#include "memory_debug.h"
#endif

// Feature-dependent function compilation
void initializeAudioEffects() {
    #if FEATURE_REVERB_ENABLED
    initReverb();
    #endif
    
    #if FEATURE_DELAY_ENABLED
    initDelay();
    #endif
    
    #if FEATURE_FILTER_ENABLED
    initFilters();
    #endif
    
    #if FEATURE_DISTORTION_ENABLED
    initDistortion();
    #endif
}

// Conditional compilation with fallbacks
f32 processAudioEffect(f32 input, int effectType) {
    switch (effectType) {
        #if FEATURE_REVERB_ENABLED
        case EFFECT_REVERB:
            return processReverb(input);
        #endif
        
        #if FEATURE_DELAY_ENABLED
        case EFFECT_DELAY:
            return processDelay(input);
        #endif
        
        #if FEATURE_FILTER_ENABLED
        case EFFECT_FILTER:
            return processFilter(input);
        #endif
        
        default:
            return input; // Pass-through for disabled effects
    }
}
```

### Build Configuration System

Create sophisticated build configuration management:

```impala
// Build configuration macros
#define BUILD_CONFIG_PERFORMANCE  1
#define BUILD_CONFIG_SIZE         2
#define BUILD_CONFIG_DEBUGGING    3

#ifndef BUILD_CONFIG
#define BUILD_CONFIG BUILD_CONFIG_PERFORMANCE
#endif

// Performance build configuration
#if BUILD_CONFIG == BUILD_CONFIG_PERFORMANCE
    #define ENABLE_SIMD_OPTIMIZATIONS    1
    #define ENABLE_LOOP_UNROLLING        1
    #define ENABLE_INLINE_EXPANSION      1
    #define BUFFER_SIZE                  512
    #define MAX_VOICES                   32
    #define MEMORY_POOL_SIZE            (64 * 1024)
    #define DEBUG_CHECKS                 0
#endif

// Size-optimized build configuration
#if BUILD_CONFIG == BUILD_CONFIG_SIZE
    #define ENABLE_SIMD_OPTIMIZATIONS    0
    #define ENABLE_LOOP_UNROLLING        0
    #define ENABLE_INLINE_EXPANSION      0
    #define BUFFER_SIZE                  256
    #define MAX_VOICES                   16
    #define MEMORY_POOL_SIZE            (32 * 1024)
    #define DEBUG_CHECKS                 0
#endif

// Debug build configuration
#if BUILD_CONFIG == BUILD_CONFIG_DEBUGGING
    #define ENABLE_SIMD_OPTIMIZATIONS    0
    #define ENABLE_LOOP_UNROLLING        0
    #define ENABLE_INLINE_EXPANSION      0
    #define BUFFER_SIZE                  128
    #define MAX_VOICES                   8
    #define MEMORY_POOL_SIZE            (16 * 1024)
    #define DEBUG_CHECKS                 1
#endif

// Conditional function attributes
#if ENABLE_INLINE_EXPANSION
    #define FORCE_INLINE __attribute__((always_inline)) inline
#else
    #define FORCE_INLINE
#endif

// Configuration-dependent implementations
#if ENABLE_SIMD_OPTIMIZATIONS
FORCE_INLINE void vectorAdd(f32* a, f32* b, f32* result, int count) {
    // SIMD implementation
    for (int i = 0; i < count; i += 4) {
        __m128 va = _mm_load_ps(&a[i]);
        __m128 vb = _mm_load_ps(&b[i]);
        __m128 vr = _mm_add_ps(va, vb);
        _mm_store_ps(&result[i], vr);
    }
}
#else
FORCE_INLINE void vectorAdd(f32* a, f32* b, f32* result, int count) {
    // Scalar implementation
    for (int i = 0; i < count; i++) {
        result[i] = a[i] + b[i];
    }
}
#endif
```

## Advanced Function Pointer Patterns

### Dynamic Dispatch Systems

Implement flexible dispatch mechanisms using function pointers:

```impala
// Abstract audio processor interface
typedef struct AudioProcessor AudioProcessor;

typedef bool (*InitFunc)(AudioProcessor* proc);
typedef void (*ProcessFunc)(AudioProcessor* proc, f32* input, f32* output, int samples);
typedef void (*SetParameterFunc)(AudioProcessor* proc, int param, f32 value);
typedef f32 (*GetParameterFunc)(AudioProcessor* proc, int param);
typedef void (*DestroyFunc)(AudioProcessor* proc);

struct AudioProcessorVTable {
    InitFunc init;
    ProcessFunc process;
    SetParameterFunc setParameter;
    GetParameterFunc getParameter;
    DestroyFunc destroy;
    const char* name;
    int parameterCount;
};

struct AudioProcessor {
    const struct AudioProcessorVTable* vtable;
    void* instanceData;
    bool initialized;
};

// Generic processor operations
bool initProcessor(AudioProcessor* proc) {
    if (proc->vtable->init) {
        proc->initialized = proc->vtable->init(proc);
        return proc->initialized;
    }
    return false;
}

void processAudio(AudioProcessor* proc, f32* input, f32* output, int samples) {
    if (proc->initialized && proc->vtable->process) {
        proc->vtable->process(proc, input, output, samples);
    }
}

void setParameter(AudioProcessor* proc, int param, f32 value) {
    if (proc->initialized && proc->vtable->setParameter) {
        proc->vtable->setParameter(proc, param, value);
    }
}

// Specific processor implementations
struct ReverbData {
    f32 roomSize;
    f32 damping;
    f32 wetLevel;
    f32 dryLevel;
    // ... reverb-specific data
};

bool reverbInit(AudioProcessor* proc) {
    struct ReverbData* data = (struct ReverbData*)allocate(sizeof(struct ReverbData));
    if (!data) return false;
    
    data->roomSize = 0.5f;
    data->damping = 0.5f;
    data->wetLevel = 0.3f;
    data->dryLevel = 0.7f;
    
    proc->instanceData = data;
    return true;
}

void reverbProcess(AudioProcessor* proc, f32* input, f32* output, int samples) {
    struct ReverbData* data = (struct ReverbData*)proc->instanceData;
    // Reverb processing implementation
    for (int i = 0; i < samples; i++) {
        f32 wet = processReverbAlgorithm(input[i], data);
        output[i] = data->dryLevel * input[i] + data->wetLevel * wet;
    }
}

void reverbSetParameter(AudioProcessor* proc, int param, f32 value) {
    struct ReverbData* data = (struct ReverbData*)proc->instanceData;
    switch (param) {
        case 0: data->roomSize = value; break;
        case 1: data->damping = value; break;
        case 2: data->wetLevel = value; break;
        case 3: data->dryLevel = value; break;
    }
}

void reverbDestroy(AudioProcessor* proc) {
    if (proc->instanceData) {
        deallocate(proc->instanceData);
        proc->instanceData = null;
    }
}

// Reverb processor vtable
static const struct AudioProcessorVTable reverbVTable = {
    .init = reverbInit,
    .process = reverbProcess,
    .setParameter = reverbSetParameter,
    .getParameter = null, // Use default implementation
    .destroy = reverbDestroy,
    .name = "Reverb",
    .parameterCount = 4
};

// Processor factory
AudioProcessor* createProcessor(const struct AudioProcessorVTable* vtable) {
    AudioProcessor* proc = (AudioProcessor*)allocate(sizeof(AudioProcessor));
    if (proc) {
        proc->vtable = vtable;
        proc->instanceData = null;
        proc->initialized = false;
    }
    return proc;
}

// Usage
void audioProcessingChain() {
    AudioProcessor* reverb = createProcessor(&reverbVTable);
    
    if (initProcessor(reverb)) {
        setParameter(reverb, 0, 0.8f); // Room size
        setParameter(reverb, 2, 0.4f); // Wet level
        
        f32 inputBuffer[BUFFER_SIZE];
        f32 outputBuffer[BUFFER_SIZE];
        
        processAudio(reverb, inputBuffer, outputBuffer, BUFFER_SIZE);
    }
}
```

### Callback Systems

Implement flexible callback mechanisms for event handling:

```impala
// Event callback system
typedef enum {
    EVENT_PARAMETER_CHANGED,
    EVENT_NOTE_ON,
    EVENT_NOTE_OFF,
    EVENT_TEMPO_CHANGED,
    EVENT_PRESET_CHANGED
} EventType;

typedef struct {
    EventType type;
    int param1;
    int param2;
    f32 value;
    void* userData;
} Event;

typedef void (*EventCallback)(const Event* event, void* userData);

struct CallbackNode {
    EventCallback callback;
    void* userData;
    struct CallbackNode* next;
};

struct EventDispatcher {
    struct CallbackNode* callbacks[16]; // One list per event type
    struct CallbackNode* freeNodes;
    struct CallbackNode nodePool[MAX_CALLBACKS];
    int poolIndex;
};

static struct EventDispatcher eventDispatcher;

void initEventDispatcher() {
    for (int i = 0; i < 16; i++) {
        eventDispatcher.callbacks[i] = null;
    }
    
    // Initialize free list
    eventDispatcher.freeNodes = null;
    for (int i = 0; i < MAX_CALLBACKS; i++) {
        eventDispatcher.nodePool[i].next = eventDispatcher.freeNodes;
        eventDispatcher.freeNodes = &eventDispatcher.nodePool[i];
    }
    eventDispatcher.poolIndex = 0;
}

bool registerCallback(EventType type, EventCallback callback, void* userData) {
    if (type >= 16 || !eventDispatcher.freeNodes) return false;
    
    struct CallbackNode* node = eventDispatcher.freeNodes;
    eventDispatcher.freeNodes = node->next;
    
    node->callback = callback;
    node->userData = userData;
    node->next = eventDispatcher.callbacks[type];
    eventDispatcher.callbacks[type] = node;
    
    return true;
}

void dispatchEvent(const Event* event) {
    if (event->type >= 16) return;
    
    struct CallbackNode* node = eventDispatcher.callbacks[event->type];
    while (node) {
        node->callback(event, node->userData);
        node = node->next;
    }
}

// Example callback implementations
void onParameterChanged(const Event* event, void* userData) {
    logInfo("Parameter %d changed to %f", event->param1, event->value);
    updateProcessorParameter(event->param1, event->value);
}

void onNoteEvent(const Event* event, void* userData) {
    if (event->type == EVENT_NOTE_ON) {
        startVoice(event->param1, event->value); // note, velocity
    } else if (event->type == EVENT_NOTE_OFF) {
        stopVoice(event->param1);
    }
}

// Usage
void setupEventHandling() {
    initEventDispatcher();
    
    registerCallback(EVENT_PARAMETER_CHANGED, onParameterChanged, null);
    registerCallback(EVENT_NOTE_ON, onNoteEvent, null);
    registerCallback(EVENT_NOTE_OFF, onNoteEvent, null);
    
    // Dispatch events
    Event paramEvent = {EVENT_PARAMETER_CHANGED, 5, 0, 0.8f, null};
    dispatchEvent(&paramEvent);
    
    Event noteEvent = {EVENT_NOTE_ON, 60, 0, 0.9f, null}; // Middle C, velocity 0.9
    dispatchEvent(&noteEvent);
}
```

## Code Generation Tools

### Build-Time Code Generation

Implement sophisticated build-time code generation systems:

```impala
// Generator script (would be run during build)
/*
#!/usr/bin/env python3

# This script generates effect processor implementations
# Based on configuration files

import json
import sys

def generate_effect_processor(config):
    name = config['name']
    params = config['parameters']
    
    # Generate header
    header = f"""
// Auto-generated {name} processor
// Generated from {config['source_file']}

struct {name}Data {{
"""
    
    # Generate parameter structure
    for param in params:
        header += f"    f32 {param['name']}; // {param['description']}\n"
    
    header += f"""
    // Processing state
    f32 processingBuffer[BUFFER_SIZE];
    int stateIndex;
}};

bool {name.lower()}Init(AudioProcessor* proc);
void {name.lower()}Process(AudioProcessor* proc, f32* input, f32* output, int samples);
void {name.lower()}SetParameter(AudioProcessor* proc, int param, f32 value);
f32 {name.lower()}GetParameter(AudioProcessor* proc, int param);
void {name.lower()}Destroy(AudioProcessor* proc);

static const struct AudioProcessorVTable {name.lower()}VTable = {{
    .init = {name.lower()}Init,
    .process = {name.lower()}Process,
    .setParameter = {name.lower()}SetParameter,
    .getParameter = {name.lower()}GetParameter,
    .destroy = {name.lower()}Destroy,
    .name = "{name}",
    .parameterCount = {len(params)}
}};
"""
    
    # Generate implementation
    impl = f"""
bool {name.lower()}Init(AudioProcessor* proc) {{
    struct {name}Data* data = (struct {name}Data*)allocate(sizeof(struct {name}Data));
    if (!data) return false;
    
    // Initialize parameters to defaults
"""
    
    for i, param in enumerate(params):
        impl += f"    data->{param['name']} = {param['default']}f; // {param['description']}\n"
    
    impl += f"""
    data->stateIndex = 0;
    proc->instanceData = data;
    return true;
}}

void {name.lower()}SetParameter(AudioProcessor* proc, int param, f32 value) {{
    struct {name}Data* data = (struct {name}Data*)proc->instanceData;
    switch (param) {{
"""
    
    for i, param in enumerate(params):
        impl += f"        case {i}: data->{param['name']} = value; break; // {param['description']}\n"
    
    impl += """    }
}

// ... rest of implementation would be generated based on DSP algorithm
"""
    
    return header + impl

# Usage: python generate_effects.py config.json output.h
if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        config = json.load(f)
    
    code = generate_effect_processor(config)
    
    with open(sys.argv[2], 'w') as f:
        f.write(code)
*/

// Example configuration file (effects.json):
/*
{
    "name": "Chorus",
    "source_file": "chorus_config.json",
    "parameters": [
        {"name": "rate", "description": "LFO rate", "default": 1.0, "min": 0.1, "max": 10.0},
        {"name": "depth", "description": "Modulation depth", "default": 0.5, "min": 0.0, "max": 1.0},
        {"name": "delay", "description": "Base delay time", "default": 10.0, "min": 1.0, "max": 50.0},
        {"name": "feedback", "description": "Feedback amount", "default": 0.2, "min": 0.0, "max": 0.9},
        {"name": "wetLevel", "description": "Effect level", "default": 0.5, "min": 0.0, "max": 1.0}
    ]
}
*/
```

### Template Instantiation System

Create a template instantiation system for common patterns:

```impala
// Template definition file (oscillator.template)
/*
// Template parameters: TYPE, NAME, WAVE_FUNC
struct %NAME%Oscillator {
    f32 frequency;
    f32 phase;
    f32 amplitude;
    %TYPE% waveTable[WAVE_TABLE_SIZE];
    bool useTable;
};

void init%NAME%Oscillator(struct %NAME%Oscillator* osc, f32 freq) {
    osc->frequency = freq;
    osc->phase = 0.0f;
    osc->amplitude = 1.0f;
    osc->useTable = false;
    
    // Pre-compute wave table for efficiency
    for (int i = 0; i < WAVE_TABLE_SIZE; i++) {
        f32 x = (f32)i / WAVE_TABLE_SIZE * TWO_PI;
        osc->waveTable[i] = (%TYPE%)%WAVE_FUNC%(x);
    }
    osc->useTable = true;
}

%TYPE% process%NAME%Oscillator(struct %NAME%Oscillator* osc) {
    %TYPE% result;
    
    if (osc->useTable) {
        // Table lookup with interpolation
        f32 index = (osc->phase / TWO_PI) * WAVE_TABLE_SIZE;
        int i1 = (int)index;
        int i2 = (i1 + 1) % WAVE_TABLE_SIZE;
        f32 frac = index - i1;
        
        result = osc->waveTable[i1] * (1.0f - frac) + osc->waveTable[i2] * frac;
    } else {
        // Direct calculation
        result = (%TYPE%)%WAVE_FUNC%(osc->phase);
    }
    
    // Update phase
    osc->phase += osc->frequency * PHASE_INCREMENT;
    if (osc->phase >= TWO_PI) {
        osc->phase -= TWO_PI;
    }
    
    return result * osc->amplitude;
}
*/

// Template instantiation macro
#define INSTANTIATE_OSCILLATOR(TYPE, NAME, WAVE_FUNC) \
    struct NAME##Oscillator { \
        f32 frequency; \
        f32 phase; \
        f32 amplitude; \
        TYPE waveTable[WAVE_TABLE_SIZE]; \
        bool useTable; \
    }; \
    \
    void init##NAME##Oscillator(struct NAME##Oscillator* osc, f32 freq) { \
        osc->frequency = freq; \
        osc->phase = 0.0f; \
        osc->amplitude = 1.0f; \
        osc->useTable = false; \
        \
        for (int i = 0; i < WAVE_TABLE_SIZE; i++) { \
            f32 x = (f32)i / WAVE_TABLE_SIZE * TWO_PI; \
            osc->waveTable[i] = (TYPE)WAVE_FUNC(x); \
        } \
        osc->useTable = true; \
    } \
    \
    TYPE process##NAME##Oscillator(struct NAME##Oscillator* osc) { \
        TYPE result; \
        \
        if (osc->useTable) { \
            f32 index = (osc->phase / TWO_PI) * WAVE_TABLE_SIZE; \
            int i1 = (int)index; \
            int i2 = (i1 + 1) % WAVE_TABLE_SIZE; \
            f32 frac = index - i1; \
            \
            result = osc->waveTable[i1] * (1.0f - frac) + osc->waveTable[i2] * frac; \
        } else { \
            result = (TYPE)WAVE_FUNC(osc->phase); \
        } \
        \
        osc->phase += osc->frequency * PHASE_INCREMENT; \
        if (osc->phase >= TWO_PI) { \
            osc->phase -= TWO_PI; \
        } \
        \
        return result * osc->amplitude; \
    }

// Instantiate different oscillator types
INSTANTIATE_OSCILLATOR(f32, Sine, sinf)
INSTANTIATE_OSCILLATOR(f32, Cosine, cosf)
INSTANTIATE_OSCILLATOR(f32, Triangle, triangleWave)
INSTANTIATE_OSCILLATOR(f32, Sawtooth, sawtoothWave)
INSTANTIATE_OSCILLATOR(f32, Square, squareWave)

// Custom wave functions
f32 triangleWave(f32 phase) {
    return 2.0f * fabs(2.0f * (phase / TWO_PI - floorf(phase / TWO_PI + 0.5f))) - 1.0f;
}

f32 sawtoothWave(f32 phase) {
    return 2.0f * (phase / TWO_PI - floorf(phase / TWO_PI + 0.5f));
}

f32 squareWave(f32 phase) {
    return (phase < PI) ? 1.0f : -1.0f;
}

// Usage
void useOscillators() {
    struct SineOscillator sine;
    struct TriangleOscillator triangle;
    struct SawtoothOscillator sawtooth;
    
    initSineOscillator(&sine, 440.0f);
    initTriangleOscillator(&triangle, 220.0f);
    initSawtoothOscillator(&sawtooth, 110.0f);
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        f32 sineOutput = processSineOscillator(&sine);
        f32 triangleOutput = processTriangleOscillator(&triangle);
        f32 sawtoothOutput = processSawtoothOscillator(&sawtooth);
        
        f32 mixed = (sineOutput + triangleOutput + sawtoothOutput) / 3.0f;
        // Output mixed signal
    }
}
```

## Integration with Build Systems

### Makefile Integration

Integrate code generation with the build system:

```makefile
# Makefile excerpt for code generation

# Generated files
GENERATED_SOURCES = generated_effects.c generated_oscillators.c generated_filters.c
GENERATED_HEADERS = generated_effects.h generated_oscillators.h generated_filters.h

# Generation rules
generated_effects.h generated_effects.c: effects.json generate_effects.py
	python3 generate_effects.py effects.json generated_effects.h generated_effects.c

generated_oscillators.h generated_oscillators.c: oscillators.template instantiate_oscillators.py
	python3 instantiate_oscillators.py oscillators.template generated_oscillators.h generated_oscillators.c

generated_filters.h generated_filters.c: filter_configs/*.json generate_filters.py
	python3 generate_filters.py filter_configs/ generated_filters.h generated_filters.c

# Make sure generated files are built before main compilation
$(OBJECTS): $(GENERATED_HEADERS)

# Clean rule
clean:
	rm -f $(GENERATED_SOURCES) $(GENERATED_HEADERS)

.PHONY: generate clean
generate: $(GENERATED_SOURCES) $(GENERATED_HEADERS)
```

### Advanced Build Configuration

Create sophisticated build configuration systems:

```impala
// Build configuration system
#include "build_config.h"

// Feature matrix compilation
#ifdef BUILD_FEATURE_MATRIX
    static const bool FEATURES[MAX_FEATURES] = {
        #include "feature_matrix.inc"
    };
    
    #define FEATURE_ENABLED(id) (FEATURES[id])
#else
    #define FEATURE_ENABLED(id) (FEATURE_##id##_ENABLED)
#endif

// Dynamic vs static dispatch based on build config
#ifdef BUILD_DYNAMIC_DISPATCH
    #define CALL_PROCESSOR(type, func, ...) \
        processorVTables[type].func(__VA_ARGS__)
#else
    #define CALL_PROCESSOR(type, func, ...) \
        switch(type) { \
            case PROCESSOR_REVERB: reverb##func(__VA_ARGS__); break; \
            case PROCESSOR_DELAY: delay##func(__VA_ARGS__); break; \
            case PROCESSOR_FILTER: filter##func(__VA_ARGS__); break; \
            default: break; \
        }
#endif

// Memory allocation strategy based on build config
#ifdef BUILD_STATIC_ALLOCATION
    #define ALLOCATE(size) allocateFromPool(size)
    #define DEALLOCATE(ptr) deallocateToPool(ptr)
#else
    #define ALLOCATE(size) malloc(size)
    #define DEALLOCATE(ptr) free(ptr)
#endif
```

## Best Practices Summary

### Metaprogramming Guidelines

1. **Maintain Readability** - Complex macros should be well-documented and debuggable
2. **Avoid Over-Abstraction** - Don't abstract away important details
3. **Use Type Safety** - Leverage compile-time checks where possible
4. **Consider Debugging** - Generated code should be debugger-friendly
5. **Document Generation** - Keep clear records of what generates what

### Code Generation Principles

1. **Separate Concerns** - Keep generators separate from generated code
2. **Version Control** - Track both generators and generated outputs appropriately
3. **Build Integration** - Make generation part of normal build process
4. **Error Handling** - Generators should fail gracefully with clear messages
5. **Performance** - Generated code should be as efficient as hand-written

### Advanced Pattern Recommendations

1. **Function Pointers** - Use for runtime polymorphism when needed
2. **X-Macros** - Excellent for maintaining consistency across related code
3. **Feature Flags** - Essential for managing code size and complexity
4. **Template Patterns** - Reduce code duplication while maintaining performance
5. **Build-Time Generation** - Move complexity from runtime to build time

Metaprogramming in Permut8 firmware requires careful balance between flexibility and performance. The techniques in this document provide the foundation for creating maintainable, efficient, and flexible audio processing systems while preserving real-time guarantees.

These patterns enable advanced code organization and reuse while maintaining the deterministic behavior required for professional audio applications. Use them judiciously to create robust, maintainable firmware that can evolve with changing requirements.
