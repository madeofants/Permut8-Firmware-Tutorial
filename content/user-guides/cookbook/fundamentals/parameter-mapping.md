# Parameter Mapping

*Convert knob values into useful parameter ranges*

## What This Does

Parameter mapping transforms raw operand values (0-255) into meaningful ranges for your audio algorithms. Good mapping makes controls feel natural and musical instead of awkward or unusable.

## Permut8 Parameter Interface Architecture

### **Understanding the Interface System**

**Original Permut8 Interface:**
- **Instruction 1**: High Operand (`params[OPERAND_1_HIGH_PARAM_INDEX]`) + Low Operand (`params[OPERAND_1_LOW_PARAM_INDEX]`)
- **Instruction 2**: High Operand (`params[OPERAND_2_HIGH_PARAM_INDEX]`) + Low Operand (`params[OPERAND_2_LOW_PARAM_INDEX]`)
- **User Control**: Scrollable LED displays + bit switches (8 switches per operand)
- **Display**: Each operand shows as hex value (00-FF) representing 0-255

**Custom Firmware Override:**
- **Transform**: Convert operand parameters into direct knob controls
- **Interface**: `panelTextRows` replaces hex displays with custom labels
- **Experience**: Same parameter data, intuitive user interface

### **Data Flow Example**
```impala










int cutoff_freq = ((int)params[OPERAND_1_HIGH_PARAM_INDEX] * 8000) / 255;



displayLEDs[0] = params[OPERAND_1_HIGH_PARAM_INDEX];
```

### **panelTextRows Layout System**
```impala
readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "FILTER |-- CUTOFF --| |-- RESO --|",
    "",
    "",
    "",
    "EFFECT |-- MIX -----| |-- GAIN --|"
};




```

## Quick Reference

**Essential Parameters:**
- `params[OPERAND_1_HIGH_PARAM_INDEX,OPERAND_1_LOW_PARAM_INDEX,OPERAND_2_HIGH_PARAM_INDEX,OPERAND_2_LOW_PARAM_INDEX]`: Instruction operand values (0-255)
- `params[CLOCK_FREQ_PARAM_INDEX]`: Clock frequency (system controlled)
- `params[SWITCHES_PARAM_INDEX]`: Switch states (bitmask)
- `target_range`: Your algorithm's useful range (often 0-AUDIO_MAX)
- `smoothing`: Prevents parameter clicks during changes

**Common Mappings:**
- **Mix controls**: Linear scaling (equal steps feel natural)
- **Frequency**: Logarithmic scaling (matches musical perception)
- **Gain**: Square-law or exponential scaling
- **Time**: Linear for short delays, logarithmic for long delays

**Key Concepts:** Range scaling, parameter smoothing, curve shaping, musical response

## Complete Code

```impala



const int PARAM_MAX = 255
const int PARAM_MIN = 0
const int PARAM_MID = 128
const int PARAM_SWITCH_THRESHOLD = 127


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int AUDIO_ZERO = 0


const int SAMPLE_RATE_44K1 = 44100
const int SAMPLE_RATE_HALF = 22050
const int SAMPLE_RATE_QUARTER = 11025


const int AUDIO_FULL_RANGE = 65536
const int AUDIO_HALF_RANGE = 32768
const int AUDIO_QUARTER_RANGE = 16384


const float PI = 3.14159265
const float TWO_PI = 6.28318531
const float PI_OVER_2 = 1.57079633


const int SMALL_BUFFER = 128
const int MEDIUM_BUFFER = 512
const int LARGE_BUFFER = 1024
const int MAX_BUFFER = 2048


const int BITS_PER_BYTE = 8
const int SHIFT_DIVIDE_BY_2 = 1
const int SHIFT_DIVIDE_BY_4 = 2
const int SHIFT_DIVIDE_BY_8 = 3


const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_DOUBLE = 0x03
const int LED_QUAD = 0x0F
const int LED_BRIGHTNESS_FULL = 255
const int LED_BRIGHTNESS_HALF = 127


const int STANDARD_BPM = 120
const int QUARTER_NOTE_DIVISIONS = 4
const int SEMITONES_PER_OCTAVE = 12
const float A4_FREQUENCY = 440.0

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


extern native yield


global int clock
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit


global int smooth_cutoff = 1000
global int smooth_resonance = 512
global int smooth_mix = 1024

function process()
locals int cutoff_target, int resonance_target, int mix_target, int filtered_signal, int dry_signal, int wet_signal, int output
{
    loop {

        mix_target = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 3);
        

        cutoff_target = 200 + (((int)global params[SWITCHES_PARAM_INDEX] * (int)global params[SWITCHES_PARAM_INDEX]) >> 4);
        if (cutoff_target > 2000) cutoff_target = 2000;
        

        resonance_target = 256 + (((int)global params[OPERATOR_1_PARAM_INDEX] * 1536) >> 8);
        

        global smooth_cutoff = global smooth_cutoff + ((cutoff_target - global smooth_cutoff) >> 4);
        global smooth_resonance = global smooth_resonance + ((resonance_target - global smooth_resonance) >> 4);
        global smooth_mix = global smooth_mix + ((mix_target - global smooth_mix) >> 4);
        

        dry_signal = (int)global signal[0];
        

        filtered_signal = global smooth_cutoff + 
            (((dry_signal - global smooth_cutoff) * global smooth_resonance) >> 11);
        

        if (filtered_signal > AUDIO_MAX) filtered_signal = AUDIO_MAX;
        if (filtered_signal < AUDIO_MIN) filtered_signal = AUDIO_MIN;
        

        wet_signal = (filtered_signal * global smooth_mix) >> 11;
        output = dry_signal + wet_signal;
        

        if (output > AUDIO_MAX) output = AUDIO_MAX;
        if (output < AUDIO_MIN) output = AUDIO_MIN;
        

        global signal[0] = output;
        global signal[1] = output;
        

        global displayLEDs[0] = global smooth_cutoff >> 3;
        global displayLEDs[1] = global smooth_resonance >> 3;
        global displayLEDs[2] = global smooth_mix >> 3;
        global displayLEDs[3] = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        
        yield();
    }
}
```

## How It Works

**Linear Mapping**: Simplest scaling where equal knob movements create equal parameter changes. Good for mix controls and balance.

**Exponential Mapping**: Using squared values creates more natural feeling controls for frequency and gain parameters.

**Parameter Smoothing**: Prevents clicks and zipper noise by gradually changing values instead of jumping immediately.

**Range Mapping**: Converting 0-255 knob values into useful ranges like 200-2000 for filter cutoff frequencies.

**Parameter Control**:
- **Control 1**: Mix level (0-255 → 0-2040 linear mapping)
- **Control 2**: Cutoff frequency (0-255 → 200-2000 exponential mapping)  
- **Control 3**: Resonance (0-255 → 256-1792 linear with offset)

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = PARAM_MID;
global params[SWITCHES_PARAM_INDEX] = 100;
global params[OPERATOR_1_PARAM_INDEX] = 80;


global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 200;
global params[OPERATOR_1_PARAM_INDEX] = 60;


global params[CLOCK_FREQ_PARAM_INDEX] = 80;
global params[SWITCHES_PARAM_INDEX] = 50;
global params[OPERATOR_1_PARAM_INDEX] = 150;


global params[CLOCK_FREQ_PARAM_INDEX] = 255;
global params[SWITCHES_PARAM_INDEX] = 255;
global params[OPERATOR_1_PARAM_INDEX] = 200;
```

## Understanding Parameter Curves

**Linear Response**: Equal knob steps = equal parameter steps. Good for mix controls and panning.

**Exponential Response**: Using squared values gives more control at low values, faster changes at high values. Good for frequencies and gain.

**Smoothing**: Gradual parameter changes prevent audio clicks. Faster smoothing for quick response, slower for smooth changes.

**Range Mapping**: Converting knob ranges (0-255) to useful parameter ranges (like 200-2000 Hz) with proper scaling.

## Try These Changes

- **Custom curves**: Create lookup tables for specific parameter responses
- **Multi-parameter control**: Control several parameters with one knob
- **Quantized mapping**: Snap parameters to musical steps (notes, rhythms)
- **Linked parameters**: Make parameters automatically adjust based on others

## Related Techniques

- **[Basic Filter](basic-filter.md)**: Apply parameter mapping to filter controls
- **[Envelope Basics](envelope-basics.md)**: Map time parameters naturally

---
*Part of the [Permut8 Cookbook](../index.md) series*