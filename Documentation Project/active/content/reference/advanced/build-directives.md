# Build Directives and Compilation Options

## Overview
Control the Impala-to-GAZL compilation process with build directives, optimization flags, and configuration options to create efficient, debuggable, and deployment-ready firmware.

## Core Build Directives

### Project Configuration
```impala
// Project metadata and build settings
#project "MyCustomEffect"
#version "1.2.3"
#author "Developer Name"
#description "Custom delay with modulation"

// Target device configuration
#target permut8_v2
#sample_rate 48000
#buffer_size 128

// Memory allocation
#heap_size 8192        // Bytes for dynamic allocation
#stack_size 1024       // Bytes for function call stack
#delay_memory 16384    // Bytes for delay line buffers
```

### Optimization Levels
```impala
// Optimization control
#optimize speed        // Prioritize execution speed
// #optimize size      // Prioritize code size
// #optimize debug     // Disable optimizations for debugging
// #optimize balanced  // Balance speed and size

// Specific optimizations
#enable loop_unroll    // Unroll small loops
#enable inline_small   // Inline functions < 32 instructions
#enable const_fold     // Constant folding optimization
#enable dead_code      // Remove unreachable code

// Advanced optimizations (use with caution)
// #enable unsafe_math     // Fast math with reduced precision
// #enable assume_aligned  // Assume memory alignment
```

### Debug Configuration
```impala
// Debug build settings
#ifdef DEBUG
    #enable assert         // Enable runtime assertions
    #enable bounds_check   // Array bounds checking
    #enable stack_check    // Stack overflow detection
    #enable trace          // Function call tracing
    #debug_symbols full    // Full debugging information
#else
    #debug_symbols minimal // Minimal debug info for release
#endif

// Conditional compilation
#define DEVELOPMENT_BUILD  // Custom build flags
#define ENABLE_PROFILING   // Performance measurement
```

## Memory Management Directives

### Buffer Allocation
```impala
// Static buffer allocation
#declare_buffer delay_line[16384]      // Fixed-size delay buffer
#declare_buffer temp_buffer[512]       // Temporary processing buffer
#declare_buffer coefficient_table[256] // Lookup table storage

// Dynamic allocation control
#enable dynamic_alloc   // Allow runtime allocation
#max_dynamic_size 4096  // Limit dynamic memory usage

// Memory layout optimization
#align_buffers 16       // 16-byte alignment for SIMD
#pack_structs          // Minimize struct padding
#cache_line_size 64    // Optimize for CPU cache
```

### Memory Safety
```impala
// Memory protection directives
#enable buffer_overflow_check   // Runtime buffer checks
#enable null_pointer_check     // Null pointer detection
#enable memory_leak_check      // Track allocation/deallocation

// Static analysis
#warn unused_variables         // Warn about unused variables
#warn uninitialized_access    // Warn about uninitialized reads
#error buffer_overrun         // Error on static buffer analysis
```

## Performance Optimization

### Instruction Set Control
```impala
// Target CPU features
#cpu_features baseline         // Basic instruction set only
// #cpu_features sse2         // Enable SSE2 instructions
// #cpu_features avx          // Enable AVX instructions
// #cpu_features neon         // ARM NEON instructions

// Floating-point precision
#float_precision single       // 32-bit floats (default)
// #float_precision double    // 64-bit floats
// #float_precision half      // 16-bit floats (if supported)

// Mathematical optimizations
#fast_math reciprocal         // Fast reciprocal approximation
#fast_math sqrt              // Fast square root approximation
#fast_math trigonometric     // Fast sin/cos lookup tables
```

### Loop Optimization
```impala
// Loop transformation directives
#pragma loop_vectorize enable    // Enable auto-vectorization
#pragma loop_unroll count(4)     // Unroll loops 4 times
#pragma loop_pipeline enable     // Enable instruction pipelining

// Manual loop control
void optimizedProcessing() {
    #pragma loop_vectorize_width(4)
    for (int i = 0; i < BUFFER_SIZE; i += 4) {
        // Process 4 samples at once
        signal[i]   = applyEffect(signal[i]);
        signal[i+1] = applyEffect(signal[i+1]);
        signal[i+2] = applyEffect(signal[i+2]);
        signal[i+3] = applyEffect(signal[i+3]);
    }
}
```

### Function Optimization
```impala
// Function inlining control
#inline always
float criticalFunction(float input) {
    // Always inlined for performance
    return input * 0.5 + 0.25;
}

#inline never
void debugPrintFunction(float value) {
    // Never inlined to save code space
    printf("Debug: %f\n", value);
}

// Hot path optimization
#hot_path
void audioProcessingLoop() {
    // Mark as frequently executed
    // Compiler will prioritize optimization
}

#cold_path
void errorHandling() {
    // Mark as rarely executed
    // Deprioritize for optimization
}
```

## Build Configurations

### Release Configuration
```impala
// Production build settings
#configuration release

#optimize speed
#enable loop_unroll
#enable inline_small
#enable const_fold
#enable dead_code

#disable assert
#disable bounds_check
#disable trace
#debug_symbols minimal

// Size optimization for deployment
#strip unused_functions
#compress_constants
#merge_identical_functions
```

### Debug Configuration
```impala
// Development build settings
#configuration debug

#optimize debug
#disable loop_unroll  // Keep code readable
#disable inline_small // Preserve function boundaries

#enable assert
#enable bounds_check
#enable stack_check
#enable trace
#debug_symbols full

// Additional debug features
#enable memory_profiler
#enable performance_counters
#output_assembly_listing
```

### Profiling Configuration
```impala
// Performance analysis build
#configuration profile

#optimize balanced  // Some optimization for realistic performance
#enable inline_small
#disable loop_unroll  // Preserve loop structure for profiling

// Profiling instrumentation
#enable cycle_counting
#enable function_timing
#enable memory_tracking
#profile_output "performance_data.json"

// Hot spot identification
#instrument_branches
#instrument_memory_access
#instrument_function_calls
```

## Advanced Build Features

### Conditional Compilation
```impala
// Feature flags
#ifdef ENABLE_REVERB
    #include "reverb_engine.imp"
    #define HAS_REVERB 1
#else
    #define HAS_REVERB 0
#endif

#ifdef COMPACT_BUILD
    #define MAX_DELAY_TIME 1000
    #disable expensive_features
#else
    #define MAX_DELAY_TIME 5000
    #enable all_features
#endif

// Version-specific code
#if VERSION >= 2.0
    // New features for v2.0+
    void newFeature() { /* implementation */ }
#endif
```

### Custom Compilation Stages
```impala
// Pre-compilation processing
#preprocess
    generate_coefficient_tables();
    validate_memory_layout();
    optimize_parameter_mapping();
#end_preprocess

// Post-compilation validation
#postprocess
    verify_timing_constraints();
    check_memory_usage();
    validate_audio_range();
#end_postprocess

// Build-time code generation
#generate_lookup_table sin_table 256 sin(x * 2 * PI / 256)
#generate_lookup_table exp_table 128 exp(-x / 128.0)
```

### Platform-Specific Builds
```impala
// Hardware variant targeting
#ifdef PERMUT8_V1
    #define LED_COUNT 4
    #define CV_INPUTS 2
    #sample_rate 44100
#endif

#ifdef PERMUT8_V2
    #define LED_COUNT 8
    #define CV_INPUTS 4
    #sample_rate 48000
    #enable advanced_dsp
#endif

// Feature availability
#if HAS_EXTERNAL_MEMORY
    #enable large_buffers
    #max_delay_time 10.0  // 10 seconds
#else
    #max_delay_time 2.0   // 2 seconds
#endif
```

## Error Handling and Validation

### Compile-Time Checks
```impala
// Static assertions
#static_assert(BUFFER_SIZE % 4 == 0, "Buffer size must be multiple of 4")
#static_assert(MAX_DELAY_TIME < 60.0, "Delay time too large for memory")
#static_assert(sizeof(AudioSample) == 4, "Unexpected sample size")

// Resource validation
#check_memory_usage()     // Verify memory fits in device
#check_timing_budget()    // Verify real-time performance
#check_parameter_ranges() // Validate parameter limits

// Dependency validation
#require_feature floating_point
#require_memory_size 32768
#require_cpu_speed 100MHz
```

### Build Warnings and Errors
```impala
// Custom diagnostics
#warning "Using experimental feature in build"
#error "Missing required configuration option"
#deprecated "This function will be removed in v3.0"

// Performance warnings
#warn_if_slow(function_name, 1000)  // Warn if > 1000 cycles
#warn_if_large(buffer_name, 8192)   // Warn if > 8KB
#warn_if_recursive(function_name)   // Warn about recursion
```

## Deployment and Distribution

### Firmware Packaging
```impala
// Firmware metadata
#firmware_info {
    .name = "Custom Delay v1.2",
    .author = "Developer Name",
    .version = {1, 2, 0},
    .build_date = __BUILD_DATE__,
    .checksum = __FIRMWARE_CHECKSUM__
}

// Parameter metadata for host integration
#parameter_info DELAY_TIME {
    .name = "Delay Time",
    .units = "seconds",
    .min = 0.001,
    .max = 2.0,
    .default = 0.25,
    .curve = "logarithmic"
}

// Preset compatibility
#preset_version 2
#preset_format binary_compact
#preset_parameters 16  // Number of stored parameters
```

### Code Size Optimization
```impala
// Minimize firmware size
#optimize size
#strip debug_info
#compress_strings
#merge_functions
#remove_unused_code

// Function selection
#ifdef MINIMAL_BUILD
    #exclude advanced_features
    #exclude debug_functions
    #exclude profiling_code
#endif

// Dead code elimination
#mark_entry_points process(), operate1(), operate2()
#eliminate_unreachable_code
#inline_single_use_functions
```

## Build System Integration

### Makefile Integration
```make
# Build configuration variables
CONFIG ?= release
OPTIMIZE ?= speed
DEBUG ?= 0

# Compilation flags based on configuration
ifeq ($(CONFIG),debug)
    IMPALA_FLAGS += -DDEBUG=1 -optimize debug
else
    IMPALA_FLAGS += -optimize $(OPTIMIZE)
endif

# Build targets
firmware.gazl: firmware.imp
    impala-compile $(IMPALA_FLAGS) -o $@ $<

debug: CONFIG=debug
debug: firmware.gazl

release: CONFIG=release
release: firmware.gazl

profile: CONFIG=profile
profile: firmware.gazl
```

### Automated Testing
```impala
// Test build configuration
#ifdef UNIT_TEST_BUILD
    #include "test_framework.imp"
    #enable test_instrumentation
    #main test_main  // Use test main instead of firmware main
#endif

// Test-specific builds
#test_configuration basic_tests {
    #optimize debug
    #enable assert
    #enable bounds_check
    #include_tests "basic_functionality"
}

#test_configuration performance_tests {
    #optimize speed
    #enable profiling
    #include_tests "performance_benchmarks"
}
```

## Build Examples

### Complete Project Build Configuration
```impala
// MyDelay.imp - Complete build setup
#project "Professional Delay"
#version "2.1.0"
#author "Audio Developer"

// Build configuration
#ifdef DEBUG
    #configuration debug
    #optimize debug
    #enable assert
    #enable bounds_check
    #debug_symbols full
#else
    #configuration release
    #optimize speed
    #enable loop_unroll
    #debug_symbols minimal
#endif

// Target hardware
#target permut8_v2
#sample_rate 48000
#buffer_size 128

// Memory allocation
#heap_size 8192
#delay_memory 32768

// Features
#enable fast_math
#enable loop_vectorize
#float_precision single

// Project-specific optimization
#hot_path
void process() {
    // Main audio processing
    processDelay();
    processModulation();
    updateLEDs();
}

// Build validation
#static_assert(DELAY_MEMORY >= 32768, "Insufficient delay memory")
#check_timing_budget()

// Firmware info
#firmware_info {
    .name = "Professional Delay v2.1",
    .build_config = __CONFIG__,
    .optimization = __OPTIMIZE_LEVEL__
}
```

## Key Benefits

**Performance Control**: Fine-tune compilation for optimal speed, size, or debugging capability based on deployment needs.

**Memory Management**: Precise control over memory allocation and layout for efficient resource utilization.

**Build Automation**: Integration with standard build systems and automated testing frameworks.

**Quality Assurance**: Comprehensive validation and error checking to prevent runtime issues.

**Deployment Ready**: Professional firmware packaging with metadata and compatibility information.

Use these build directives to create optimized, reliable firmware that meets specific performance requirements and deployment constraints while maintaining development productivity.
