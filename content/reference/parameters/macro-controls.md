# Macro Controls

*Control multiple parameters simultaneously with single knobs for expressive musical performance*

## What This Does

Allows a single knob to control multiple parameters with custom relationships. Transforms technical parameter adjustments into intuitive musical gestures like "brightness," "drive," and "space."

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Brightness macro (filter + tone)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Drive macro (distortion + gain)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Space macro (reverb + delay)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Energy macro (levels + speed)

**Core Techniques:**
- **Multi-parameter mapping**: One knob controls several values
- **Curve shaping**: Linear, exponential, inverted responses
- **Musical gestures**: Intuitive control groupings
- **Parameter relationships**: Complementary parameter changes

**Key Concepts:** Macro mapping, parameter curves, musical intuition, expressive control

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


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]


global int brightness_level = 128
global int drive_level = 0
global int space_level = 0
global int energy_level = 128

function process()
locals int brightness_macro, int drive_macro, int space_macro, int energy_macro, int filter_cutoff, int filter_resonance, int distortion_gain, int reverb_mix, int energy_level, int input_sample, int filtered_sample, int driven_sample, int spatial_sample, int output_sample
{
    loop {

        brightness_macro = (int)global (int)global params[CLOCK_FREQ_PARAM_INDEX];
        drive_macro = (int)global (int)global params[SWITCHES_PARAM_INDEX];
        space_macro = (int)global (int)global params[OPERATOR_1_PARAM_INDEX];
        energy_macro = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        


        filter_cutoff = 200 + ((brightness_macro * 1800) >> 8);
        filter_resonance = 256 + ((brightness_macro * 1024) >> 8);
        



        distortion_gain = (drive_macro * drive_macro) >> 8;
        if (distortion_gain < 128) distortion_gain = 128;
        


        reverb_mix = (space_macro * 180) >> 8;
        


        energy_level = 512 + ((energy_macro * 1536) >> 8);
        

        

        input_sample = (int)global signal[0];
        

        filtered_sample = filter_cutoff + 
            (((input_sample - filter_cutoff) * filter_resonance) >> 11);
        

        if (filtered_sample > 2047) filtered_sample = 2047;
        if (filtered_sample < -2047) filtered_sample = -2047;
        

        driven_sample = (filtered_sample * distortion_gain) >> 8;
        if (driven_sample > 1536) {
            driven_sample = 1536 + ((driven_sample - 1536) >> 2);
        }
        if (driven_sample < -1536) {
            driven_sample = -1536 + ((driven_sample + 1536) >> 2);
        }
        

        spatial_sample = driven_sample + 
            (((driven_sample >> 2) * reverb_mix) >> 8);
        

        output_sample = (spatial_sample * energy_level) >> 10;
        

        if (output_sample > 2047) output_sample = 2047;
        if (output_sample < -2047) output_sample = -2047;
        

        global signal[0] = output_sample;
        global signal[1] = output_sample;
        

        global displayLEDs[0] = brightness_macro;
        global displayLEDs[1] = drive_macro;
        global displayLEDs[2] = space_macro;
        global displayLEDs[3] = energy_macro;
        
        yield();
    }
}

```

## How It Works

**Brightness Macro**: Controls filter cutoff and resonance together. Higher values = brighter, more resonant sound.

**Drive Macro**: Uses exponential curve for natural distortion feel. Controls pre-gain and soft limiting together.

**Space Macro**: Controls reverb/delay mix amount. Creates sense of acoustic space and depth.

**Energy Macro**: Final level and dynamics control. Sets overall energy and impact of the sound.

**Parameter Control**:
- **Knob 1**: Brightness (filter cutoff + resonance)
- **Knob 2**: Drive (distortion gain + saturation) 
- **Knob 3**: Space (reverb mix + spatial effects)
- **Knob 4**: Energy (levels + dynamics)

## Try These Settings

```impala

(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;
(int)global params[SWITCHES_PARAM_INDEX] = 64;
(int)global params[OPERATOR_1_PARAM_INDEX] = 80;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 80;
(int)global params[SWITCHES_PARAM_INDEX] = 180;
(int)global params[OPERATOR_1_PARAM_INDEX] = 120;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 120;
(int)global params[SWITCHES_PARAM_INDEX] = 100;
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 100;


(int)global params[CLOCK_FREQ_PARAM_INDEX] = 255;
(int)global params[SWITCHES_PARAM_INDEX] = 255;
(int)global params[OPERATOR_1_PARAM_INDEX] = 50;
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 255;
```

## Understanding Macro Controls

**Musical Intuition**: Group related parameters so users think musically, not technically.

**Parameter Curves**: Linear curves feel technical. Exponential/logarithmic curves feel more natural.

**Complementary Controls**: Some parameters should increase while others decrease for musical balance.

**Performance Oriented**: Design macros for real-time performance and expression.

## Try These Changes

- **Custom curves**: Add S-curves, inverted responses, or stepped mappings
- **Bipolar controls**: Center position = neutral, extremes = opposite effects
- **Cross-parameter coupling**: One macro affects the response of another
- **Tempo-synced macros**: Sync parameter changes to musical timing

## Related Techniques

- **[Parameter Smoothing](parameter-smoothing.md)**: Add smoothing to macro controls
- **[Read Knobs](read-knobs.md)**: Basic parameter reading for macro inputs
- **[Parameter Mapping](../fundamentals/parameter-mapping.md)**: Advanced parameter scaling

---
*Part of the [Permut8 Cookbook](../index.md) series*