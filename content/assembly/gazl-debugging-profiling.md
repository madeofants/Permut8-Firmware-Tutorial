# GAZL Debugging and Performance Profiling

## Overview

Master professional debugging workflows and performance analysis for GAZL virtual machine development on the Permut8 platform. This comprehensive guide covers debugging techniques and systematic performance profiling specifically designed for GAZL virtual machine code compiled from Impala.

GAZL operates as a virtual machine with its own instruction set, execution model, and debugging infrastructure. Understanding these VM-specific characteristics is essential for effective debugging and optimization.

## What You'll Learn

By the end of this guide, you'll master:
- GAZL virtual machine debugging techniques
- Trace-based debugging and analysis methods  
- Memory debugging for VM environments
- Virtual machine performance profiling methodologies
- GAZL instruction timing and optimization analysis
- Integration debugging between Impala and GAZL
- Real-time debugging for audio applications
- Data-driven optimization decision making

**Prerequisites**: 
- [GAZL Assembly Introduction](gazl-assembly-introduction.md)
- Understanding of virtual machine concepts
- Basic Impala programming knowledge

**Time Required**: 2-3 hours  
**Difficulty**: Advanced

---

## Part I: GAZL Virtual Machine Debugging

### Chapter 1: GAZL VM Debug Architecture

#### Permut8 Debug Infrastructure

The Permut8 platform provides VM-specific debugging support tailored for GAZL virtual machine execution:

**Key Debugging Features**:
- **Trace-based debugging**: Monitor VM instruction execution
- **State inspection**: Examine virtual registers and memory
- **Breakpoint support**: Pause execution at specific VM instructions
- **Memory watch**: Monitor global and local variable changes
- **Call stack analysis**: Track function calls through the VM

#### Debug Information in GAZL

GAZL includes debug metadata that maps virtual machine instructions back to Impala source:

```gazl
; Function with debug information
process_audio:  FUNC
                PARA *2
    $input:     INPp        ; Debug: input audio buffer
    $output:    OUTp        ; Debug: output audio buffer
    $sample:    LOCi        ; Debug: current sample being processed
    $temp:      LOCi        ; Debug: temporary calculation storage
    
    ; Debug trace point
    PEEK $sample $input     ; Load sample from input buffer
    
    ; Processing with debug context
    MULi %0 $sample #120    ; Apply gain (debug: gain=120/128)
    SHRi $temp %0 #7        ; Normalize (debug: divide by 128)
    
    ; Range checking for debug
    GRTi $temp #2047 @.clamp_high
    LEQi $temp #-2047 @.clamp_low
    GOTO @.store_result
    
.clamp_high:
    MOVi $temp #2047        ; Debug: clamped to maximum
    GOTO @.store_result
    
.clamp_low:
    MOVi $temp #-2047       ; Debug: clamped to minimum
    
.store_result:
    POKE $output $temp      ; Store processed sample
    RETU
```

### Chapter 2: Trace-Based Debugging

#### GAZL Trace System

The primary debugging mechanism for GAZL is the built-in trace system:

```impala

function enableDebugTracing() {
    if (DEBUG) {
        trace("Debug mode enabled");
        trace("Starting audio processing");
    }
}

function debugProcessingSample(sample) {
    if (DEBUG) {
        trace("Processing sample: ");
        trace(intToString(sample, 10, 1, tempBuffer));
    }
}
```

Compiled GAZL includes trace calls:

```gazl
; Compiled with debug tracing
debug_processing:   FUNC
                    PARA *1
    $sample:        INPi
    $buffer:        LOCA *32
    
    ; Debug trace
    EQUi #DEBUG #0 @.no_debug
    MOVp %1 &.s_processing_sample
    CALL ^trace %0 *2
    
    ; Convert sample to string for tracing
    MOVi %1 $sample
    MOVi %2 #10
    MOVi %3 #1
    ADRL %4 $buffer *0
    CALL &intToString %0 *5
    CALL ^trace %0 *2
    
.no_debug:
    ; Continue processing...
    RETU
```

#### Dynamic Trace Analysis

Monitor GAZL execution through systematic trace analysis:

```impala

function traceAudioProcessingState() {
    if (DEBUG) {
        trace("=== Audio Processing State ===");
        

        trace("Operator 1: ");
        trace(intToString(global params[OPERATOR_1_PARAM_INDEX], 10, 1, buffer));
        
        trace("Operand 1 High: ");
        trace(intToString(global params[OPERAND_1_HIGH_PARAM_INDEX], 10, 1, buffer));
        
        trace("Current clock: ");
        trace(intToString(global clock, 16, 4, buffer));
        

        trace("Left signal: ");
        trace(intToString(global signal[0], 10, 1, buffer));
        
        trace("Right signal: ");
        trace(intToString(global signal[1], 10, 1, buffer));
        
        trace("=== End State ===");
    }
}
```

### Chapter 3: Memory Debugging for GAZL VM

#### Global Variable Monitoring

Track changes to global variables through the VM execution:

```gazl
; Memory debugging with validation
safe_global_write:  FUNC
                    PARA *2
    $address:       INPp
    $value:         INPi
    $old_value:     LOCi
    
    ; Debug: Read current value
    EQUi #DEBUG #0 @.no_debug
    PEEK $old_value $address
    
    ; Trace the change
    MOVp %1 &.s_memory_write
    CALL ^trace %0 *2
    
    ; Trace old value
    MOVp %1 &.s_old_value
    CALL ^trace %0 *2
    MOVi %1 $old_value
    CALL &traceInt %0 *2
    
    ; Trace new value
    MOVp %1 &.s_new_value
    CALL ^trace %0 *2
    MOVi %1 $value
    CALL &traceInt %0 *2
    
.no_debug:
    ; Perform the actual write
    POKE $address $value
    RETU
```

#### Array Bounds Checking

Implement runtime bounds checking for GAZL arrays:

```gazl
; Safe array access with bounds checking
safe_array_read:    FUNC
                    PARA *3
    $array:         INPp
    $index:         INPi
    $size:          INPi
    $result:        OUTi
    
    ; Debug bounds check
    EQUi #DEBUG #0 @.no_bounds_check
    
    ; Check lower bound
    GEQi $index #0 @.check_upper
    MOVp %1 &.s_array_underflow
    CALL ^trace %0 *2
    CALL ^abort %0 *1
    
.check_upper:
    ; Check upper bound
    LEQi $index $size @.bounds_ok
    MOVp %1 &.s_array_overflow
    CALL ^trace %0 *2
    CALL ^abort %0 *1
    
.bounds_ok:
.no_bounds_check:
    ; Safe to access array
    PEEK $result $array:$index
    RETU
```

### Chapter 4: Integration Debugging

#### Cross-Language Debug Workflows

Debug seamlessly across Impala-GAZL boundaries with coordinated tracing:

```impala

function debugAudioProcessing() {
    if (DEBUG) {
        trace("=== Impala: Starting Audio Processing ===");
        traceInts("Input parameters: ", PARAM_COUNT, global params);
        trace("Calling GAZL process function...");
    }
    

    process();
    
    if (DEBUG) {
        trace("=== Impala: Audio Processing Complete ===");
        traceInts("Output signal: ", 2, global signal);
    }
}
```

```gazl
; GAZL side debug integration
process:        FUNC
                PARA *1
    $i:         LOCi
    
    ; Debug entry
    EQUi #DEBUG #0 @.no_debug_entry
    MOVp %1 &.s_gazl_process_entry
    CALL ^trace %0 *2
    
.no_debug_entry:
    ; Main processing loop
    MOVi $i #0
    
.loop:
    ; Debug loop iteration
    EQUi #DEBUG #0 @.no_debug_loop
    MOVp %1 &.s_processing_iteration
    CALL ^trace %0 *2
    MOVi %1 $i
    CALL &traceInt %0 *2
    
.no_debug_loop:
    ; Process current sample
    PEEK %0 &signal:0
    MULi %0 %0 #120
    SHRi %0 %0 #7
    POKE &signal:0 %0
    
    ; Continue loop
    ADDi $i $i #1
    LEQi $i #BUFFER_SIZE @.loop
    
    ; Debug exit
    EQUi #DEBUG #0 @.no_debug_exit
    MOVp %1 &.s_gazl_process_exit
    CALL ^trace %0 *2
    
.no_debug_exit:
    CALL ^yield %0 *1
    RETU
```

---

## Part II: GAZL VM Performance Profiling

### Chapter 5: Virtual Machine Performance Analysis

#### Understanding GAZL VM Performance

GAZL virtual machine performance differs significantly from native assembly performance. Key factors include:

**Instruction Execution**: Virtual machine instructions have different costs than native instructions
**Memory Access Patterns**: VM memory model affects access performance
**Function Call Overhead**: VM function calls have specific overhead characteristics
**Register Allocation**: Virtual register usage impacts performance

#### VM Instruction Timing Analysis

Profile the actual cost of GAZL instructions:

```gazl
; Performance measurement framework
measure_instruction_timing:  FUNC
                            PARA *0
    $iterations:            LOCi
    $start_time:            LOCi
    $end_time:              LOCi
    $i:                     LOCi
    
    ; Get start timestamp
    CALL ^getClock %0 *1
    MOVi $start_time %0
    
    ; Test loop
    MOVi $i #0
.test_loop:
    ; INSTRUCTION UNDER TEST
    MULi %0 %1 %2           ; Example: multiplication instruction
    
    ; Loop control
    ADDi $i $i #1
    LEQi $i $iterations @.test_loop
    
    ; Get end timestamp
    CALL ^getClock %0 *1
    MOVi $end_time %0
    
    ; Calculate duration
    SUBi %0 $end_time $start_time
    
    ; Trace result
    MOVp %1 &.s_instruction_timing
    CALL ^trace %0 *2
    CALL &traceInt %0 *2
    
    RETU
```

### Chapter 6: Memory Performance Profiling

#### Global vs Local Variable Access

Compare performance characteristics of different memory access patterns:

```gazl
; Memory access performance test
test_memory_performance:    FUNC
                           PARA *0
    $iterations:           LOCi
    $i:                    LOCi
    $local_var:            LOCi
    $start_time:           LOCi
    $end_time:             LOCi
    
    ; Test global variable access
    CALL ^getClock %0 *1
    MOVi $start_time %0
    
    MOVi $i #0
.global_test_loop:
    PEEK %0 &global_test_var
    ADDi %0 %0 #1
    POKE &global_test_var %0
    
    ADDi $i $i #1
    LEQi $i $iterations @.global_test_loop
    
    CALL ^getClock %0 *1
    MOVi $end_time %0
    SUBi %0 $end_time $start_time
    
    MOVp %1 &.s_global_access_time
    CALL ^trace %0 *2
    CALL &traceInt %0 *2
    
    ; Test local variable access
    CALL ^getClock %0 *1
    MOVi $start_time %0
    
    MOVi $i #0
.local_test_loop:
    ADDi $local_var $local_var #1
    
    ADDi $i $i #1
    LEQi $i $iterations @.local_test_loop
    
    CALL ^getClock %0 *1
    MOVi $end_time %0
    SUBi %0 $end_time $start_time
    
    MOVp %1 &.s_local_access_time
    CALL ^trace %0 *2
    CALL &traceInt %0 *2
    
    RETU
```

### Chapter 7: Function Call Profiling

#### Analyzing GAZL Function Call Overhead

Measure the cost of function calls in the GAZL virtual machine:

```gazl
; Function call overhead measurement
measure_call_overhead:      FUNC
                           PARA *0
    $iterations:           LOCi
    $i:                    LOCi
    $start_time:           LOCi
    $end_time:             LOCi
    
    ; Measure direct operations
    CALL ^getClock %0 *1
    MOVi $start_time %0
    
    MOVi $i #0
.direct_loop:
    ; Direct operation
    MULi %0 %1 %2
    ADDi %0 %0 #1
    
    ADDi $i $i #1
    LEQi $i $iterations @.direct_loop
    
    CALL ^getClock %0 *1
    MOVi $end_time %0
    SUBi %0 $end_time $start_time
    
    MOVp %1 &.s_direct_time
    CALL ^trace %0 *2
    CALL &traceInt %0 *2
    
    ; Measure function call operations
    CALL ^getClock %0 *1
    MOVi $start_time %0
    
    MOVi $i #0
.call_loop:
    ; Function call for same operation
    MOVi %1 %1
    MOVi %2 %2
    CALL &simple_multiply %0 *3
    
    ADDi $i $i #1
    LEQi $i $iterations @.call_loop
    
    CALL ^getClock %0 *1
    MOVi $end_time %0
    SUBi %0 $end_time $start_time
    
    MOVp %1 &.s_call_time
    CALL ^trace %0 *2
    CALL &traceInt %0 *2
    
    RETU

; Simple function for overhead testing
simple_multiply:            FUNC
                           PARA *2
    $a:                    INPi
    $b:                    INPi
    $result:               OUTi
    
    MULi $result $a $b
    ADDi $result $result #1
    RETU
```

---

## Chapter 8: Real-Time Performance Monitoring

### Non-Intrusive Profiling

For real-time audio applications, profiling must not disrupt timing:

```gazl
; Lightweight performance monitoring
audio_process_monitored:    FUNC
                           PARA *0
    $sample_count:         LOCi
    $start_time:           LOCi
    $process_time:         LOCi
    
    ; Quick timestamp (low overhead)
    CALL ^getClock %0 *1
    MOVi $start_time %0
    
    ; Actual audio processing
    CALL &core_audio_algorithm %0 *1
    
    ; Calculate processing time
    CALL ^getClock %0 *1
    SUBi $process_time %0 $start_time
    
    ; Check against real-time deadline
    GRTi $process_time #MAX_PROCESS_TIME @.timing_violation
    GOTO @.timing_ok
    
.timing_violation:
    ; Log timing violation (only if debug enabled)
    EQUi #DEBUG #0 @.timing_ok
    MOVp %1 &.s_timing_violation
    CALL ^trace %0 *2
    MOVi %1 $process_time
    CALL &traceInt %0 *2
    
.timing_ok:
    RETU
```

### Statistical Performance Analysis

Collect performance data over time for analysis:

```gazl
; Performance statistics collection
collect_performance_stats:  FUNC
                           PARA *1
    $current_time:         INPi
    $stats_index:          LOCi
    
    ; Get current statistics index
    PEEK $stats_index &perf_stats_index
    
    ; Store timing data
    POKE &perf_stats_buffer:$stats_index $current_time
    
    ; Update index (circular buffer)
    ADDi $stats_index $stats_index #1
    MODi $stats_index $stats_index #STATS_BUFFER_SIZE
    POKE &perf_stats_index $stats_index
    
    ; Periodically analyze statistics
    EQUi $stats_index #0 @.analyze_stats
    GOTO @.no_analysis
    
.analyze_stats:
    CALL &analyze_performance_trends %0 *1
    
.no_analysis:
    RETU
```

---

## Best Practices

### GAZL VM Debugging Best Practices

1. **Use Conditional Compilation**: Only include debug code when DEBUG is defined
2. **Leverage Trace System**: Use the built-in trace() function extensively
3. **Preserve Real-Time Behavior**: Minimize debug overhead in audio processing
4. **Cross-Language Coordination**: Maintain debug state consistency across Impala-GAZL boundaries
5. **Memory Safety**: Implement bounds checking and validation in debug builds

### GAZL VM Profiling Best Practices

1. **VM-Aware Analysis**: Consider virtual machine execution characteristics
2. **Instruction-Level Timing**: Profile individual GAZL instruction costs
3. **Memory Pattern Analysis**: Understand global vs local variable access costs
4. **Function Call Overhead**: Measure and optimize function call patterns
5. **Real-Time Constraints**: Ensure profiling doesn't violate audio timing requirements

### Integration Recommendations

1. **Unified Debug Framework**: Use consistent debug approaches across Impala and GAZL
2. **Performance Baselines**: Establish VM performance baselines for regression detection
3. **Automated Testing**: Integrate debug and performance validation into build process
4. **Documentation**: Maintain performance characteristics documentation for the VM

---

## Conclusion

GAZL virtual machine debugging and profiling requires understanding the unique characteristics of the VM execution environment. Unlike native assembly debugging, GAZL debugging focuses on virtual machine state, instruction execution patterns, and the interaction between Impala source code and compiled GAZL instructions.

The trace-based debugging approach, combined with systematic performance analysis of VM instruction costs, provides the foundation for professional GAZL development. This enables developers to create high-performance, reliable firmware while maintaining real-time audio processing requirements.

**Next Steps**: Apply these debugging and profiling techniques in conjunction with [GAZL Optimization Patterns](gazl-optimization.md) and [Integration Best Practices](gazl-integration-production.md) for comprehensive GAZL virtual machine development mastery.