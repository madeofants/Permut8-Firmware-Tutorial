# Lookup Tables - Pre-Computed Optimization Techniques

## Overview

Lookup tables (LUTs) replace expensive runtime calculations with pre-computed values stored in memory. This technique transforms costly mathematical operations into simple memory reads, dramatically improving performance for functions that can be approximated or have limited input ranges.

## Performance Impact

**Runtime calculations** create processing bottlenecks:
- Trigonometric functions: 50-200 CPU cycles
- Logarithmic operations: 30-100 CPU cycles  
- Power/exponential functions: 40-150 CPU cycles
- Non-linear transformations: 20-80 CPU cycles

**Lookup tables** deliver immediate benefits:
- Memory read: 1-3 CPU cycles
- 10-50x performance improvement for complex functions
- Deterministic execution time
- Reduced CPU load for other processing

## Basic Lookup Table Pattern

### Before: Runtime Calculation
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


global float osc_phase = 0.0;

function operate1() {
    float frequency = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 0.01;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        osc_phase = osc_phase + frequency * TWO_PI / SAMPLE_RATE;
        signal[i] = sine(osc_phase) * 2000;
        i = i + 1;
    }
}

```

### After: Sine Wave Lookup Table
```impala

global int SINE_TABLE_SIZE = 1024;
global array sine_table[1024];
global int lut_phase = 0;


function initializeSineTable() {
    int i = 0;
    loop {
        if (i >= SINE_TABLE_SIZE) break;
        float angle = (i * TWO_PI) / SINE_TABLE_SIZE;
        sine_table[i] = sine(angle) * 2000;
        i = i + 1;
    }
}


function operate1() {
    float frequency = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 0.01;
    int phase_increment = (frequency * SINE_TABLE_SIZE) / SAMPLE_RATE;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        int table_index = lut_phase >> PHASE_FRACTIONAL_BITS;
        signal[i] = sine_table[table_index & (SINE_TABLE_SIZE - 1)];
        lut_phase = lut_phase + phase_increment;
        i = i + 1;
    }
}
```

## Advanced Lookup Techniques

### Interpolated Lookup Tables
```impala

global int WAVE_TABLE_SIZE = 512;
global array wavetable[512];


function interpolatedLookup(int phase) returns int result {
    int index = phase >> 16;
    int fraction = phase & 0xFFFF;
    
    int sample1 = wavetable[index & (WAVE_TABLE_SIZE - 1)];
    int sample2 = wavetable[(index + 1) & (WAVE_TABLE_SIZE - 1)];
    

    result = sample1 + ((sample2 - sample1) * fraction >> 16);
}
```

### Saturation/Waveshaping Table
```impala

global int SATURATION_TABLE_SIZE = 2048;
global array saturation_table[2048];

function initializeSaturationTable() {
    int i = 0;
    loop {
        if (i >= SATURATION_TABLE_SIZE) break;

        int input = (i - SATURATION_TABLE_SIZE/2) * 4;
        
        int output;

        if (input > 1500) {
            output = 1500 + (input - 1500) * 0.3;
        } else if (input < -1500) {
            output = -1500 + (input + 1500) * 0.3;
        } else {
            output = input;
        }
        
        saturation_table[i] = clamp(output, -2047, 2047);
        i = i + 1;
    }
}


function operate2() {
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;

        int index = (signal[i] + 2047) >> 1;
        signal[i] = saturation_table[clamp(index, 0, SATURATION_TABLE_SIZE-1)];
        i = i + 1;
    }
}
```

## Memory-Efficient Multi-Function Tables

### Combined Waveform Table
```impala

global int WAVEFORMS = 4;
global int TABLE_SIZE = 256;
global int TOTAL_TABLE_SIZE = 1024;
global array wave_table[1024];
global int multi_phase = 0;

function initializeWaveTable() {
    int wave = 0;
    loop {
        if (wave >= WAVEFORMS) break;
        int offset = wave * TABLE_SIZE;
        
        int i = 0;
        loop {
            if (i >= TABLE_SIZE) break;
            float phase = (i * TWO_PI) / TABLE_SIZE;
            
            if (wave == 0) {
                wave_table[offset + i] = sine(phase) * 2000;
            } else if (wave == 1) {
                wave_table[offset + i] = triangleWave(phase);
            } else if (wave == 2) {
                wave_table[offset + i] = sawWave(phase);
            } else if (wave == 3) {
                wave_table[offset + i] = squareWave(phase);
            }
            i = i + 1;
        }
        wave = wave + 1;
    }
}


function operate1() {
    int waveform = (int)global params[CLOCK_FREQ_PARAM_INDEX] >> 5;
    int table_offset = waveform * TABLE_SIZE;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        int index = (multi_phase >> 8) & (TABLE_SIZE - 1);
        signal[i] = wave_table[table_offset + index];
        multi_phase = multi_phase + frequency_increment;
        i = i + 1;
    }
}
```

## Real-World Example: Exponential Envelope

```impala

global int ENVELOPE_TABLE_SIZE = 1024;
global array envelope_table[1024];
global int envelope_phase = 0;
global int gate_triggered = 0;

function initializeEnvelopeTable() {
    int i = 0;
    loop {
        if (i >= ENVELOPE_TABLE_SIZE) break;

        float t = i / ENVELOPE_TABLE_SIZE;
        envelope_table[i] = exp(-t * 8) * 2047;
        i = i + 1;
    }
}


function operate2() {
    int attack_time = (int)global params[CLOCK_FREQ_PARAM_INDEX] * 10;
    int decay_time = (int)global params[SWITCHES_PARAM_INDEX] * 10;
    
    int i = 0;
    loop {
        if (i >= BLOCK_SIZE) break;
        if (gate_triggered != 0) {
            envelope_phase = 0;
        }
        
        int envelope;
        if (envelope_phase < attack_time) {

            envelope = (envelope_phase * 2047) / attack_time;
        } else {

            int decay_phase = envelope_phase - attack_time;
            int table_index = (decay_phase * ENVELOPE_TABLE_SIZE) / decay_time;
            envelope = envelope_table[clamp(table_index, 0, ENVELOPE_TABLE_SIZE-1)];
        }
        
        signal[i] = (signal[i] * envelope) >> 11;
        envelope_phase = envelope_phase + 1;
        i = i + 1;
    }
}
```

## Implementation Guidelines

**Optimal table sizes:**
- Powers of 2 (256, 512, 1024) for efficient indexing
- Balance memory usage vs. accuracy
- 8-bit tables for rough approximations
- 16-bit tables for high-quality audio

**Best candidates for lookup tables:**
- Periodic functions (sine, triangle, sawtooth)
- Non-linear transformations (saturation, compression)
- Envelope shapes (exponential, logarithmic)
- Filter coefficient calculations

**Memory considerations:**
- Store tables in program memory when possible
- Use shared tables for common functions
- Consider table compression for space-critical applications

Lookup tables typically provide 10-50x performance improvements for mathematical functions while using minimal additional memory (1-4KB for most audio applications).