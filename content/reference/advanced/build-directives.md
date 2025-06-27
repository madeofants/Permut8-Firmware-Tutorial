# Build Directives and Compilation Options

## Overview
Control the Impala-to-GAZL compilation process with build directives, optimization flags, and configuration options to create efficient, debuggable, and deployment-ready firmware.

## Core Build Directives

### Project Configuration
```impala

#project "MyCustomEffect"
#version "1.2.3"
#author "Developer Name"
#description "Custom delay with modulation"


#target permut8_v2
#sample_rate 48000
#buffer_size 128


#heap_size 8192
#stack_size 1024
#delay_memory 16384
```

### Optimization Levels
```impala

#optimize speed





#enable loop_unroll
#enable inline_small
#enable const_fold
#enable dead_code




```

### Debug Configuration
```impala

#ifdef DEBUG
    #enable assert
    #enable bounds_check
    #enable stack_check
    #enable trace
    #debug_symbols full
#else
    #debug_symbols minimal
#endif


#define DEVELOPMENT_BUILD
#define ENABLE_PROFILING
```

## Memory Management Directives

### Buffer Allocation
```impala

#declare_buffer delay_line[16384]
#declare_buffer temp_buffer[512]
#declare_buffer coefficient_table[256]


#enable dynamic_alloc
#max_dynamic_size 4096


#align_buffers 16
#pack_structs
#cache_line_size 64
```

### Memory Safety
```impala

#enable buffer_overflow_check
#enable null_pointer_check
#enable memory_leak_check


#warn unused_variables
#warn uninitialized_access
#error buffer_overrun
```

## Performance Optimization

### Instruction Set Control
```impala

#cpu_features baseline





#float_precision single




#fast_math reciprocal
#fast_math sqrt
#fast_math trigonometric
```

### Loop Optimization
```impala

#pragma loop_vectorize enable
#pragma loop_unroll count(4)
#pragma loop_pipeline enable


void optimizedProcessing() {
    #pragma loop_vectorize_width(4)
    for (int i = 0; i < BUFFER_SIZE; i += 4) {

        signal[i]   = applyEffect(signal[i]);
        signal[i+1] = applyEffect(signal[i+1]);
        signal[i+2] = applyEffect(signal[i+2]);
        signal[i+3] = applyEffect(signal[i+3]);
    }
}
```

### Function Optimization
```impala

#inline always
float criticalFunction(float input) {

    return input * 0.5 + 0.25;
}

#inline never
void debugPrintFunction(float value) {

    printf("Debug: %f\n", value);
}


#hot_path
void audioProcessingLoop() {


}

#cold_path
void errorHandling() {


}
```

## Build Configurations

### Release Configuration
```impala

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


#strip unused_functions
#compress_constants
#merge_identical_functions
```

### Debug Configuration
```impala

#configuration debug

#optimize debug
#disable loop_unroll
#disable inline_small

#enable assert
#enable bounds_check
#enable stack_check
#enable trace
#debug_symbols full


#enable memory_profiler
#enable performance_counters
#output_assembly_listing
```

### Profiling Configuration
```impala

#configuration profile

#optimize balanced
#enable inline_small
#disable loop_unroll


#enable cycle_counting
#enable function_timing
#enable memory_tracking
#profile_output "performance_data.json"


#instrument_branches
#instrument_memory_access
#instrument_function_calls
```

## Advanced Build Features

### Conditional Compilation
```impala

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


#if VERSION >= 2.0

    void newFeature() { /* implementation */ }
#endif
```

### Custom Compilation Stages
```impala

#preprocess
    generate_coefficient_tables();
    validate_memory_layout();
    optimize_parameter_mapping();
#end_preprocess


#postprocess
    verify_timing_constraints();
    check_memory_usage();
    validate_audio_range();
#end_postprocess


#generate_lookup_table sin_table 256 sin(x * 2 * PI / 256)
#generate_lookup_table exp_table 128 exp(-x / 128.0)
```

### Platform-Specific Builds
```impala

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


#if HAS_EXTERNAL_MEMORY
    #enable large_buffers
    #max_delay_time 10.0
#else
    #max_delay_time 2.0
#endif
```

## Error Handling and Validation

### Compile-Time Checks
```impala

#static_assert(BUFFER_SIZE % 4 == 0, "Buffer size must be multiple of 4")
#static_assert(MAX_DELAY_TIME < 60.0, "Delay time too large for memory")
#static_assert(sizeof(AudioSample) == 4, "Unexpected sample size")


#check_memory_usage()
#check_timing_budget()
#check_parameter_ranges()


#require_feature floating_point
#require_memory_size 32768
#require_cpu_speed 100MHz
```

### Build Warnings and Errors
```impala

#warning "Using experimental feature in build"
#error "Missing required configuration option"
#deprecated "This function will be removed in v3.0"


#warn_if_slow(function_name, 1000)
#warn_if_large(buffer_name, 8192)
#warn_if_recursive(function_name)
```

## Deployment and Distribution

### Firmware Packaging
```impala

#firmware_info {
    .name = "Custom Delay v1.2",
    .author = "Developer Name",
    .version = {1, 2, 0},
    .build_date = __BUILD_DATE__,
    .checksum = __FIRMWARE_CHECKSUM__
}


#parameter_info DELAY_TIME {
    .name = "Delay Time",
    .units = "seconds",
    .min = 0.001,
    .max = 2.0,
    .default = 0.25,
    .curve = "logarithmic"
}


#preset_version 2
#preset_format binary_compact
#preset_parameters 16
```

### Code Size Optimization
```impala

#optimize size
#strip debug_info
#compress_strings
#merge_functions
#remove_unused_code


#ifdef MINIMAL_BUILD
    #exclude advanced_features
    #exclude debug_functions
    #exclude profiling_code
#endif


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

#ifdef UNIT_TEST_BUILD
    #include "test_framework.imp"
    #enable test_instrumentation
    #main test_main
#endif


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

#project "Professional Delay"
#version "2.1.0"
#author "Audio Developer"


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


#target permut8_v2
#sample_rate 48000
#buffer_size 128


#heap_size 8192
#delay_memory 32768


#enable fast_math
#enable loop_vectorize
#float_precision single


#hot_path
void process() {

    processDelay();
    processModulation();
    updateLEDs();
}


#static_assert(DELAY_MEMORY >= 32768, "Insufficient delay memory")
#check_timing_budget()


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
