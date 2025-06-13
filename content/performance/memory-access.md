# Memory Access Optimization

Memory access patterns have a dramatic impact on Permut8 firmware performance. The ARM Cortex-M4's cache architecture and memory hierarchy reward predictable, sequential access patterns while penalizing random memory accesses. Understanding and optimizing memory usage is essential for maintaining real-time audio performance.

## Understanding Permut8 Memory Architecture

The Permut8's ARM Cortex-M4 includes several types of memory with different performance characteristics:

- **SRAM**: Fast local memory, single-cycle access when cached
- **Flash**: Slower program storage, cached for frequently accessed code
- **Cache**: Hardware cache improves repeated access to the same memory regions
- **DMA Buffers**: Special memory regions optimized for audio I/O

### Memory Access Performance

Different access patterns have vastly different performance implications:

```impala
// Cache-friendly: sequential access pattern
function efficient_buffer_process(array buffer, int size) {
    int i = 0;
    loop {
        if (i >= size) break;
        buffer[i] = buffer[i] * 0.5;  // Sequential access, cache-friendly
        i = i + 1;
    }
}

// Cache-unfriendly: random access pattern
function inefficient_buffer_process(array buffer, int size) {
    int i = 0;
    loop {
        if (i >= size) break;
        int random_index = (i * 7919) % size;  // Random access, cache-hostile
        buffer[random_index] = buffer[random_index] * 0.5;
        i = i + 1;
    }
}

// Performance measurement example
global int BUFFER_SIZE = 1024;
global array test_buffer[1024];

function compare_access_patterns() {
    int start, end;
    
    // Sequential access timing
    start = getCycleCount();
    efficient_buffer_process(test_buffer, BUFFER_SIZE);
    end = getCycleCount();
    int sequential_cycles = end - start;
    
    // Random access timing
    start = getCycleCount();
    inefficient_buffer_process(test_buffer, BUFFER_SIZE);
    end = getCycleCount();
    int random_cycles = end - start;
    
    // Display performance difference on LEDs
    displayLEDs[0] = sequential_cycles >> 8;  // Sequential (should be low)
    displayLEDs[1] = random_cycles >> 8;     // Random (typically 3-5x higher)
}
```

Typical performance differences:
- Sequential access: ~1 cycle per sample
- Random access: ~3-5 cycles per sample
- Cache miss penalty: 10-20 cycles

## Buffer Organization for Cache Efficiency

Organizing audio buffers for optimal cache usage significantly improves performance. The key principle is maximizing spatial and temporal locality.

### Interleaved vs. Separate Buffers

Buffer layout affects cache performance in multi-channel audio processing.

```impala
// Poor cache usage: separate channel buffers
global int STEREO_BUFFER_SIZE = 512;
global array left_buffer[512];
global array right_buffer[512];

function process_stereo_poor() {
    // Process left channel - loads left_buffer into cache
    int i = 0;
    loop {
        if (i >= STEREO_BUFFER_SIZE) break;
        left_buffer[i] = apply_effect(left_buffer[i]);
        i = i + 1;
    }
    
    // Process right channel - cache miss, loads right_buffer
    i = 0;
    loop {
        if (i >= STEREO_BUFFER_SIZE) break;
        right_buffer[i] = apply_effect(right_buffer[i]);
        i = i + 1;
    }
}

function apply_effect(float input) returns float result {
    result = input * 0.7 + input * input * 0.3;  // Simple saturation
}

// Better cache usage: interleaved stereo buffer
global array stereo_buffer[1024];  // Interleaved L,R,L,R...

function process_stereo_efficient() {
    // Process both channels together - better cache locality
    int i = 0;
    loop {
        if (i >= STEREO_BUFFER_SIZE * 2) break;
        stereo_buffer[i] = apply_effect(stereo_buffer[i]);        // Left
        stereo_buffer[i+1] = apply_effect(stereo_buffer[i+1]);    // Right
        i = i + 2;
    }
}

// Best: SIMD-optimized processing (when possible)
global array simd_buffer[1024];  // Interleaved L,R,L,R...

function process_stereo_simd() {
    // ARM NEON can process multiple samples simultaneously
    int i = 0;
    loop {
        if (i >= STEREO_BUFFER_SIZE * 2) break;
        // Process 4 samples at once (2 stereo pairs)
        simd_buffer[i] = apply_effect(simd_buffer[i]);
        simd_buffer[i+1] = apply_effect(simd_buffer[i+1]);
        simd_buffer[i+2] = apply_effect(simd_buffer[i+2]);
        simd_buffer[i+3] = apply_effect(simd_buffer[i+3]);
        i = i + 4;
    }
}
```

### Memory Pool Management

Pre-allocating memory pools eliminates dynamic allocation overhead and improves cache behavior.

```impala
// Inefficient: dynamic allocation during audio processing
// NOTE: Impala doesn't support dynamic allocation - this is for comparison only
global array dynamic_buffer[48000];  // Pre-allocated maximum size
global int dynamic_buffer_size = 0;
global int dynamic_write_pos = 0;

function setDelayTime(float delay_seconds, float sample_rate) {
    // NEVER do dynamic resizing in real-time audio!
    dynamic_buffer_size = delay_seconds * sample_rate;
    dynamic_write_pos = 0;
    
    // Clear buffer area
    int i = 0;
    loop {
        if (i >= dynamic_buffer_size) break;
        dynamic_buffer[i] = 0.0;
        i = i + 1;
    }
}

function processDynamicDelay(float input) returns float output {
    if (dynamic_buffer_size == 0) {
        output = input;
    } else {
        output = dynamic_buffer[dynamic_write_pos];
        dynamic_buffer[dynamic_write_pos] = input;
        dynamic_write_pos = (dynamic_write_pos + 1) % dynamic_buffer_size;
    }
}

// Efficient: pre-allocated memory pool
global int MAX_DELAY_SAMPLES = 48000;  // 1 second at 48kHz
global array delay_pool[48000];        // Pre-allocated pool
global int pool_buffer_size = 0;
global int pool_write_pos = 0;

function setPooledDelayTime(float delay_seconds, float sample_rate) returns int success {
    int required_size = delay_seconds * sample_rate;
    
    if (required_size > MAX_DELAY_SAMPLES) {
        success = 0;  // Delay too long for pool
    } else {
        // No allocation - just use pool directly
        pool_buffer_size = required_size;
        pool_write_pos = 0;
        
        // Clear the buffer area we'll use
        int i = 0;
        loop {
            if (i >= pool_buffer_size) break;
            delay_pool[i] = 0.0;
            i = i + 1;
        }
        
        success = 1;
    }
}

function processPooledDelay(float input) returns float output {
    output = delay_pool[pool_write_pos];
    delay_pool[pool_write_pos] = input;
    pool_write_pos = (pool_write_pos + 1) % pool_buffer_size;
}
```

## Data Structure Optimization

Choosing appropriate data structures and memory layouts dramatically affects performance.

### Structure of Arrays vs. Array of Structures

The choice between SoA and AoS depends on access patterns.

```impala
// Array of Structures (AoS) - good for processing complete objects
// Note: Impala uses separate arrays instead of structs
global int NUM_VOICES = 8;
global array voice_frequencies[8];
global array voice_amplitudes[8];
global array voice_phases[8];
global array voice_filter_states[8];

function process_all_voices_aos() {
    int i = 0;
    loop {
        if (i >= NUM_VOICES) break;
        // Good cache locality - process one voice completely
        voice_phases[i] = voice_phases[i] + voice_frequencies[i];
        float output = sine(voice_phases[i]) * voice_amplitudes[i];
        voice_filter_states[i] = output * 0.1 + voice_filter_states[i] * 0.9;
        i = i + 1;
    }
}

// Structure of Arrays (SoA) - good for bulk operations on single parameters
global array soa_frequencies[8];
global array soa_amplitudes[8];
global array soa_phases[8];
global array soa_filter_states[8];

function update_all_frequencies(float transpose) {
    // Excellent cache locality - all frequencies are contiguous
    int i = 0;
    loop {
        if (i >= NUM_VOICES) break;
        soa_frequencies[i] = soa_frequencies[i] * transpose;
        i = i + 1;
    }
}

function process_all_voices_soa() {
    int i = 0;
    loop {
        if (i >= NUM_VOICES) break;
        soa_phases[i] = soa_phases[i] + soa_frequencies[i];
        float output = sine(soa_phases[i]) * soa_amplitudes[i];
        soa_filter_states[i] = output * 0.1 + soa_filter_states[i] * 0.9;
        i = i + 1;
    }
}

// Hybrid approach: group related data
// Group frequently accessed together
global array osc_frequencies[8];
global array osc_phases[8];

// Separate arrays for bulk operations
global array hybrid_amplitudes[8];
global array hybrid_filter_states[8];

function update_frequencies_hybrid(float transpose) {
    int i = 0;
    loop {
        if (i >= NUM_VOICES) break;
        osc_frequencies[i] = osc_frequencies[i] * transpose;
        i = i + 1;
    }
}

function process_voices_hybrid() {
    int i = 0;
    loop {
        if (i >= NUM_VOICES) break;
        osc_phases[i] = osc_phases[i] + osc_frequencies[i];
        float output = sine(osc_phases[i]) * hybrid_amplitudes[i];
        hybrid_filter_states[i] = output * 0.1 + hybrid_filter_states[i] * 0.9;
        i = i + 1;
    }
}
```

### Circular Buffer Optimization

Circular buffers are common in audio applications. Efficient implementation considers both cache behavior and computational efficiency.

```impala
// Basic circular buffer with modulo (slow)
global int CIRC_SIZE = 1024;
global array circ_buffer[1024];
global int circ_write_pos = 0;

function writeCircBuffer(float sample) {
    circ_buffer[circ_write_pos] = sample;
    circ_write_pos = (circ_write_pos + 1) % CIRC_SIZE;  // Modulo is expensive
}

function readCircBuffer(int delay) returns float result {
    int read_pos = (circ_write_pos - delay + CIRC_SIZE) % CIRC_SIZE;
    result = circ_buffer[read_pos];
}

// Optimized circular buffer with power-of-2 size
global int FAST_SIZE = 1024;  // Must be power of 2
global int FAST_MASK = 1023;  // SIZE - 1
global array fast_buffer[1024];
global int fast_write_pos = 0;

function writeFastCircBuffer(float sample) {
    fast_buffer[fast_write_pos] = sample;
    fast_write_pos = (fast_write_pos + 1) & FAST_MASK;  // Bitwise AND is fast
}

function readFastCircBuffer(int delay) returns float result {
    int read_pos = (fast_write_pos - delay) & FAST_MASK;
    result = fast_buffer[read_pos];
}

// Batch processing for better cache usage
function write_block(array samples, int count) {
    int i = 0;
    loop {
        if (i >= count) break;
        fast_buffer[fast_write_pos] = samples[i];
        fast_write_pos = (fast_write_pos + 1) & FAST_MASK;
        i = i + 1;
    }
}

function read_block(array output, int delay, int count) {
    int read_pos = (fast_write_pos - delay) & FAST_MASK;
    int i = 0;
    loop {
        if (i >= count) break;
        output[i] = fast_buffer[read_pos];
        read_pos = (read_pos + 1) & FAST_MASK;
        i = i + 1;
    }
}
```

## Memory Access Patterns for DSP

Common DSP algorithms can be optimized by considering memory access patterns.

### Filter Implementation

Digital filters benefit significantly from memory access optimization.

```impala
// Standard biquad filter (reasonable performance)
global float bq_x1 = 0.0;
global float bq_x2 = 0.0;  // Input history
global float bq_y1 = 0.0;
global float bq_y2 = 0.0;  // Output history
global float bq_a0, bq_a1, bq_a2, bq_b1, bq_b2;  // Filter coefficients

function processBiquad(float input) returns float output {
    output = bq_a0 * input + bq_a1 * bq_x1 + bq_a2 * bq_x2 - bq_b1 * bq_y1 - bq_b2 * bq_y2;
    
    // Update history
    bq_x2 = bq_x1; bq_x1 = input;
    bq_y2 = bq_y1; bq_y1 = output;
}

// Memory-optimized biquad using circular buffer approach
global array opt_history[4] = {0.0, 0.0, 0.0, 0.0};  // x[n-1], x[n-2], y[n-1], y[n-2]
global int opt_history_pos = 0;
global array opt_coeffs[5];  // a0, a1, a2, b1, b2

function processOptimizedBiquad(float input) returns float output {
    // Calculate output using current history position
    output = opt_coeffs[0] * input + 
             opt_coeffs[1] * opt_history[(opt_history_pos + 2) & 3] +  // x[n-1]
             opt_coeffs[2] * opt_history[(opt_history_pos + 0) & 3] +  // x[n-2]
             opt_coeffs[3] * opt_history[(opt_history_pos + 3) & 3] +  // y[n-1]
             opt_coeffs[4] * opt_history[(opt_history_pos + 1) & 3];   // y[n-2]
    
    // Update circular buffer
    opt_history[opt_history_pos] = input;
    opt_history[(opt_history_pos + 1) & 3] = output;
    opt_history_pos = (opt_history_pos + 2) & 3;
}

// Block-based filter for maximum cache efficiency
global float blk_x1 = 0.0, blk_x2 = 0.0, blk_y1 = 0.0, blk_y2 = 0.0;
global float blk_a0, blk_a1, blk_a2, blk_b1, blk_b2;

function process_biquad_block(array input, array output, int size) {
    // Process samples in groups to maximize cache hits
    int i = 0;
    loop {
        if (i >= size) break;
        float out = blk_a0 * input[i] + blk_a1 * blk_x1 + blk_a2 * blk_x2 - blk_b1 * blk_y1 - blk_b2 * blk_y2;
        
        blk_x2 = blk_x1; blk_x1 = input[i];
        blk_y2 = blk_y1; blk_y1 = out;
        output[i] = out;
        i = i + 1;
    }
}
```

## Memory Layout Strategies

Strategic memory layout can improve cache efficiency across the entire firmware.

### Hot/Cold Data Separation

Separate frequently accessed data from rarely used configuration data.

```impala
// Better: separate hot and cold data
// Hot data in contiguous arrays for cache efficiency
global array hot_phases[8];
global array hot_frequencies[8];
global array hot_amplitudes[8];
global array hot_filter_states[8];

// Cold data separate (won't pollute cache during audio processing)
global array cold_preset_numbers[8];
global array cold_max_frequencies[8];
global array cold_min_frequencies[8];
global array cold_is_active[8];

function process_audio_efficient() {
    // Only touch hot data during audio processing
    int i = 0;
    loop {
        if (i >= NUM_VOICES) break;
        hot_phases[i] = hot_phases[i] + hot_frequencies[i];
        float output = sine(hot_phases[i]) * hot_amplitudes[i];
        hot_filter_states[i] = output * 0.1 + hot_filter_states[i] * 0.9;
        i = i + 1;
    }
}

function configure_voice(int voice, int preset) {
    // Cold data access only during configuration
    cold_preset_numbers[voice] = preset;
    cold_is_active[voice] = 1;
}
```

## Performance Monitoring

Monitor memory access efficiency to validate optimizations.

```impala
global int profiler_cache_hits = 0;
global int profiler_cache_misses = 0;
global array profiler_test_buffer[1024];

function start_profiling() {
    // Initialize profiler state
    profiler_cache_hits = 0;
    profiler_cache_misses = 0;
}

function measure_memory_performance() {
    int start_cycles = getCycleCount();
    
    // Your memory-intensive code here
    int i = 0;
    loop {
        if (i >= 1024) break;
        profiler_test_buffer[i] = profiler_test_buffer[i] * 1.1;
        i = i + 1;
    }
    
    int end_cycles = getCycleCount();
    int cycles_per_sample = (end_cycles - start_cycles) / 1024;
    
    // Display performance metrics
    displayLEDs[0] = cycles_per_sample;  // Should be 1-2 for good cache usage
}
```

## Key Principles

Effective memory optimization for Permut8 firmware follows these principles:

**Sequential Access**: Process data in order whenever possible. Sequential access maximizes cache efficiency.

**Data Locality**: Keep related data close together in memory. Process data that's used together at the same time.

**Pre-allocation**: Avoid dynamic memory allocation during audio processing. Use pre-allocated pools instead.

**Hot/Cold Separation**: Keep frequently accessed data separate from configuration data to avoid cache pollution.

**Block Processing**: Process data in blocks rather than one sample at a time when the algorithm allows.

Memory access optimization can improve overall firmware performance by 30-50%, making the difference between a firmware that works and one that performs excellently under all conditions.
