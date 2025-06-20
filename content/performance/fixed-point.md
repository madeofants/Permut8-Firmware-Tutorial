# Fixed-Point Math - Integer Math for Performance-Critical Code

## Overview

Fixed-point arithmetic replaces expensive floating-point operations with fast integer math by using a predetermined number of fractional bits. This technique provides predictable performance, eliminates floating-point unit dependencies, and dramatically speeds up mathematical operations in embedded DSP systems.

## Performance Impact

**Floating-point operations** on embedded systems:
- Multiplication: 10-30 CPU cycles
- Division: 20-100 CPU cycles  
- Trigonometric functions: 50-200 CPU cycles
- Unpredictable execution time
- May require software emulation

**Fixed-point operations** deliver consistent speed:
- Multiplication: 1-2 CPU cycles
- Division by power-of-2: 1 cycle (bit shift)
- Addition/subtraction: 1 cycle
- Deterministic execution time
- 5-20x performance improvement

## Basic Fixed-Point Representation

### Q15 Format (Most Common for Audio)
```impala
// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT

// Q15: 1 sign bit + 15 fractional bits
// Range: -1.0 to +0.999969 (almost +1.0)
// Resolution: 1/32768 ≈ 0.00003

// Convert floating-point to Q15
function floatToQ15(float value) returns int result {
    result = value * 32768.0;
}

// Convert Q15 to floating-point  
function Q15ToFloat(int value) returns float result {
    result = value / 32768.0;
}

// Example: 0.5 in Q15 format
global int half_volume = 16384;  // 0.5 * 32768

```

### Q12 Format (Extended Range)
```impala
// Q12: 4 integer bits + 12 fractional bits  
// Range: -8.0 to +7.999756
// Resolution: 1/4096 ≈ 0.000244

// Useful for parameters that exceed ±1.0 range
function convertParamToQ12() returns int gain_q12 {
    gain_q12 = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 41;  // Convert 0-100 param to Q12 (0-10.0 range)
}
```

## Fixed-Point DSP Operations

### Basic Arithmetic
```impala
// Fixed-point multiplication (Q15 * Q15 = Q30, shift back to Q15)
function multiplyQ15(int a, int b) returns int result {
    result = (a * b) >> 15;
    if (result > 32767) {
        result = 32767;
    } else if (result < -32768) {
        result = -32768;
    }
}

// Fixed-point division (rare, expensive)
function divideQ15(int a, int b) returns int result {
    result = (a << 15) / b;  // Shift a up before division
}

// Faster: multiply by reciprocal (pre-computed)
// Instead of: output = input / 3
global int reciprocal_3_q15 = 10923;  // 1/3 in Q15 format

function fastDivideBy3(int input) returns int output {
    output = multiplyQ15(input, reciprocal_3_q15);
}
```

### Biquad Filter Implementation
```impala
// High-performance fixed-point biquad filter
global int x1 = 0;
global int x2 = 0;
global int y1 = 0;
global int y2 = 0;

function operate1() {
    // Filter coefficients in Q15 format
    int a1_q15 = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 327;  // Feedback coefficient
    int a2_q15 = (int)global params[SWITCHES_PARAM_INDEX] * 327;  
    int b0_q15 = (int)global params[OPERATOR_1_PARAM_INDEX] * 327;  // Feedforward coefficient
    int b1_q15 = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 327;
    int b2_q15 = (int)global params[OPERAND_1_LOW_PARAM_INDEX] * 327;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        
        int input_q15 = signal[i] << 4;  // Convert to Q15 (input is Q11)
        
        // Biquad equation in fixed-point
        int y = multiplyQ15(b0_q15, input_q15) +
                multiplyQ15(b1_q15, x1) + 
                multiplyQ15(b2_q15, x2) -
                multiplyQ15(a1_q15, y1) -
                multiplyQ15(a2_q15, y2);
                
        // Update delay line
        x2 = x1; x1 = input_q15;
        y2 = y1; y1 = y;
        
        signal[i] = y >> 4;  // Convert back to Q11
        i = i + 1;
    }
}
```

### Oscillator with Fixed-Point Phase
```impala
// Phase accumulator oscillator using Q16 phase
global int SINE_TABLE_SIZE = 1024;
global array sine_table_q15[1024];  // Pre-computed in Q15
global int phase = 0;

function operate2() {
    int frequency = (int)global params[CLOCK_FREQ_PARAM_INDEX];  // 0-100 range
    
    // Convert frequency to Q16 phase increment
    // phase_inc = (frequency * table_size * 65536) / sample_rate
    int phase_increment = (frequency * SINE_TABLE_SIZE * 655) >> 8;  // Optimized
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        
        // Extract integer part for table index
        int table_index = (phase >> 6) & (SINE_TABLE_SIZE - 1);
        
        // Get sine value in Q15 format
        int sine_q15 = sine_table_q15[table_index];
        
        // Apply amplitude and convert to output format
        int amplitude = (int)global params[SWITCHES_PARAM_INDEX] * 20;  // 0-100 to 0-2000 range
        signal[i] = (sine_q15 * amplitude) >> 15;
        
        phase = phase + phase_increment;  // Q16 phase accumulation
        i = i + 1;
    }
}
```

## Advanced Fixed-Point Techniques

### Envelope Generator with Exponential Decay
```impala
// Fixed-point envelope with bit-shift decay
global int envelope_q15 = 0;
global int envelope_state = 0;  // 0=ATTACK, 1=DECAY
global int gate_triggered = 0;
global int ATTACK = 0;
global int DECAY = 1;

function operate1() {
    int attack_rate = (int)global params[CLOCK_FREQ_PARAM_INDEX] + 1;   // Prevent division by zero
    int decay_shift = (int)global params[SWITCHES_PARAM_INDEX] >> 3;  // Decay rate as bit shift amount
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        
        if (gate_triggered != 0) {
            envelope_q15 = 0;
            envelope_state = ATTACK;
        }
        
        if (envelope_state == ATTACK) {
            envelope_q15 = envelope_q15 + (attack_rate << 8);  // Linear attack
            if (envelope_q15 >= 32767) {
                envelope_q15 = 32767;
                envelope_state = DECAY;
            }
        } else if (envelope_state == DECAY) {
            // Exponential decay via bit shift (very fast!)
            envelope_q15 = envelope_q15 - (envelope_q15 >> decay_shift);
        }
        
        // Apply envelope to signal
        signal[i] = (signal[i] * envelope_q15) >> 15;
        i = i + 1;
    }
}
```

### Saturation with Fixed-Point
```impala
// Fast soft saturation using fixed-point
function softSaturateQ15(int input) returns int result {
    if (input > 24576) {          // 0.75 in Q15
        int excess = input - 24576;
        result = 24576 + (excess >> 2);  // Compress by 75%
    } else if (input < -24576) {
        int excess = input + 24576;
        result = -24576 + (excess >> 2);
    } else {
        result = input;
    }
}
```

## Precision and Overflow Management

### Avoiding Overflow
```impala
// Safe multiplication with overflow detection
function safeMultiplyQ15(int a, int b) returns int result {
    // Use 32-bit intermediate result
    int temp = a * b;
    result = temp >> 15;
    
    // Clamp to prevent overflow
    if (result > 32767) {
        result = 32767;
    } else if (result < -32768) {
        result = -32768;
    }
}

// Guard against accumulation overflow
function accumulateWithOverflowGuard(array values, int count) returns int accumulator {
    accumulator = 0;
    int i = 0;
    loop {
        if (i >= count) break;
        accumulator = accumulator + values[i];
        if (accumulator > 1000000) {
            accumulator = 1000000;  // Prevent overflow
        }
        i = i + 1;
    }
}
```

## Implementation Guidelines

**Choose the right format:**
- Q15 for standard audio processing (-1.0 to +1.0)
- Q12 for parameters with extended range
- Q8 for low-precision, high-speed operations

**Optimization strategies:**
- Pre-compute reciprocals instead of division
- Use bit shifts for powers-of-2 operations
- Combine operations to minimize intermediate conversions
- Watch for overflow in intermediate calculations

**Precision considerations:**
- Q15 provides ~0.003% resolution (sufficient for most audio)
- Accumulate in higher precision, then convert back
- Consider dithering for very low-level signals

Fixed-point arithmetic typically improves DSP performance by 500-2000% while maintaining audio quality equivalent to 16-bit systems.