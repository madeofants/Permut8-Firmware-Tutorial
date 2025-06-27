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

const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT






function floatToQ15(float value) returns int result {
    result = value * 32768.0;
}


function Q15ToFloat(int value) returns float result {
    result = value / 32768.0;
}


global int half_volume = 16384;

```

### Q12 Format (Extended Range)
```impala





function convertParamToQ12() returns int gain_q12 {
    gain_q12 = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 41;
}
```

## Fixed-Point DSP Operations

### Basic Arithmetic
```impala

function multiplyQ15(int a, int b) returns int result {
    result = (a * b) >> 15;
    if (result > 32767) {
        result = 32767;
    } else if (result < -32768) {
        result = -32768;
    }
}


function divideQ15(int a, int b) returns int result {
    result = (a << 15) / b;
}



global int reciprocal_3_q15 = 10923;

function fastDivideBy3(int input) returns int output {
    output = multiplyQ15(input, reciprocal_3_q15);
}
```

### Biquad Filter Implementation
```impala

global int x1 = 0;
global int x2 = 0;
global int y1 = 0;
global int y2 = 0;

function operate1() {

    int a1_q15 = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 327;
    int a2_q15 = (int)global params[SWITCHES_PARAM_INDEX] * 327;  
    int b0_q15 = (int)global params[OPERATOR_1_PARAM_INDEX] * 327;
    int b1_q15 = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 327;
    int b2_q15 = (int)global params[OPERAND_1_LOW_PARAM_INDEX] * 327;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        
        int input_q15 = signal[i] << 4;
        

        int y = multiplyQ15(b0_q15, input_q15) +
                multiplyQ15(b1_q15, x1) + 
                multiplyQ15(b2_q15, x2) -
                multiplyQ15(a1_q15, y1) -
                multiplyQ15(a2_q15, y2);
                

        x2 = x1; x1 = input_q15;
        y2 = y1; y1 = y;
        
        signal[i] = y >> 4;
        i = i + 1;
    }
}
```

### Oscillator with Fixed-Point Phase
```impala

global int SINE_TABLE_SIZE = 1024;
global array sine_table_q15[1024];
global int phase = 0;

function operate2() {
    int frequency = (int)global params[CLOCK_FREQ_PARAM_INDEX];
    


    int phase_increment = (frequency * SINE_TABLE_SIZE * 655) >> 8;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        

        int table_index = (phase >> 6) & (SINE_TABLE_SIZE - 1);
        

        int sine_q15 = sine_table_q15[table_index];
        

        int amplitude = (int)global params[SWITCHES_PARAM_INDEX] * 20;
        signal[i] = (sine_q15 * amplitude) >> 15;
        
        phase = phase + phase_increment;
        i = i + 1;
    }
}
```

## Advanced Fixed-Point Techniques

### Envelope Generator with Exponential Decay
```impala

global int envelope_q15 = 0;
global int envelope_state = 0;
global int gate_triggered = 0;
global int ATTACK = 0;
global int DECAY = 1;

function operate1() {
    int attack_rate = (int)global params[CLOCK_FREQ_PARAM_INDEX] + 1;
    int decay_shift = (int)global params[SWITCHES_PARAM_INDEX] >> 3;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        
        if (gate_triggered != 0) {
            envelope_q15 = 0;
            envelope_state = ATTACK;
        }
        
        if (envelope_state == ATTACK) {
            envelope_q15 = envelope_q15 + (attack_rate << 8);
            if (envelope_q15 >= 32767) {
                envelope_q15 = 32767;
                envelope_state = DECAY;
            }
        } else if (envelope_state == DECAY) {

            envelope_q15 = envelope_q15 - (envelope_q15 >> decay_shift);
        }
        

        signal[i] = (signal[i] * envelope_q15) >> 15;
        i = i + 1;
    }
}
```

### Saturation with Fixed-Point
```impala

function softSaturateQ15(int input) returns int result {
    if (input > 24576) {
        int excess = input - 24576;
        result = 24576 + (excess >> 2);
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

function safeMultiplyQ15(int a, int b) returns int result {

    int temp = a * b;
    result = temp >> 15;
    

    if (result > 32767) {
        result = 32767;
    } else if (result < -32768) {
        result = -32768;
    }
}


function accumulateWithOverflowGuard(array values, int count) returns int accumulator {
    accumulator = 0;
    int i = 0;
    loop {
        if (i >= count) break;
        accumulator = accumulator + values[i];
        if (accumulator > 1000000) {
            accumulator = 1000000;
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