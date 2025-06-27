# Multi-Band Compressor

*Split audio into frequency bands and compress each independently*

## What This Does

Creates a simple 2-band compressor that splits audio into low and high frequencies and applies different compression to each band. This allows for more precise dynamic control - for example, compressing bass heavily while leaving highs untouched.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Low band threshold (0-255, bass compression level)
- `params[SWITCHES_PARAM_INDEX]`: High band threshold (0-255, treble compression level)
- `params[OPERATOR_1_PARAM_INDEX]`: Crossover frequency (0-255, where to split bass/treble)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Output gain (0-255, level compensation)

**Key Concepts:** Frequency splitting, independent compression, band recombination

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


global int low_envelope = 0
global int high_envelope = 0
global int low_gain = 255
global int high_gain = 255
global int filter_state = 0

function process()
locals int crossover, int low_thresh, int high_thresh, int output_gain, int input, int low_band, int high_band, int compressed_low, int compressed_high, int output, int low_level, int high_level, int overage, int target_gain
{
    loop {

        low_thresh = ((int)global params[CLOCK_FREQ_PARAM_INDEX] << 3) + 512;
        high_thresh = ((int)global params[SWITCHES_PARAM_INDEX] << 3) + 512;
        crossover = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 4) + 1;
        output_gain = ((int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 1) + 128;
        
        input = (int)global signal[0];
        


        global filter_state = global filter_state + ((input - global filter_state) >> crossover);
        low_band = global filter_state;
        

        high_band = input - low_band;
        

        low_level = low_band;
        if (low_level < 0) low_level = -low_level;
        if (low_level > global low_envelope) {
            global low_envelope = global low_envelope + ((low_level - global low_envelope) >> 2);
        } else {
            global low_envelope = global low_envelope + ((low_level - global low_envelope) >> 4);
        }
        
        high_level = high_band;
        if (high_level < 0) high_level = -high_level;
        if (high_level > global high_envelope) {
            global high_envelope = global high_envelope + ((high_level - global high_envelope) >> 2);
        } else {
            global high_envelope = global high_envelope + ((high_level - global high_envelope) >> 4);
        }
        

        if (global low_envelope > low_thresh) {
            overage = global low_envelope - low_thresh;
            target_gain = 255 - (overage >> 3);
            if (target_gain < 128) target_gain = 128;
            
            if (target_gain < global low_gain) {
                global low_gain = global low_gain - ((global low_gain - target_gain) >> 2);
            } else {
                global low_gain = global low_gain + ((target_gain - global low_gain) >> 4);
            }
        } else {
            global low_gain = global low_gain + ((255 - global low_gain) >> 4);
        }
        

        if (global high_envelope > high_thresh) {
            overage = global high_envelope - high_thresh;
            target_gain = 255 - (overage >> 3);
            if (target_gain < 128) target_gain = 128;
            
            if (target_gain < global high_gain) {
                global high_gain = global high_gain - ((global high_gain - target_gain) >> 2);
            } else {
                global high_gain = global high_gain + ((target_gain - global high_gain) >> 4);
            }
        } else {
            global high_gain = global high_gain + ((255 - global high_gain) >> 4);
        }
        

        compressed_low = (low_band * global low_gain) >> 8;
        compressed_high = (high_band * global high_gain) >> 8;
        

        output = compressed_low + compressed_high;
        

        output = (output * output_gain) >> 8;
        

        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        

        global signal[0] = output;
        global signal[1] = output;
        

        global displayLEDs[0] = 255 - global low_gain;
        global displayLEDs[1] = 255 - global high_gain;
        global displayLEDs[2] = global low_envelope >> 3;
        global displayLEDs[3] = global high_envelope >> 3;
        
        yield();
    }
}

```

## How It Works

**Frequency Splitting**: Uses a simple one-pole low-pass filter to separate bass from treble.

**Independent Compression**: Each band has its own envelope follower and gain reduction.

**Band Recombination**: Compressed bands are simply added back together.

**Parameter Control**:
- **Control 1**: Low band threshold (higher = less bass compression)
- **Control 2**: High band threshold (higher = less treble compression)
- **Control 3**: Crossover frequency (higher = more bass in low band)
- **Control 4**: Output gain (compensate for compression)

**LED Feedback**: Shows gain reduction and levels for both bands.

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 100;
global params[SWITCHES_PARAM_INDEX] = 200;
global params[OPERATOR_1_PARAM_INDEX] = 128;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;


global params[CLOCK_FREQ_PARAM_INDEX] = 180;
global params[SWITCHES_PARAM_INDEX] = 180;
global params[OPERATOR_1_PARAM_INDEX] = 128;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 160;
```

## Try These Changes

- **Three-band**: Add a mid-band between low and high
- **Different ratios**: Use different compression ratios for each band
- **Stereo processing**: Process left and right channels independently
- **Better crossovers**: Implement steeper filter slopes

## Related Techniques

- **[Basic Compressor](compressor-basic.md)**: Single-band compression fundamentals
- **[Basic Filter](../fundamentals/basic-filter.md)**: Filter implementation basics

---
*Part of the [Permut8 Cookbook](../index.md) series*