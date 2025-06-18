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
// Bad: random access pattern destroys cache performance
function operate1()
locals int i, int delay_length, int read_pos, int delayed_sample, int output
{
    delay_length = global params[0] * 10;  // 0-1000 samples
    
    for (i = 0 to BLOCK_SIZE - 1) {
        // Random access to delay buffer - cache miss likely
        read_pos = (global write_pos - delay_length) & DELAY_MASK;
        delayed_sample = global delay_buffer[read_pos];
        
        output = global signal[i] + (delayed_sample >> 1);  // Divide by 2 instead of * 0.5
        global delay_buffer[global write_pos] = output;
        
        global signal[i] = output;
        global write_pos = (global write_pos + 1) & DELAY_MASK;
    }
}
```

### After: Cache-Friendly Sequential Access
```impala
// Good: process in blocks to maintain cache locality
function operate1_optimized()
locals int delay_length, int feedback, int block, int end, int read_start, int i
locals int read_pos, int delayed, int output
{
    delay_length = global params[0] * 10;
    feedback = global params[1] / 100;  // Integer division instead of * 0.01
    
    // Process samples in cache-sized chunks
    block = 0;
    while (block < BLOCK_SIZE) {
        end = block + 32;
        if (end > BLOCK_SIZE) {
            end = BLOCK_SIZE;
        }
        
        // Sequential read from delay buffer
        read_start = (global write_pos - delay_length) & DELAY_MASK;
        
        for (i = block to end - 1) {
            // Sequential access improves cache hit rate
            read_pos = (read_start + (i - block)) & DELAY_MASK;
            delayed = global delay_buffer[read_pos];
            
            output = global signal[i] + (delayed * feedback >> 8);  // Fixed-point multiplication
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
// Poor cache usage: Array of Structures (AoS) - Impala approach
// Impala doesn't have structs, so simulate with grouped arrays
global array filter_data[8 * 9]  // 8 filters * 9 values each (x1,x2,y1,y2,a1,a2,b0,b1,b2)

// Bad: accessing scattered data causes cache misses
function operate2_aos()
locals int i, int f, int y, int filter_offset
{
    for (i = 0 to BLOCK_SIZE - 1) {
        for (f = 0 to 7) {
            filter_offset = f * 9;
            // Each access loads scattered struct data, wastes cache bandwidth
            y = (global filter_data[filter_offset + 6] * global signal[i] +     // b0
                 global filter_data[filter_offset + 7] * global filter_data[filter_offset + 0] +  // b1 * x1
                 global filter_data[filter_offset + 8] * global filter_data[filter_offset + 1] -  // b2 * x2
                 global filter_data[filter_offset + 4] * global filter_data[filter_offset + 2] -  // a1 * y1
                 global filter_data[filter_offset + 5] * global filter_data[filter_offset + 3]) >> 8;  // a2 * y2
        }
    }
}

// Better cache usage: Structure of Arrays (SoA) - Impala approach
global array x1[8]      // Input histories grouped
global array x2[8]
global array y1[8]      // Output histories grouped  
global array y2[8]
global array a1[8]      // Coefficients grouped
global array a2[8]
global array b0[8]
global array b1[8]
global array b2[8]
global array y_temp[8]  // Temporary output array

// Good: sequential access to same data type
function operate2_soa()
locals int i, int f, int input
{
    for (i = 0 to BLOCK_SIZE - 1) {
        input = global signal[i];
        
        // Process all filters with same coefficient type sequentially
        for (f = 0 to 7) {
            global y_temp[f] = (global b0[f] * input + 
                               global b1[f] * global x1[f] + 
                               global b2[f] * global x2[f] -
                               global a1[f] * global y1[f] - 
                               global a2[f] * global y2[f]) >> 8;
        }
        
        // Update all histories sequentially
        for (f = 0 to 7) {
            global x2[f] = global x1[f]; 
            global x1[f] = input;
            global y2[f] = global y1[f]; 
            global y1[f] = global y_temp[f];
        }
        
        global signal[i] = global y_temp[0];  // Use first filter output
    }
}
```

## Buffer Management Strategies

### Circular Buffer Optimization
```impala
// Cache-friendly circular buffer design
const int BUFFER_SIZE = 1024     // Power of 2 for efficient masking
const int BUFFER_MASK = 1023     // Efficient modulo operation

global array audio_buffer[BUFFER_SIZE]
global int read_ptr = 0
global int write_ptr = 512        // Half-buffer offset for delay

// Optimized buffer access with prefetching
function operate1_buffered()
locals int chunk_size, int chunk, int next_read, int i, int chunk_end
locals int delayed
{
    chunk_size = 16;    // Process in cache-line sized chunks
    
    chunk = 0;
    while (chunk < BLOCK_SIZE) {
        // Calculate chunk end
        chunk_end = chunk + chunk_size;
        if (chunk_end > BLOCK_SIZE) {
            chunk_end = BLOCK_SIZE;
        }
        
        // Prefetch next chunk of data (hint to CPU - not directly available in Impala)
        next_read = (global read_ptr + chunk_size) & BUFFER_MASK;
        // Note: Actual prefetching would be handled by compiler optimization
        
        // Process current chunk sequentially
        for (i = chunk to chunk_end - 1) {
            // Sequential reads maximize cache efficiency
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
// Pre-allocated memory pool to avoid fragmentation
const int POOL_SIZE = 4096
global array memory_pool[POOL_SIZE]
global int pool_offset = 0

// Allocate from pool in sequential chunks
function allocateFromPool(size) returns int
locals int ptr_offset
{
    if (global pool_offset + size > POOL_SIZE) {
        global pool_offset = 0;  // Reset to beginning (circular pool)
    }
    
    ptr_offset = global pool_offset;
    global pool_offset = global pool_offset + size;
    return ptr_offset;  // Return offset into memory pool
}

// Example: allocate temporary buffers with good locality
function operate2_pooled()
locals int temp_buffer1_offset, int temp_buffer2_offset, int i
{
    temp_buffer1_offset = allocateFromPool(BLOCK_SIZE);
    temp_buffer2_offset = allocateFromPool(BLOCK_SIZE);
    
    // Both buffers are adjacent in memory - excellent cache behavior
    for (i = 0 to BLOCK_SIZE - 1) {
        global memory_pool[temp_buffer1_offset + i] = (global signal[i] * global params[0]) >> 8;
        global memory_pool[temp_buffer2_offset + i] = applyFilter(global memory_pool[temp_buffer1_offset + i]);
        global signal[i] = global memory_pool[temp_buffer2_offset + i];
    }
}
```

## Real-World Example: Multi-Tap Delay

```impala
// Cache-optimized multi-tap delay with grouped operations
const int TAP_COUNT = 4
global array delay_buffer[2048]
global array tap_positions[TAP_COUNT]  // Initialized with: 100, 250, 500, 1000
global array tap_gains[TAP_COUNT]      // Initialized with: 204, 153, 102, 51 (0.8, 0.6, 0.4, 0.2 * 255)
global array positions[1]              // Current write position

function operate1_multitap()
locals int write_pos, int i, int dry_signal, int wet_sum, int tap, int read_pos
{
    write_pos = global positions[0];  // Current write position
    
    // Initialize tap positions and gains if not done
    if (global tap_positions[0] == 0) {
        global tap_positions[0] = 100;
        global tap_positions[1] = 250;
        global tap_positions[2] = 500;
        global tap_positions[3] = 1000;
        global tap_gains[0] = 204;  // 0.8 * 255
        global tap_gains[1] = 153;  // 0.6 * 255
        global tap_gains[2] = 102;  // 0.4 * 255
        global tap_gains[3] = 51;   // 0.2 * 255
    }
    
    // Process all taps for each sample (better cache locality than tap-by-tap)
    for (i = 0 to BLOCK_SIZE - 1) {
        dry_signal = global signal[i];
        wet_sum = 0;
        
        // Read all taps sequentially for current sample
        for (tap = 0 to TAP_COUNT - 1) {
            read_pos = (write_pos - global tap_positions[tap]) & 2047;
            wet_sum = wet_sum + ((global delay_buffer[read_pos] * global tap_gains[tap]) >> 8);
        }
        
        // Write new sample to delay buffer
        global delay_buffer[write_pos] = dry_signal;
        
        // Mix dry and wet signals
        global signal[i] = dry_signal + (wet_sum >> 2);  // Divide by 4
        
        write_pos = (write_pos + 1) & 2047;
    }
    
    global positions[0] = write_pos;  // Store updated position
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