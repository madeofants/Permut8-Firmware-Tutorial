# Memory Patterns - Cache-Friendly Data Access Strategies

## Overview

Memory access patterns dramatically impact DSP performance due to CPU cache behavior. Sequential access patterns maximize cache hits, while random access causes expensive cache misses. Understanding and optimizing memory layouts can improve performance by 200-500% without changing algorithmic complexity.

## Cache Performance Impact

**Cache-unfriendly patterns** create performance bottlenecks:
- Random memory access: 100-300 CPU cycles per miss
- Strided access with large gaps: 50-150 cycles
- Frequent pointer chasing: 20-100 cycles per hop
- Poor spatial locality: Wastes cache line bandwidth

**Cache-friendly patterns** maximize performance:
- Sequential access: 1-3 CPU cycles per access
- Small stride access: 2-5 cycles
- Data structure alignment: Optimal cache utilization
- Prefetching opportunities: Predictable access patterns

## Sequential Access Patterns

### Before: Poor Memory Access
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


function operate1()
locals int i, int delay_length, int read_pos, int delayed_sample, int output
{
    delay_length = global (int)global params[CLOCK_FREQ_PARAM_INDEX] * 10;
    
    for (i = 0 to BLOCK_SIZE - 1) {

        read_pos = (global write_pos - delay_length) & DELAY_MASK;
        delayed_sample = global delay_buffer[read_pos];
        
        output = global signal[i] + (delayed_sample >> 1);
        global delay_buffer[global write_pos] = output;
        
        global signal[i] = output;
        global write_pos = (global write_pos + 1) & DELAY_MASK;
    }
}

```

### After: Cache-Friendly Sequential Access
```impala

function operate1_optimized()
locals int delay_length, int feedback, int block, int end, int read_start, int i
locals int read_pos, int delayed, int output
{
    delay_length = global (int)global params[CLOCK_FREQ_PARAM_INDEX] * 10;
    feedback = global (int)global params[SWITCHES_PARAM_INDEX] / 100;
    

    block = 0;
    while (block < BLOCK_SIZE) {
        end = block + 32;
        if (end > BLOCK_SIZE) {
            end = BLOCK_SIZE;
        }
        

        read_start = (global write_pos - delay_length) & DELAY_MASK;
        
        for (i = block to end - 1) {

            read_pos = (read_start + (i - block)) & DELAY_MASK;
            delayed = global delay_buffer[read_pos];
            
            output = global signal[i] + (delayed * feedback >> 8);
            global delay_buffer[global write_pos] = output;
            
            global signal[i] = output;
            global write_pos = (global write_pos + 1) & DELAY_MASK;
        }
        
        block = block + 32;
    }
}
```

## Data Structure Optimization

### Array of Structures vs Structure of Arrays
```impala


global array filter_data[8 * 9]


function operate2_aos()
locals int i, int f, int y, int filter_offset
{
    for (i = 0 to BLOCK_SIZE - 1) {
        for (f = 0 to 7) {
            filter_offset = f * 9;

            y = (global filter_data[filter_offset + 6] * global signal[i] +
                 global filter_data[filter_offset + 7] * global filter_data[filter_offset + 0] +
                 global filter_data[filter_offset + 8] * global filter_data[filter_offset + 1] -
                 global filter_data[filter_offset + 4] * global filter_data[filter_offset + 2] -
                 global filter_data[filter_offset + 5] * global filter_data[filter_offset + 3]) >> 8;
        }
    }
}


global array x1[8]
global array x2[8]
global array y1[8]
global array y2[8]
global array a1[8]
global array a2[8]
global array b0[8]
global array b1[8]
global array b2[8]
global array y_temp[8]


function operate2_soa()
locals int i, int f, int input
{
    for (i = 0 to BLOCK_SIZE - 1) {
        input = global signal[i];
        

        for (f = 0 to 7) {
            global y_temp[f] = (global b0[f] * input + 
                               global b1[f] * global x1[f] + 
                               global b2[f] * global x2[f] -
                               global a1[f] * global y1[f] - 
                               global a2[f] * global y2[f]) >> 8;
        }
        

        for (f = 0 to 7) {
            global x2[f] = global x1[f]; 
            global x1[f] = input;
            global y2[f] = global y1[f]; 
            global y1[f] = global y_temp[f];
        }
        
        global signal[i] = global y_temp[0];
    }
}
```

## Buffer Management Strategies

### Circular Buffer Optimization
```impala

const int BUFFER_SIZE = 1024
const int BUFFER_MASK = 1023

global array audio_buffer[BUFFER_SIZE]
global int read_ptr = 0
global int write_ptr = 512


function operate1_buffered()
locals int chunk_size, int chunk, int next_read, int i, int chunk_end
locals int delayed
{
    chunk_size = 16;
    
    chunk = 0;
    while (chunk < BLOCK_SIZE) {

        chunk_end = chunk + chunk_size;
        if (chunk_end > BLOCK_SIZE) {
            chunk_end = BLOCK_SIZE;
        }
        

        next_read = (global read_ptr + chunk_size) & BUFFER_MASK;

        

        for (i = chunk to chunk_end - 1) {

            delayed = global audio_buffer[global read_ptr];
            global audio_buffer[global write_ptr] = global signal[i];
            
            global signal[i] = (global signal[i] + delayed) >> 1;
            
            global read_ptr = (global read_ptr + 1) & BUFFER_MASK;
            global write_ptr = (global write_ptr + 1) & BUFFER_MASK;
        }
        
        chunk = chunk + chunk_size;
    }
}
```

### Memory Pool for Dynamic Allocation
```impala

const int POOL_SIZE = 4096
global array memory_pool[POOL_SIZE]
global int pool_offset = 0


function allocateFromPool(size) returns int
locals int ptr_offset
{
    if (global pool_offset + size > POOL_SIZE) {
        global pool_offset = 0;
    }
    
    ptr_offset = global pool_offset;
    global pool_offset = global pool_offset + size;
    return ptr_offset;
}


function operate2_pooled()
locals int temp_buffer1_offset, int temp_buffer2_offset, int i
{
    temp_buffer1_offset = allocateFromPool(BLOCK_SIZE);
    temp_buffer2_offset = allocateFromPool(BLOCK_SIZE);
    

    for (i = 0 to BLOCK_SIZE - 1) {
        global memory_pool[temp_buffer1_offset + i] = (global signal[i] * global (int)global params[CLOCK_FREQ_PARAM_INDEX]) >> 8;
        global memory_pool[temp_buffer2_offset + i] = applyFilter(global memory_pool[temp_buffer1_offset + i]);
        global signal[i] = global memory_pool[temp_buffer2_offset + i];
    }
}
```

## Real-World Example: Multi-Tap Delay

```impala

const int TAP_COUNT = 4
global array delay_buffer[2048]
global array tap_positions[TAP_COUNT]
global array tap_gains[TAP_COUNT]
global array positions[1]

function operate1_multitap()
locals int write_pos, int i, int dry_signal, int wet_sum, int tap, int read_pos
{
    write_pos = global positions[0];
    

    if (global tap_positions[0] == 0) {
        global tap_positions[0] = 100;
        global tap_positions[1] = 250;
        global tap_positions[2] = 500;
        global tap_positions[3] = 1000;
        global tap_gains[0] = 204;
        global tap_gains[1] = 153;
        global tap_gains[2] = 102;
        global tap_gains[3] = 51;
    }
    

    for (i = 0 to BLOCK_SIZE - 1) {
        dry_signal = global signal[i];
        wet_sum = 0;
        

        for (tap = 0 to TAP_COUNT - 1) {
            read_pos = (write_pos - global tap_positions[tap]) & 2047;
            wet_sum = wet_sum + ((global delay_buffer[read_pos] * global tap_gains[tap]) >> 8);
        }
        

        global delay_buffer[write_pos] = dry_signal;
        

        global signal[i] = dry_signal + (wet_sum >> 2);
        
        write_pos = (write_pos + 1) & 2047;
    }
    
    global positions[0] = write_pos;
}
```

## Performance Guidelines

**Optimize for sequential access:**
- Process arrays from start to finish
- Avoid large strides between accesses
- Group similar operations together

**Data structure design:**
- Use Structure of Arrays for parallel processing
- Align data to cache line boundaries (32-64 bytes)
- Keep frequently accessed data together

**Buffer management:**
- Use power-of-2 sizes for efficient modulo operations
- Implement circular buffers with proper masking
- Pre-allocate from memory pools to avoid fragmentation

Cache-friendly memory patterns typically improve performance by 200-500% through better CPU cache utilization, with the largest gains seen in algorithms that process large data sets or use complex data structures.