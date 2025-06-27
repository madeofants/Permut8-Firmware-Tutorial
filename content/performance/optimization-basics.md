# Optimization Basics: The 80/20 Guide for Permut8 Performance

## Overview

When developing firmware for Permut8, understanding optimization principles can mean the difference between smooth real-time performance and audio dropouts. This guide focuses on the 80/20 rule: the 20% of optimization techniques that deliver 80% of the performance gains.

Permut8's constrained environment demands efficient code, but premature optimization can waste development time. This guide helps you identify where to focus your optimization efforts for maximum impact.

## The Optimization Mindset

### Performance First, Optimization Second

The most important optimization principle: **write correct code first, then optimize**. Permut8's real-time constraints are strict, but buggy optimized code is worse than slightly slower correct code.

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


function process() {

    global signal[0] = ((global (int)global params[CLOCK_FREQ_PARAM_INDEX] * 3547) >> 12) + global offset;
}


function process() 
locals int gain
{
    gain = global (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 4;
    global signal[0] = global input * gain + global offset;
}

```

### Measure Before Optimizing

Permut8 provides timing information through the development environment. Always profile your code to identify actual bottlenecks rather than assumed ones.

**Key Performance Indicators:**
- **CPU Usage**: Target <80% for stable real-time performance
- **Memory Usage**: Stay within allocated buffers
- **Timing Consistency**: Avoid irregular processing spikes

### The 80/20 Optimization Hierarchy

Focus optimization efforts in this order:

1. **Algorithm Choice** (80% impact) - Choose efficient algorithms
2. **Memory Access Patterns** (15% impact) - Optimize data flow
3. **Arithmetic Optimization** (4% impact) - Efficient math operations
4. **Micro-optimizations** (1% impact) - Assembly tweaks

## Algorithm-Level Optimization (80% Impact)

### Choose the Right Algorithm

The algorithm you choose has more performance impact than any other optimization. For Permut8's real-time constraints, algorithmic efficiency is paramount.

**Example: Filter Design Choices**

```impala

function convolution_reverb(input) returns int
locals int output, int i
{
    output = 0;
    for (i = 0 to global impulse_length - 1) {
        output = output + (global input_buffer[i] * global impulse_response[i] >> 8);
    }
    return output;
}


function iir_filter(input) returns int
locals int output
{
    output = (global a0 * input + global a1 * global x1 + global a2 * global x2 
              - global b1 * global y1 - global b2 * global y2) >> 8;
    global x2 = global x1; 
    global x1 = input;
    global y2 = global y1; 
    global y1 = output;
    return output;
}
```

### Algorithmic Complexity Considerations

For real-time audio, prefer algorithms with:
- **O(1)** constant time - Perfect for real-time
- **O(log n)** logarithmic time - Usually acceptable
- **O(n)** linear time - Use carefully, minimize n
- **O(n²)** quadratic time - Avoid in real-time processing

### Approximate vs. Exact Algorithms

Often, approximate algorithms provide sufficient quality with much better performance:

```impala

function precise_sine(phase) returns int
{

    return sine(phase * 6283 >> 10);
}


function fast_sine(phase) returns int
locals int table_index, int fraction, int current, int next
{
    table_index = (phase * SINE_TABLE_SIZE) >> 16;
    fraction = ((phase * SINE_TABLE_SIZE) >> 8) & 255;
    current = global SINE_TABLE[table_index];
    next = global SINE_TABLE[(table_index + 1) % SINE_TABLE_SIZE];
    return current + ((next - current) * fraction >> 8);
}
```

## Memory Access Optimization (15% Impact)

### Sequential Access Patterns

Permut8's memory architecture favors sequential access. Design your data structures and algorithms to access memory sequentially whenever possible.

```impala

function process_scattered()
locals int i, int index
{
    for (i = 0 to BUFFER_SIZE - 1) {
        index = global random_indices[i];
        global signal[i] = process_sample(global input_buffer[index]);
    }
}


function process_sequential()
locals int i
{
    for (i = 0 to BUFFER_SIZE - 1) {
        global signal[i] = process_sample(global input_buffer[i]);
    }
}
```

### Cache-Friendly Data Structures

Organize data to maximize cache efficiency:

```impala


global array delay_buffer[MAX_DELAY]
global int delay_write_pos = 0
global int delay_read_pos = 0
global int delay_feedback = 128



global array delay_buffers[NUM_DELAYS * MAX_DELAY]
global array delay_write_positions[NUM_DELAYS]
global array delay_read_positions[NUM_DELAYS]
global array delay_feedbacks[NUM_DELAYS]


function get_delay_buffer_sample(delay_index, sample_offset) returns int
{
    return global delay_buffers[delay_index * MAX_DELAY + sample_offset];
}
```

### Memory Pool Management

Pre-allocate buffers and reuse them to avoid dynamic allocation:

```impala

global array temp_buffers[4 * BUFFER_SIZE]
global array buffer_usage[4]

function get_temp_buffer() returns int
locals int i
{
    for (i = 0 to 3) {
        if (global buffer_usage[i] == 0) {
            global buffer_usage[i] = 1;
            return i;
        }
    }
    return -1;
}

function return_temp_buffer(index)
{
    if (index >= 0 && index < 4) {
        global buffer_usage[index] = 0;
    }
}


function get_temp_buffer_sample(buffer_index, sample_index) returns int
{
    return global temp_buffers[buffer_index * BUFFER_SIZE + sample_index];
}

function set_temp_buffer_sample(buffer_index, sample_index, value)
{
    global temp_buffers[buffer_index * BUFFER_SIZE + sample_index] = value;
}
```

## Arithmetic Optimization (4% Impact)

### Fixed-Point Arithmetic

For operations that don't require full floating-point precision, fixed-point arithmetic can be significantly faster:

```impala

function apply_gain_fixed(input, gain_q15) returns int
locals int result
{
    result = (input * gain_q15) >> 15;
    return result;
}


function apply_gain_integer(input, gain) returns int
locals int result
{
    result = (input * gain) >> 8;
    return result;
}
```

### Efficient Math Operations

Replace expensive operations with cheaper alternatives where possible:

```impala

function expensive_normalize(value, max) returns int
{
    return value / max;
}


function cheap_normalize(value, max_reciprocal) returns int
{
    return (value * max_reciprocal) >> 16;
}


function power_of_two_divide(value, shift) returns int
{
    return value >> shift;
}
```

### Vector Operations

When processing multiple samples, consider vectorized operations:

```impala

function apply_gain_scalar(buffer_size, gain)
locals int i
{
    for (i = 0 to buffer_size - 1) {
        global audio_buffer[i] = (global audio_buffer[i] * gain) >> 8;
    }
}


function apply_gain_vectorized(buffer_size, gain)
locals int i
{
    i = 0;
    while (i + 4 <= buffer_size) {
        global audio_buffer[i] = (global audio_buffer[i] * gain) >> 8;
        global audio_buffer[i + 1] = (global audio_buffer[i + 1] * gain) >> 8;
        global audio_buffer[i + 2] = (global audio_buffer[i + 2] * gain) >> 8;
        global audio_buffer[i + 3] = (global audio_buffer[i + 3] * gain) >> 8;
        i = i + 4;
    }

    while (i < buffer_size) {
        global audio_buffer[i] = (global audio_buffer[i] * gain) >> 8;
        i = i + 1;
    }
}
```

## Permut8-Specific Optimizations

### Exploit Hardware Features

Permut8's DSP hardware provides specific optimizations you should leverage:

```impala

function optimized_filter(input) returns int
locals int output, int coeff
{
    coeff = global filter_coefficient;

    output = (input * coeff) >> 8;
    return output;
}
```

### Parameter Update Optimization

Don't recalculate expensive parameter-derived values every sample:

```impala

function process_sample(input) returns int
locals int cutoff_freq, int q, int filter_coeff
{
    cutoff_freq = (global params[CUTOFF] * SAMPLE_RATE) >> 1;
    q = global params[RESONANCE] * 10 + 128;
    filter_coeff = calculate_filter_coeffs(cutoff_freq, q);
    return apply_filter(input, filter_coeff);
}


global int cached_coeff = 0
global array last_(int)global params[OPERATOR_1_PARAM_INDEX]

function process_sample_optimized(input) returns int
locals int cutoff_freq, int q
{
    if (global params[CUTOFF] != global last_(int)global params[CLOCK_FREQ_PARAM_INDEX] || 
        global params[RESONANCE] != global last_(int)global params[SWITCHES_PARAM_INDEX]) {
        cutoff_freq = (global params[CUTOFF] * SAMPLE_RATE) >> 1;
        q = global params[RESONANCE] * 10 + 128;
        global cached_coeff = calculate_filter_coeffs(cutoff_freq, q);
        global last_(int)global params[CLOCK_FREQ_PARAM_INDEX] = global params[CUTOFF];
        global last_(int)global params[SWITCHES_PARAM_INDEX] = global params[RESONANCE];
    }
    return apply_filter(input, global cached_coeff);
}
```

### Buffer Size Optimization

Choose buffer sizes that work well with Permut8's architecture:

```impala

const int OPTIMAL_BUFFER_SIZE = 64
const int DELAY_BUFFER_SIZE = 1024


function circular_buffer_write(value)
locals int new_pos
{
    global circular_buffer[global write_pos] = value;
    new_pos = (global write_pos + 1) & (DELAY_BUFFER_SIZE - 1);
    global write_pos = new_pos;
}

function circular_buffer_read() returns int
locals int value, int new_pos
{
    value = global circular_buffer[global read_pos];
    new_pos = (global read_pos + 1) & (DELAY_BUFFER_SIZE - 1);
    global read_pos = new_pos;
    return value;
}
```

## Assembly-Level Optimization (1% Impact)

### When to Use Assembly

Reserve assembly optimization for proven bottlenecks that can't be optimized at higher levels:

```gazl
; Example: Optimized inner loop for filter processing
filter_loop:    FUNC
                PARA *0
    $input:     LOCi
    $output:    LOCi
    $i:         LOCi
    
    MOVi $i #0
.loop:
    PEEK $input &input_buffer:$i     ; Load input sample
    MULi %0 $input &coeff_a0         ; Multiply with coefficient
    ADDi $output $output %0          ; Accumulate
    MULi %0 &state1 &coeff_a1        ; Continue MAC operations
    ADDi $output $output %0
    POKE &output_buffer:$i $output   ; Store result
    ADDi $i $i #1                    ; Increment counter
    LEQi $i #BUFFER_SIZE @.loop      ; Loop if not done
    RETU
```

### Assembly Best Practices

1. **Profile First**: Verify the bottleneck before writing assembly
2. **Keep It Simple**: Complex assembly is hard to debug and maintain
3. **Document Thoroughly**: Assembly code needs extensive comments
4. **Test Extensively**: Assembly bugs are particularly nasty

## Performance Measurement and Profiling

### Timing Your Code

Use Permut8's built-in timing facilities to measure performance:

```impala
function benchmark_function()
locals int start_time, int end_time, int cycles_used
{
    start_time = global clock;
    

    expensive_operation();
    
    end_time = global clock;
    cycles_used = end_time - start_time;
    

    if (DEBUG) {
        trace("Function took cycles: ");
        trace(intToString(cycles_used, 10, 1, global debug_buffer));
    }
}
```

### Performance Testing Framework

Create a systematic approach to performance testing:

```impala

global array test_names[8 * 32]
global array test_iterations[8]
global array test_total_cycles[8]
global int current_test_count = 0

function create_performance_test(iterations)
locals int test_index
{
    test_index = global current_test_count;
    global test_iterations[test_index] = iterations;
    global test_total_cycles[test_index] = 0;
    global current_test_count = global current_test_count + 1;
    return test_index;
}

function run_performance_test(test_index)
locals int i, int start_time, int end_time
{
    for (i = 0 to global test_iterations[test_index] - 1) {
        start_time = global clock;
        expensive_operation();
        end_time = global clock;
        global test_total_cycles[test_index] = global test_total_cycles[test_index] + 
                                               (end_time - start_time);
    }
}

function report_performance_test(test_index)
locals int avg_cycles
{
    avg_cycles = global test_total_cycles[test_index] / global test_iterations[test_index];
    if (DEBUG) {
        trace("Test cycles/iteration: ");
        trace(intToString(avg_cycles, 10, 1, global debug_buffer));
    }
}
```

### Memory Usage Monitoring

Track memory usage to prevent overruns:

```impala
function check_memory_usage()
locals int buffer_usage, int param_usage
{

    buffer_usage = global buffer_write_pos;
    param_usage = global param_update_count;
    
    if (buffer_usage > BUFFER_WARNING_THRESHOLD) {
        if (DEBUG) {
            trace("Warning: High buffer usage");
        }
    }
    
    if (param_usage > PARAM_WARNING_THRESHOLD) {
        if (DEBUG) {
            trace("Warning: High parameter update rate");
        }
    }
}
```

## Common Optimization Pitfalls

### Premature Optimization

**Problem**: Optimizing code before identifying actual bottlenecks
**Solution**: Profile first, optimize second

```impala

function premature_optimization()
locals int result, int value
{
    value = global input_sample;

    result = ((value << 3) + (value << 1)) >> 2;
    global output_sample = result;
}


function clear_code()
locals int result, int value
{
    value = global input_sample;
    result = (value * 5) >> 1;
    global output_sample = result;
}
```

### Over-Optimization

**Problem**: Optimizing code that's already fast enough
**Solution**: Focus on actual bottlenecks that impact user experience

### Optimization at Wrong Level

**Problem**: Micro-optimizing when algorithmic changes would be more effective
**Solution**: Follow the 80/20 hierarchy

### Breaking Code Correctness

**Problem**: Introducing bugs through aggressive optimization
**Solution**: Extensive testing of optimized code

```impala

function unsafe_fast_function(input) returns int
locals int index
{

    index = input;
    return global LOOKUP_TABLE[index];
}


function safe_function(input) returns int
locals int index
{

    if (input < 0) {
        index = 0;
    } else if (input >= LOOKUP_TABLE_SIZE) {
        index = LOOKUP_TABLE_SIZE - 1;
    } else {
        index = input;
    }
    return global LOOKUP_TABLE[index];
}
```

## Real-World Optimization Examples

### Example 1: Oscillator Optimization

```impala

global int slow_oscillator_phase = 0
global int slow_oscillator_frequency = 1000

function slow_oscillator_next_sample() returns int
locals int output
{

    output = sine((global slow_oscillator_phase * 6283) >> 16);
    global slow_oscillator_phase = global slow_oscillator_phase + 
                                   (global slow_oscillator_frequency * 65536 / SAMPLE_RATE);
    if (global slow_oscillator_phase >= 65536) {
        global slow_oscillator_phase = global slow_oscillator_phase - 65536;
    }
    return output;
}


global int fast_oscillator_phase_accumulator = 0
global int fast_oscillator_frequency_word = 1000

function fast_oscillator_next_sample() returns int
locals int table_index, int fraction, int current, int next, int result
{
    table_index = global fast_oscillator_phase_accumulator >> (32 - SINE_TABLE_BITS);
    fraction = (global fast_oscillator_phase_accumulator >> (32 - SINE_TABLE_BITS - 8)) & 255;
    
    current = global SINE_TABLE[table_index];
    next = global SINE_TABLE[(table_index + 1) & SINE_TABLE_MASK];
    
    global fast_oscillator_phase_accumulator = global fast_oscillator_phase_accumulator + 
                                                global fast_oscillator_frequency_word;
    
    result = current + ((next - current) * fraction >> 8);
    return result;
}
```

### Example 2: Filter Bank Optimization

```impala

global array filter_states[NUM_FILTERS * 4]
global array filter_coeffs[NUM_FILTERS * 5]

function process_filter_bank_slow(input) returns int
locals int output, int filter, int state_offset, int coeff_offset
{
    output = input;
    for (filter = 0 to NUM_FILTERS - 1) {
        state_offset = filter * 4;
        coeff_offset = filter * 5;
        output = process_single_filter(output, state_offset, coeff_offset);
    }
    return output;
}


function process_filter_bank_fast(input) returns int
locals int y, int x1, int x2, int y1, int y2
{
    y = input;
    

    x1 = global filter_states[1];
    x2 = global filter_states[2];
    y1 = global filter_states[3];
    y2 = global filter_states[4];
    
    y = ((global filter_coeffs[0] * y + global filter_coeffs[1] * x1 + 
          global filter_coeffs[2] * x2 - global filter_coeffs[3] * y1 - 
          global filter_coeffs[4] * y2) >> 8);
          
    global filter_states[2] = x1;
    global filter_states[1] = input;
    global filter_states[4] = y1;
    global filter_states[3] = y;
    

    
    return y;
}

function process_single_filter(input, state_offset, coeff_offset) returns int
locals int output
{
    output = ((global filter_coeffs[coeff_offset] * input + 
               global filter_coeffs[coeff_offset + 1] * global filter_states[state_offset + 1] + 
               global filter_coeffs[coeff_offset + 2] * global filter_states[state_offset + 2] - 
               global filter_coeffs[coeff_offset + 3] * global filter_states[state_offset + 3] - 
               global filter_coeffs[coeff_offset + 4] * global filter_states[state_offset + 4]) >> 8);
    

    global filter_states[state_offset + 2] = global filter_states[state_offset + 1];
    global filter_states[state_offset + 1] = input;
    global filter_states[state_offset + 4] = global filter_states[state_offset + 3];
    global filter_states[state_offset + 3] = output;
    
    return output;
}
```

## Optimization Checklist

### Before You Start
- [ ] Profile your code to identify actual bottlenecks
- [ ] Ensure your code is correct and tested
- [ ] Set performance targets based on real requirements
- [ ] Document current performance baseline

### Algorithm Level (High Impact)
- [ ] Choose appropriate algorithms for real-time constraints
- [ ] Consider approximate algorithms for non-critical calculations
- [ ] Minimize algorithmic complexity in hot paths
- [ ] Cache expensive calculations when possible

### Memory Level (Medium Impact)
- [ ] Optimize memory access patterns for sequential access
- [ ] Align data structures to cache boundaries
- [ ] Use memory pools to avoid dynamic allocation
- [ ] Minimize memory footprint of hot data structures

### Arithmetic Level (Low Impact)
- [ ] Use fixed-point arithmetic where appropriate
- [ ] Replace divisions with multiplications when possible
- [ ] Utilize bit shifts for power-of-2 operations
- [ ] Consider lookup tables for expensive functions

### Assembly Level (Very Low Impact)
- [ ] Only optimize proven bottlenecks
- [ ] Keep assembly code simple and well-documented
- [ ] Test assembly optimizations thoroughly
- [ ] Maintain fallback implementations

### Verification
- [ ] Verify optimized code produces correct results
- [ ] Measure actual performance improvement
- [ ] Test edge cases and error conditions
- [ ] Document optimization techniques used

## Conclusion

Effective optimization for Permut8 follows the 80/20 principle: focus on algorithmic choices and memory access patterns for the biggest performance gains. The key is to measure first, optimize systematically, and maintain code correctness throughout the process.

Remember that the best optimization is often choosing the right algorithm from the start. Micro-optimizations have their place, but they should never come at the expense of code clarity and correctness unless absolutely necessary.

By following these principles and focusing your optimization efforts where they matter most, you can achieve excellent real-time performance on Permut8 while maintaining clean, maintainable code.