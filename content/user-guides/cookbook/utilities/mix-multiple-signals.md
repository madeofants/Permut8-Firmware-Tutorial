# Mix Multiple Signals

*Combine multiple audio sources with proper level management and headroom control*

## What This Does

Provides efficient multi-signal mixing techniques for combining oscillators, effects returns, or layered sounds. Essential for preventing clipping while maintaining good signal-to-noise ratios in complex patches.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Input 1 level (0-255)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Input 2 level (0-255) 
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Input 3 level (0-255)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Master level (0-255)

**Core Techniques:**
- **Signal summing**: Linear addition of multiple sources
- **Level balancing**: Individual input gain control
- **Headroom management**: Prevent clipping with proper scaling
- **Master control**: Final output level adjustment

**Key Concepts:** Signal summing, headroom management, gain staging, clipping prevention

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


global int phase1 = 0
global int phase2 = 0
global int noise_seed = 12345
global int mix_buffer = 0

function process()
locals input1_level, input2_level, input3_level, master_level, signal1, signal2, signal3, external_input, input1_scaled, input2_scaled, input3_scaled, external_scaled, mixed_output
{
    loop {

        input1_level = params[CLOCK_FREQ_PARAM_INDEX];
        input2_level = params[SWITCHES_PARAM_INDEX];
        input3_level = params[OPERATOR_1_PARAM_INDEX];
        master_level = params[OPERAND_1_HIGH_PARAM_INDEX];
        


        global phase1 = global phase1 + (input1_level + 32);
        if (global phase1 >= 2048) global phase1 = global phase1 - 2048;
        
        if (global phase1 < 512) {
            signal1 = (global phase1 << 2);
        } else if (global phase1 < 1536) {
            signal1 = 2047 - ((global phase1 - 512) << 1);
        } else {
            signal1 = -2047 + ((global phase1 - 1536) << 2);
        }
        

        global phase2 = global phase2 + (input2_level + 16);
        if (global phase2 >= 2048) global phase2 = global phase2 - 2048;
        signal2 = global phase2 - 1024;
        

        global noise_seed = (global noise_seed * 1103515245 + 12345) & 0x7FFFFFFF;
        signal3 = (global noise_seed >> 16) - 1024;
        

        external_input = signal[0];
        

        input1_scaled = (signal1 * input1_level) >> 8;
        input2_scaled = (signal2 * input2_level) >> 8;
        input3_scaled = (signal3 * input3_level) >> 8;
        external_scaled = (external_input * 128) >> 8;
        


        global mix_buffer = (input1_scaled + input2_scaled + input3_scaled + external_scaled) >> 2;
        

        mixed_output = (global mix_buffer * master_level) >> 8;
        

        if (mixed_output > 2047) mixed_output = 2047;
        if (mixed_output < -2047) mixed_output = -2047;
        

        global signal[0] = mixed_output;
        global signal[1] = mixed_output;
        

        global displayLEDs[0] = input1_level;
        global displayLEDs[1] = input2_level;
        global displayLEDs[2] = input3_level;
        global displayLEDs[3] = master_level;
        
        yield();
    }
}

```

## How It Works

**Signal Generation**: Creates three different test signals (sine wave, sawtooth, and noise) plus external audio input for mixing demonstration.

**Individual Level Control**: Each input has independent gain control from 0-255, scaled to 0-100% gain for mixing.

**Headroom Management**: Divides the final mix by 4 to prevent clipping when all inputs are at maximum level. This reserves headroom for safe mixing.

**Master Level**: Final output level control applied after mixing, allowing overall volume adjustment.

**Parameter Control**:
- **Knob 1**: Input 1 level (sine wave)
- **Knob 2**: Input 2 level (sawtooth wave) 
- **Knob 3**: Input 3 level (noise)
- **Knob 4**: Master output level

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 128;
params[OPERATOR_1_PARAM_INDEX] = 64;
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


params[CLOCK_FREQ_PARAM_INDEX] = 200;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 32;
params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


params[CLOCK_FREQ_PARAM_INDEX] = 100;
params[SWITCHES_PARAM_INDEX] = 80;
params[OPERATOR_1_PARAM_INDEX] = 180;
params[OPERAND_1_HIGH_PARAM_INDEX] = 120;


params[CLOCK_FREQ_PARAM_INDEX] = 160;
params[SWITCHES_PARAM_INDEX] = 160;
params[OPERATOR_1_PARAM_INDEX] = 0;
params[OPERAND_1_HIGH_PARAM_INDEX] = 180;
```

## Understanding Mixing Mathematics

**Linear Addition**: Basic mixing is mathematical addition: `output = input1 + input2 + input3`

**Headroom Management**: With multiple inputs at maximum level, the sum can exceed the available range. Dividing by the number of inputs prevents overflow.

**Gain Staging**: Each input is scaled by its level control before mixing, allowing individual balance control while maintaining overall headroom.

**Master Control**: Final level adjustment applied after mixing for overall volume control.

## Try These Changes

- **Logarithmic faders**: Use `level = (param * param) >> 8` for more natural volume curves
- **Stereo panning**: Add pan controls for each input to create stereo positioning
- **Mute/solo controls**: Implement mute and solo functionality for live performance
- **Send effects**: Route portions of each input to reverb or delay effects

## Related Techniques

- **[Crossfade](crossfade.md)**: Smooth transitions between mixed signals
- **[Input Monitoring](input-monitoring.md)**: Monitor signal levels for mixing feedback
- **[Parameter Smoothing](../parameters/parameter-smoothing.md)**: Smooth level changes to prevent clicks

---
*Part of the [Permut8 Cookbook](../index.md) series*
