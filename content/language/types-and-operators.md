# Types and Operators - Data Types in Permut8 Firmware

Understanding Impala's data types and operators is essential for efficient audio processing. Permut8 firmware works with integers, arrays, and specialized operations designed for real-time DSP performance.

## Basic Data Types

### Integer Type

All audio samples and most calculations use signed integers:

```impala
int sample = -1024          // Audio sample (-2047 to 2047)
int param = 127             // Parameter value (0 to 255)
int position = 0x80000      // 20-bit position value
```

**Key Range**: Audio samples range from -2047 to 2047, giving you 12-bit signed audio with plenty of headroom for calculations.

### Boolean Type

Use for control logic and state flags:

```impala
int gate_open = 1                    // Use 1 for true, 0 for false
int effect_bypass = 0
// CORRECT: Always use parameter constants
if ((int)global params[OPERAND_2_LOW_PARAM_INDEX] > 128) effect_bypass = 1;

if (gate_open && (effect_bypass == 0)) {
    // Process audio
}
```

### Array Types

Fixed-size arrays for buffers and lookup tables:

```impala
// Standard global arrays (required)
global int clock = 0
global array params[PARAM_COUNT]
global array displayLEDs[4]
global array signal[2]

// Custom arrays for your firmware
global array delay_line[1024]               // 1024-sample delay buffer
global array sine_table[256]                // Lookup table for oscillator
global array coefficients[8] = {64, 32, 16, 8, 4, 2, 1, 1}  // Filter coefficients
```

## Fixed-Point Arithmetic

### Position Values (20-bit)

Positions use 16.4 fixed-point format (16 integer bits, 4 fractional bits):

```impala
int base_pos = 0x10000      // Position 1.0
int half_pos = 0x08000      // Position 0.5
int quarter = 0x04000       // Position 0.25

// Extract integer part
int sample_index = position >> 4

// Extract fractional part for interpolation
int frac = position & 0xF
```

### Parameter Scaling

Convert 8-bit parameters to useful ranges:

```impala
// Scale parameter (0-255) to full audio range
int gain = params[0] * 2047 / 255

// Scale to frequency range (0-4000 Hz equivalent)
int frequency = params[1] * 4000 / 255

// Scale to feedback amount (-128 to +127)
int feedback = params[2] - 128
```

## Bitwise Operations

### Efficient Calculations

Use bit operations for fast arithmetic:

```impala
// Fast division by powers of 2
int half_sample = input >> 1        // Divide by 2
int quarter = input >> 2            // Divide by 4
int eighth = input >> 3             // Divide by 8

// Fast multiplication by powers of 2
int doubled = input << 1            // Multiply by 2
int quadrupled = input << 2         // Multiply by 4

// Wraparound using bit masks (for buffer sizes that are powers of 2)
int next_pos = (current_pos + 1) & 1023  // Wrap at 1024
```

### Bit Manipulation for Control

Extract and combine multiple values efficiently:

```impala
// Pack two 8-bit values into one int
int packed = (high_byte << 8) | low_byte

// Extract values back
int high = (packed >> 8) & 0xFF
int low = packed & 0xFF

// Set individual bits for LED control
int led_pattern = 0
led_pattern |= (1 << 3)   // Turn on LED 3
led_pattern &= ~(1 << 1)  // Turn off LED 1
```

## Array Operations

### Safe Array Access

Use modulo or bit masking to prevent buffer overruns:

```impala
global array buffer[512]
global int pos = 0

// Safe access with modulo
buffer[pos % 512] = input

// Faster access with bit mask (buffer size must be power of 2)
buffer[pos & 511] = input
pos = (pos + 1) & 511
```

### Linear Interpolation

Smooth array lookups for high-quality audio:

```impala
function interpolate_lookup(array table[256], int position) returns int result {
    int index = position >> 8          // Integer part
    int frac = position & 0xFF         // Fractional part
    
    int sample1 = table[index & 255]
    int sample2 = table[(index + 1) & 255]
    
    // Linear interpolation
    result = sample1 + ((sample2 - sample1) * frac / 256)
}
```

## Arithmetic Operators

### Audio-Safe Math

Prevent overflow in audio calculations:

```impala
// Safe addition with saturation
function add_saturate(int a, int b) returns int result {
    result = a + b
    if (result > 2047) result = 2047
    if (result < -2047) result = -2047
}

// Safe multiplication with scaling
function multiply_audio(int sample, int gain) returns int result {
    result = (sample * gain) >> 8  // Assume gain is 8-bit (0-255)
}
```

### Comparison and Logic

```impala
// Threshold detection
int above_threshold = 0
if (abs(input) > noise_floor) above_threshold = 1

// Range checking
int in_range = 0
if ((param >= min_val) && (param <= max_val)) in_range = 1

// Conditional assignment
int output = input  // Default value
if (bypass == 0) output = process_effect(input)
```

Understanding these types and operators helps you write efficient, reliable audio processing code that makes full use of Permut8's capabilities while maintaining real-time performance.
