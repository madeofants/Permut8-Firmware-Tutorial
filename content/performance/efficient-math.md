# Efficient Math Techniques

Mathematical operations can be significant performance bottlenecks in real-time audio processing. The Permut8's ARM Cortex-M4 processor includes hardware floating-point support, but even fast FPU operations can accumulate overhead when performed thousands of times per second. This guide covers practical techniques for optimizing mathematical calculations in Permut8 firmware.

## Fast Approximations vs. Exact Calculations

The key insight for audio DSP optimization is that perfect mathematical accuracy is often unnecessary. Human hearing cannot distinguish differences below certain thresholds, making fast approximations ideal for real-time processing.

### Sine Wave Approximation

Trigonometric functions like `sin()` and `cos()` are expensive to compute. For audio applications, polynomial approximations provide excellent results with dramatically better performance.

```impala
// Expensive: exact sine calculation using native function
function expensive_sine(float x) returns float result {
    result = sine(x);  // Native sine function
}

// Fast: polynomial approximation (error < 0.1%)
function fast_sine(float x) returns float result {
    // Normalize to [-π, π]
    while (x > 3.14159) {
        x = x - 6.28318;
    }
    while (x < -3.14159) {
        x = x + 6.28318;
    }
    
    // Polynomial approximation
    float x2 = x * x;
    result = x * (1.0 - x2 * (0.16666 - x2 * 0.00833));
}

// Audio oscillator using fast approximation
global float osc_phase = 0.0;
global float osc_phase_increment = 0.0;

function setOscillatorFrequency(float freq, float sample_rate) {
    osc_phase_increment = (freq * 6.28318) / sample_rate;
}

function processOscillator() returns float output {
    output = fast_sine(osc_phase);
    osc_phase = osc_phase + osc_phase_increment;
    if (osc_phase > 6.28318) {
        osc_phase = osc_phase - 6.28318;
    }
}
```

Performance comparison on Permut8:
- `sin()`: ~45 CPU cycles
- `fast_sine()`: ~12 CPU cycles
- Accuracy: >99.9% for audio applications

### Fast Exponential Decay

Envelope generators and filter decay calculations often use exponential functions. Integer-based approximations can be much faster than floating-point exponentials.

```impala
// Expensive: floating-point exponential decay
global float env_value = 1.0;
global float env_decay_rate = 0.999;

function processSlowEnvelope() returns float result {
    env_value = env_value * env_decay_rate;
    result = env_value;
}

// Fast: fixed-point exponential approximation
global int fast_env_value = 65536;  // 16.16 fixed point
global int fast_decay_factor = 65470;  // Equivalent to 0.999 in fixed point

function processFastEnvelope() returns float result {
    fast_env_value = (fast_env_value * fast_decay_factor) >> 16;
    result = fast_env_value / 65536.0;
}

// Even faster: lookup table with linear interpolation
global array decay_table[256] = {
    65536, 65470, 65405, 65340, 65275, 65211, 65147, 65083,
    // ... fill with pre-computed decay values
    65020, 64957, 64894, 64832, 64769, 64707, 64645, 64583
};

global int table_env_value = 65536;
global int table_pos = 0;

function processTableEnvelope() returns float result {
    table_env_value = decay_table[table_pos];
    table_pos = (table_pos + 1) & 255;  // Wrap at 256
    result = table_env_value / 65536.0;
}
```

### Square Root Approximation

Audio applications frequently need square root calculations for RMS detection, distance calculations, and envelope following. Fast integer approximations work well for these use cases.

```impala
// Fast integer square root using bit manipulation
function fast_sqrt(int x) returns int result {
    if (x == 0) {
        result = 0;
    } else {
        result = 0;
        int bit = 1 << 30;  // Start with highest bit
        
        while (bit > x) {
            bit = bit >> 2;
        }
        
        while (bit != 0) {
            if (x >= result + bit) {
                x = x - result - bit;
                result = (result >> 1) + bit;
            } else {
                result = result >> 1;
            }
            bit = bit >> 2;
        }
    }
}

// RMS calculation using fast square root
global int rms_sum_squares = 0;
global int rms_sample_count = 0;
global int RMS_WINDOW_SIZE = 64;

function processRMS(float input) returns float result {
    // Convert to integer for fast processing
    int sample = input * 32767.0;
    rms_sum_squares = rms_sum_squares + ((sample * sample) >> 10);  // Scale to prevent overflow
    rms_sample_count = rms_sample_count + 1;
    
    if (rms_sample_count >= RMS_WINDOW_SIZE) {
        int rms_int = fast_sqrt(rms_sum_squares / RMS_WINDOW_SIZE);
        result = rms_int / 32767.0;
        
        rms_sum_squares = 0;
        rms_sample_count = 0;
    } else {
        result = 0.0;  // No output until window complete
    }
}
```

## Bitwise Operations for Speed

Bit manipulation operations are among the fastest calculations available on ARM processors. Many common mathematical operations can be replaced with bitwise equivalents.

### Power-of-Two Operations

Multiplication and division by powers of two can be replaced with bit shifts, which are single-cycle operations.

```impala
// Slow: floating-point arithmetic
function slow_gain(float input, float gain_db) returns float result {
    float gain_linear = pow(10.0, gain_db / 20.0);
    result = input * gain_linear;
}

// Fast: bit-shift gain control (for simple gain adjustments)
function fast_gain(int input, int shift_amount) returns int result {
    if (shift_amount >= 0) {
        result = input << shift_amount;  // Multiply by 2^shift_amount
    } else {
        result = input >> (-shift_amount);  // Divide by 2^shift_amount
    }
}

// Practical example: simple compressor with bit-shift gain reduction
global int comp_threshold = 16384;  // 50% of full scale
global int comp_attack_shift = 1;   // 2:1 compression ratio

function processCompressor(int input) returns int result {
    int abs_input;
    if (input < 0) {
        abs_input = -input;
    } else {
        abs_input = input;
    }
    
    if (abs_input > comp_threshold) {
        // Simple compression: reduce gain above threshold
        int excess = abs_input - comp_threshold;
        excess = excess >> comp_attack_shift;  // Divide excess by 2
        int output = comp_threshold + excess;
        if (input < 0) {
            result = -output;
        } else {
            result = output;
        }
    } else {
        result = input;
    }
}
```

### Fast Modulo Operations

Modulo operations with power-of-two values can be replaced with bitwise AND operations.

```impala
// Slow: modulo with division
function slow_wrap(int index, int buffer_size) returns int result {
    result = index % buffer_size;  // Only fast if buffer_size is power of 2
}

// Fast: bitwise AND (requires power-of-2 buffer size)
function fast_wrap(int index, int buffer_mask) returns int result {
    result = index & buffer_mask;  // buffer_mask = buffer_size - 1
}

// Circular buffer using fast wrapping
global int BUFFER_SIZE = 1024;  // Must be power of 2
global int BUFFER_MASK = 1023;  // BUFFER_SIZE - 1
global array circ_buffer[1024];
global int write_pos = 0;

function writeCircularBuffer(float sample) {
    circ_buffer[write_pos] = sample;
    write_pos = (write_pos + 1) & BUFFER_MASK;  // Fast wrap
}

function readCircularBuffer(int delay_samples) returns float result {
    int read_pos = (write_pos - delay_samples) & BUFFER_MASK;
    result = circ_buffer[read_pos];
}
```

## Fixed-Point Arithmetic Patterns

For maximum performance in mathematical operations, fixed-point arithmetic eliminates floating-point overhead while maintaining sufficient precision for audio applications.

### Mixing and Crossfading

Audio mixing operations benefit significantly from fixed-point optimization.

```impala
// Standard floating-point crossfade
function float_crossfade(float a, float b, float mix) returns float result {
    result = a * (1.0 - mix) + b * mix;
}

// Fixed-point crossfade (16.16 format)
function fixed_crossfade(int a, int b, int mix_16_16) returns int result {
    int inv_mix = 65536 - mix_16_16;  // 1.0 - mix in 16.16 format
    
    // Multiply and shift back to 16.16 format
    int result_a = (a * inv_mix) >> 16;
    int result_b = (b * mix_16_16) >> 16;
    
    result = result_a + result_b;
}

// Practical mixer using fixed-point math
global int NUM_CHANNELS = 4;
global array channel_gains[4];  // 16.16 fixed point

function setChannelGain(int channel, float gain) {
    channel_gains[channel] = gain * 65536.0;
}

function mixChannels(array inputs[4]) returns int result {
    int sum = 0;
    
    // Mix all channels
    sum = sum + ((inputs[0] * channel_gains[0]) >> 16);
    sum = sum + ((inputs[1] * channel_gains[1]) >> 16);
    sum = sum + ((inputs[2] * channel_gains[2]) >> 16);
    sum = sum + ((inputs[3] * channel_gains[3]) >> 16);
    
    // Clamp to prevent overflow
    if (sum > 32767) {
        sum = 32767;
    }
    if (sum < -32768) {
        sum = -32768;
    }
    
    result = sum;
}
```

## Performance Measurement and Validation

Always measure the actual performance impact of mathematical optimizations. The Permut8's real-time constraints make measurement essential.

```impala
// Simple cycle counter for performance measurement
global int perf_start_cycles;

function startPerformanceTimer() {
    perf_start_cycles = getCycleCount();  // Native function to get cycle count
}

function stopPerformanceTimer() returns int cycles {
    int end_cycles = getCycleCount();
    cycles = end_cycles - perf_start_cycles;
}

// Compare mathematical implementations
function benchmark_math_functions() {
    float test_input = 1.57;  // π/2
    
    // Test standard sine
    startPerformanceTimer();
    float result1 = sine(test_input);
    int std_cycles = stopPerformanceTimer();
    
    // Test fast sine
    startPerformanceTimer();
    float result2 = fast_sine(test_input);
    int fast_cycles = stopPerformanceTimer();
    
    // Display results on LEDs (cycle count as brightness)
    displayLEDs[0] = std_cycles >> 2;   // Standard implementation
    displayLEDs[1] = fast_cycles >> 2;  // Fast implementation
    displayLEDs[2] = abs(result1 - result2) * 1000;  // Error magnitude
}
```

## Key Takeaways

Mathematical optimization in Permut8 firmware follows several important principles:

**Choose Appropriate Precision**: Audio applications rarely need perfect mathematical accuracy. Fast approximations with 0.1% error are usually inaudible.

**Leverage Hardware Strengths**: ARM processors excel at integer and bitwise operations. Use these whenever possible instead of complex floating-point math.

**Measure Real Performance**: Theoretical improvements don't always translate to real-world benefits. Always profile your optimizations in the actual firmware context.

**Maintain Code Clarity**: Optimized code should still be readable and maintainable. Document the tradeoffs and expected accuracy of approximations.

The techniques in this guide can reduce mathematical processing overhead by 50-80% in typical audio applications, freeing up CPU cycles for more complex algorithms or allowing lower latency operation.
