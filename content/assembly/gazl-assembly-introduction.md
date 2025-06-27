# GAZL Assembly Language Introduction

## Overview

GAZL (GPU Assembly-like Language) is the virtual machine language used by the Permut8 platform for ultimate performance optimization. While Impala provides high-level firmware development capabilities, GAZL is the compiled output that runs on the Permut8 virtual machine for direct hardware control in time-critical audio processing where every CPU cycle matters.

**Key Concept**: GAZL is a **virtual machine language**, not native ARM64 assembly. Impala compiles to GAZL, which then executes on the Permut8 virtual machine.

This introduction covers GAZL language fundamentals, preparing you for advanced GAZL understanding and Impala-GAZL integration patterns.

## Understanding the Impala-GAZL Architecture

### Development Model
Impala serves as the high-level language that compiles to GAZL virtual machine code:

```
Impala Source Code (.impala)
        ↓ [Impala Compiler]
GAZL Virtual Machine Code (.gazl)
        ↓ [Permut8 Virtual Machine]
Audio Processing on Hardware
```

### When to Study GAZL
Direct GAZL knowledge becomes essential when:

**Performance Analysis**: Understanding compiled output for optimization
**Advanced Debugging**: Examining virtual machine execution for complex issues
**Low-Level Integration**: Creating advanced Impala-GAZL interaction patterns
**Optimization Verification**: Confirming that Impala optimizations produce efficient GAZL

### Development Context
GAZL understanding complements Impala development:

```impala

const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


function process_samples() {
    int i;
    for (i = 0 to BUFFER_SIZE - 1) {
        global signal[i] = complex_dsp_algorithm(global signal[i]);
    }
}

```

Compiles to GAZL virtual machine code:
```gazl
process_samples:    FUNC
                    PARA *1
        $i:         LOCi
        .loop:      PEEK %0 &signal:$i
                    CALL ^complex_dsp_algorithm %1 *1
                    POKE &signal:$i %1
                    ADDi $i $i #1
                    LEQi $i #BUFFER_SIZE @.loop
                    RETU
```

## GAZL Virtual Machine Architecture

### Execution Model
GAZL operates as a stack-based virtual machine with audio-specific optimizations:

**Register Model**: Virtual registers (%0, %1, %2...) for temporary values
**Memory Model**: Global/local allocation with direct addressing
**Instruction Set**: Virtual machine instructions optimized for audio processing
**Function Calling**: Stack-based parameter passing with local variable support

### Core GAZL Data Types
**Integer (i)**: 32-bit signed integers for audio samples and parameters
**Pointer (p)**: Memory addresses for arrays and data structures
**Float (f)**: Floating-point values for precise calculations (when supported)

### Memory Architecture
```gazl
; Global memory allocation
global_var:     GLOB *1         ; Allocate 1 global integer
global_array:   GLOB *256       ; Allocate 256-element global array

; Constant data
CONST_TABLE:    CNST *16        ; Constant table with 16 elements
                DATA #100 #200 #300 #400  ; Initialize with values

; Local variables (within functions)
function_name:  FUNC
                PARA *2         ; Function takes 2 parameters
    $local_var: LOCi           ; Local integer variable
    $local_arr: LOCA *8        ; Local array with 8 elements
```

## GAZL Syntax Fundamentals

### Basic Instruction Format
GAZL follows virtual machine instruction syntax:

```gazl
; Basic instruction format
INSTRUCTION destination, source1, source2

; Examples
MOVi %0 #255            ; %0 = 255 (move immediate to register)
ADDi %0 %1 %2           ; %0 = %1 + %2 (add registers)
PEEK %0 &global_var     ; %0 = global_var (load from memory)
POKE &global_var %0     ; global_var = %0 (store to memory)
```

### Virtual Registers
```gazl
; Virtual registers for temporary computation
%0, %1, %2, %3...       ; Temporary registers (managed by VM)

; Local variables (persistent within function)
$variable_name          ; Named local variable
$array_name             ; Named local array

; Memory references
&global_name            ; Reference to global variable/array
&global_array:index     ; Reference to array element
```

### Core GAZL Instructions

#### Memory Operations
```gazl
; Load from memory
PEEK %0 &global_var     ; Load global variable
PEEK %0 &array:5        ; Load array[5]
PEEK %0 $local_var      ; Load local variable

; Store to memory
POKE &global_var %0     ; Store to global variable
POKE &array:5 %0        ; Store to array[5] 
POKE $local_var %0      ; Store to local variable
```

#### Arithmetic Operations
```gazl
; Integer arithmetic
ADDi %0 %1 %2           ; %0 = %1 + %2
SUBi %0 %1 %2           ; %0 = %1 - %2
MULi %0 %1 %2           ; %0 = %1 * %2
DIVi %0 %1 %2           ; %0 = %1 / %2
MODi %0 %1 %2           ; %0 = %1 % %2

; Bitwise operations
SHLi %0 %1 #4           ; %0 = %1 << 4 (shift left)
SHRi %0 %1 #4           ; %0 = %1 >> 4 (shift right)
IORi %0 %1 %2           ; %0 = %1 | %2 (bitwise OR)
XORi %0 %1 %2           ; %0 = %1 ^ %2 (bitwise XOR)
ANDi %0 %1 %2           ; %0 = %1 & %2 (bitwise AND)
```

#### Control Flow
```gazl
; Conditional branches
EQUi %0 #0 @.label      ; if (%0 == 0) goto .label
NEQi %0 #0 @.label      ; if (%0 != 0) goto .label
GRTi %0 %1 @.label      ; if (%0 > %1) goto .label
LEQi %0 %1 @.label      ; if (%0 <= %1) goto .label

; Unconditional jump
GOTO @.label            ; goto .label

; Function calls
CALL ^function_name %0 *2   ; Call function with 2 parameters
RETU                    ; Return from function
```

## Audio-Specific GAZL Patterns

### Sample Processing
```gazl
; Audio sample processing example
process_audio:  FUNC
                PARA *0
    $sample:    LOCi
    $processed: LOCi
    
    ; Load audio sample
    PEEK $sample &signal:0      ; Load left channel
    
    ; Apply gain (multiply by 120, divide by 128)
    MULi %0 $sample #120
    SHRi $processed %0 #7       ; Divide by 128 (>> 7)
    
    ; Clamp to audio range (-2047 to 2047)
    GRTi $processed #2047 @.clamp_high
    LEQi $processed #-2047 @.clamp_low
    GOTO @.store_result
    
.clamp_high:
    MOVi $processed #2047
    GOTO @.store_result
    
.clamp_low:
    MOVi $processed #-2047
    
.store_result:
    ; Store processed sample
    POKE &signal:0 $processed
    RETU
```

### Parameter Handling
```gazl
; Parameter processing example
update_parameters: FUNC
                   PARA *1
    $param_val:    LOCi
    $scaled_val:   LOCi
    
    ; Read parameter (0-255 range)
    PEEK $param_val &params:0
    
    ; Scale to useful range (multiply by 80)
    MULi $scaled_val $param_val #80
    
    ; Store for use in processing (requires filter_cutoff global)
    POKE &filter_cutoff $scaled_val
    RETU
```

### Array Operations
```gazl
; Array processing example
clear_buffer:   FUNC
                PARA *1
    $i:         LOCi
    $size:      LOCi
    
    ; Initialize loop
    MOVi $i #0
    MOVi $size #256
    
.loop:
    ; Clear array element
    POKE &audio_buffer:$i #0
    
    ; Increment and check loop condition
    ADDi $i $i #1
    LEQi $i $size @.loop
    
    RETU
```

## Function Structure and Calling Conventions

### Function Declaration
```gazl
; Function with parameters and local variables
my_function:    FUNC
                PARA *2         ; Takes 2 parameters
    $param1:    INPi           ; First parameter (input)
    $param2:    INPi           ; Second parameter (input)
    $result:    OUTi           ; Return value (output)
    $temp:      LOCi           ; Local temporary variable
    
    ; Function body
    ADDi $result $param1 $param2
    RETU
```

### Variable Types
```gazl
; Parameter and variable declarations
$input_var:     INPi           ; Input parameter (integer)
$output_var:    OUTi           ; Output parameter/return value
$local_var:     LOCi           ; Local variable (integer)
$local_array:   LOCA *16       ; Local array (16 elements)
$pointer_var:   INPp           ; Pointer parameter
```

## Integration with Impala

### How Impala Becomes GAZL
```impala

function addNumbers(a, b) returns int result {
    result = a + b;
}
```

Compiles to:
```gazl
addNumbers:     FUNC
                PARA *2
    $a:         INPi
    $b:         INPi
    $result:    OUTi
    
    ADDi $result $a $b
    RETU
```

### Global Variable Mapping
```impala

global array signal[2]
global array params[PARAM_COUNT]
global int my_variable = 100
```

Becomes GAZL:
```gazl
signal:         GLOB *2
params:         GLOB *8
my_variable:    GLOB *1
                DATi #100
```

## Practical GAZL Analysis

### Reading Compiled Output
When debugging or optimizing, you can examine the compiled GAZL to understand:

1. **Performance Characteristics**: Count instructions in critical loops
2. **Memory Access Patterns**: Identify PEEK/POKE frequency
3. **Function Call Overhead**: Analyze CALL/RETU patterns
4. **Optimization Opportunities**: Spot redundant operations

### Common Optimization Patterns
```gazl
; Efficient loop with minimal branches
efficient_loop: FUNC
                PARA *1
    $i:         LOCi
    $count:     LOCi
    
    PEEK $count &buffer_size
    MOVi $i #0
    
.loop:
    ; Process element at index $i
    PEEK %0 &input_buffer:$i
    MULi %0 %0 #120
    SHRi %0 %0 #7
    POKE &output_buffer:$i %0
    
    ; Efficient loop continuation
    ADDi $i $i #1
    LEQi $i $count @.loop
    
    RETU
```

## Best Practices for GAZL Understanding

### When to Examine GAZL Output
1. **Performance Debugging**: When Impala code isn't performing as expected
2. **Optimization Verification**: To confirm compiler optimizations are working
3. **Complex Algorithms**: For algorithms where every instruction matters
4. **Integration Issues**: When debugging Impala-GAZL boundary problems

### Reading GAZL Effectively
1. **Focus on Critical Paths**: Examine inner loops and frequently called functions
2. **Understand Memory Patterns**: Track PEEK/POKE operations for cache efficiency
3. **Count Instructions**: Estimate execution cost of different approaches
4. **Identify Bottlenecks**: Look for instruction sequences that could be optimized

## Conclusion

Understanding GAZL provides insight into the virtual machine that executes your Impala firmware. While you typically develop in Impala, GAZL knowledge enables advanced debugging, performance analysis, and optimization verification.

The virtual machine architecture of GAZL, with its stack-based execution model and audio-optimized instruction set, provides the foundation for efficient real-time audio processing on the Permut8 platform.

**Next Steps**: With GAZL fundamentals understood, explore [GAZL Debugging and Profiling](gazl-debugging-profiling.md) for advanced analysis techniques, and [GAZL Optimization](gazl-optimization.md) for performance optimization strategies.