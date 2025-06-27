# Types and Operators - Data Types in Permut8 Firmware

Understanding Impala's data types and operators is essential for efficient audio processing. Permut8 firmware works with integers, arrays, and specialized operations designed for real-time DSP performance.

## Basic Data Types

### Integer Type

All audio samples and most calculations use signed integers:

```impala
int sample = -1024
int param = 127
int position = 0x80000
```

**Key Range**: Audio samples range from -2047 to 2047, giving you 12-bit signed audio with plenty of headroom for calculations.

### Boolean Type

Use for control logic and state flags:

```impala
int gate_open = 1
int effect_bypass = 0

if ((int)global params[OPERAND_2_LOW_PARAM_INDEX] > 128) effect_bypass = 1;

if (gate_open && (effect_bypass == 0)) {

}
```

### Array Types

Fixed-size arrays for buffers and lookup tables:

```impala

global int clock = 0
global array params[PARAM_COUNT]
global array displayLEDs[4]
global array signal[2]


global array delay_line[1024]
global array sine_table[256]
global array coefficients[8] = {64, 32, 16, 8, 4, 2, 1, 1}
```

## Fixed-Point Arithmetic

### Position Values (20-bit)

Positions use 16.4 fixed-point format (16 integer bits, 4 fractional bits):

```impala
int base_pos = 0x10000
int half_pos = 0x08000
int quarter = 0x04000


int sample_index = position >> 4


int frac = position & 0xF
```

### Parameter Scaling

Convert 8-bit parameters to useful ranges:

```impala

int gain = params[0] * 2047 / 255


int frequency = params[1] * 4000 / 255


int feedback = params[2] - 128
```

## Bitwise Operations

### Efficient Calculations

Use bit operations for fast arithmetic:

```impala

int half_sample = input >> 1
int quarter = input >> 2
int eighth = input >> 3


int doubled = input << 1
int quadrupled = input << 2


int next_pos = (current_pos + 1) & 1023
```

### Bit Manipulation for Control

Extract and combine multiple values efficiently:

```impala

int packed = (high_byte << 8) | low_byte


int high = (packed >> 8) & 0xFF
int low = packed & 0xFF


int led_pattern = 0
led_pattern |= (1 << 3)
led_pattern &= ~(1 << 1)
```

## Array Operations

### Safe Array Access

Use modulo or bit masking to prevent buffer overruns:

```impala
global array buffer[512]
global int pos = 0


buffer[pos % 512] = input


buffer[pos & 511] = input
pos = (pos + 1) & 511
```

### Linear Interpolation

Smooth array lookups for high-quality audio:

```impala
function interpolate_lookup(array table[256], int position) returns int result {
    int index = position >> 8
    int frac = position & 0xFF
    
    int sample1 = table[index & 255]
    int sample2 = table[(index + 1) & 255]
    

    result = sample1 + ((sample2 - sample1) * frac / 256)
}
```

## Arithmetic Operators

### Audio-Safe Math

Prevent overflow in audio calculations:

```impala

function add_saturate(int a, int b) returns int result {
    result = a + b
    if (result > 2047) result = 2047
    if (result < -2047) result = -2047
}


function multiply_audio(int sample, int gain) returns int result {
    result = (sample * gain) >> 8
}
```

### Comparison and Logic

```impala

int above_threshold = 0
if (abs(input) > noise_floor) above_threshold = 1


int in_range = 0
if ((param >= min_val) && (param <= max_val)) in_range = 1


int output = input
if (bypass == 0) output = process_effect(input)
```

Understanding these types and operators helps you write efficient, reliable audio processing code that makes full use of Permut8's capabilities while maintaining real-time performance.
