# Bitcrusher

*Create digital distortion effects through bit depth reduction and sample rate downsampling*

## What This Does

Generates digital distortion by reducing the bit depth and sample rate of audio signals, creating characteristic lo-fi artifacts, digital stepping, and harmonic distortion. Perfect for vintage sampler emulation and modern digital textures.

### **Approach: Custom Firmware (Direct Processing)**

This recipe demonstrates **Approach 2: Custom Firmware** - completely bypassing Permut8's delay memory system to process audio samples directly with bit manipulation algorithms.

**Why This Approach?**:
- **Bit crushing** requires sample-by-sample mathematical processing
- **Direct control** over quantization and sample rate algorithms  
- **Custom interface** needed for intuitive bit depth and rate controls
- **Real-time processing** without delay memory dependencies

**Alternative Approaches**:
- **Original operators**: Could use AND operator for bit masking, but lacks sample rate control
- **Operator modification**: Could enhance AND operator, but custom firmware provides better control

### **Interface Architecture**

This effect uses all four instruction operands as custom knob controls:

**Original Interface**: Each operand controlled via scrollable LED displays + bit switches  
**Custom Firmware**: Direct knob controls with custom labels via `panelTextRows`

**Suggested Panel Layout**:
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

readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "CRUSH |-- BIT DEPTH --| |--- DRY/WET ---|",
    "",
    "",
    "",
    "CRUSH |-- RATE DIV ---| |--- GAIN -----|")
};

```

## Quick Reference

**Essential Parameters:**
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Bit depth (Instruction 1 High Operand, 0-255, controls quantization amount)
- `params[OPERAND_1_LOW_PARAM_INDEX]`: Sample rate reduction (Instruction 1 Low Operand, 0-255, hold factor) 
- `params[OPERAND_2_HIGH_PARAM_INDEX]`: Dry/wet mix (Instruction 2 High Operand, 0-255, blend control)
- `params[OPERAND_2_LOW_PARAM_INDEX]`: Output gain (Instruction 2 Low Operand, 0-255, level compensation)

**Key Concepts:** Quantization distortion, sample-and-hold, digital artifacts, aliasing effects

**Common Settings:**
```impala

vintage_bits = 180; vintage_rate = 60; vintage_mix = 200; vintage_gain = 220;


lofi_bits = 100; lofi_rate = 120; lofi_mix = 180; lofi_gain = 240;


extreme_bits = 30; extreme_rate = 200; extreme_mix = 255; extreme_gain = 200;
```

## Complete Code

```impala
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


global int hold_left = 0
global int hold_right = 0
global int hold_counter = 0

function process()
locals int bits, int rate_div, int mix, int gain, int crushed_left, int crushed_right, int shift_amount, int dry_left, int dry_right, int wet_left, int wet_right, int output_left, int output_right
{
    loop {

        bits = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 4) + 1;
        rate_div = ((int)global params[OPERAND_1_LOW_PARAM_INDEX] >> 3) + 1;
        mix = (int)global params[OPERAND_2_HIGH_PARAM_INDEX];
        gain = ((int)global params[OPERAND_2_LOW_PARAM_INDEX] >> 1) + 64;
        

        global hold_counter = global hold_counter + 1;
        if (global hold_counter >= rate_div) {
            global hold_counter = 0;
            global hold_left = (int)global signal[0];
            global hold_right = (int)global signal[1];
        }
        

        shift_amount = 12 - bits;
        if (shift_amount < 0) shift_amount = 0;
        if (shift_amount > 11) shift_amount = 11;
        

        crushed_left = (global hold_left >> shift_amount) << shift_amount;
        crushed_right = (global hold_right >> shift_amount) << shift_amount;
        

        dry_left = (int)global signal[0];
        dry_right = (int)global signal[1];
        

        wet_left = (crushed_left * gain) >> 7;
        wet_right = (crushed_right * gain) >> 7;
        

        if (wet_left > 2047) wet_left = 2047;
        if (wet_left < -2047) wet_left = -2047;
        if (wet_right > 2047) wet_right = 2047;
        if (wet_right < -2047) wet_right = -2047;
        

        output_left = ((dry_left * (255 - mix)) + (wet_left * mix)) >> 8;
        output_right = ((dry_right * (255 - mix)) + (wet_right * mix)) >> 8;
        

        global signal[0] = output_left;
        global signal[1] = output_right;
        

        global displayLEDs[0] = ((bits - 1) << 4) & 255;
        global displayLEDs[1] = ((rate_div - 1) << 3) & 255;
        global displayLEDs[2] = mix;
        global displayLEDs[3] = (gain - 64) << 1;
        
        yield();
    }
}
```

## How It Works

**Bit Depth Reduction**: Uses right-shift quantization to reduce effective bit depth from 12-bit to 1-16 bits, creating digital stepping artifacts.

**Sample Rate Reduction**: Holds samples for multiple cycles (1-32x), creating characteristic stepping and aliasing effects.

**Dry/Wet Mixing**: Blends original signal with crushed signal for controlled intensity.

**Output Gain**: Compensates for level changes caused by bit reduction and provides creative gain staging.

**Parameter Control**:
- **Control 1**: Bit depth (1-16 effective bits) 
- **Control 2**: Sample rate reduction (1-32x)
- **Control 3**: Dry/wet mix (0% = clean, 100% = crushed)
- **Control 4**: Output gain (compensate for level changes)

**LED Feedback**: Shows bit depth, rate reduction, mix level, and output gain.

## Try These Settings

```impala

global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;
global params[OPERAND_1_LOW_PARAM_INDEX] = 64;
global params[OPERAND_2_HIGH_PARAM_INDEX] = 180;
global params[OPERAND_2_LOW_PARAM_INDEX] = 200;


global params[OPERAND_1_HIGH_PARAM_INDEX] = 32;
global params[OPERAND_1_LOW_PARAM_INDEX] = 200;
global params[OPERAND_2_HIGH_PARAM_INDEX] = 255;
global params[OPERAND_2_LOW_PARAM_INDEX] = 255;
```
