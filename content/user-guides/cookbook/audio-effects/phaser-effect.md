# Phaser Effect

*Create sweeping "whoosh" sounds with modulated filtering*

## What This Does

Creates the classic phaser effect by using a simple variable filter with LFO modulation. The moving filter frequency creates characteristic sweeping sounds - from subtle movement to dramatic jet-plane effects.

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: LFO rate (0-255, sweep speed)
- `params[SWITCHES_PARAM_INDEX]`: Modulation depth (0-255, sweep range)
- `params[OPERATOR_1_PARAM_INDEX]`: Feedback amount (0-255, intensity)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Variable filtering, LFO modulation, feedback loops, phase relationships

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


global int lfo_phase = 0
global int allpass_state1 = 0
global int allpass_state2 = 0
global int allpass_state3 = 0
global int allpass_state4 = 0
global int feedback_sample = 0

function process()
locals int rate, int depth, int feedback, int mix, int lfo_val, int coeff1, int coeff2, int coeff3, int coeff4, int input, int temp1, int temp2, int temp3, int temp4, int allpass1, int allpass2, int allpass3, int allpass4, int phased_output, int output
{
    loop {

        rate = ((int)global params[CLOCK_FREQ_PARAM_INDEX] >> 4) + 1;
        depth = ((int)global params[SWITCHES_PARAM_INDEX] >> 2) + 1;
        feedback = (int)global params[OPERATOR_1_PARAM_INDEX];
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        
        input = (int)global signal[0];
        

        input = input + ((global feedback_sample * feedback) >> 9);
        if (input > 2047) input = 2047;
        if (input < -2047) input = -2047;
        

        global lfo_phase = (global lfo_phase + rate) & 255;
        if (global lfo_phase < 128) {
            lfo_val = global lfo_phase;
        } else {
            lfo_val = 255 - global lfo_phase;
        }
        

        coeff1 = (lfo_val * depth) >> 6;
        if (coeff1 > 127) coeff1 = 127;
        
        coeff2 = coeff1 + 16;
        if (coeff2 > 127) coeff2 = 127;
        
        coeff3 = coeff1 + 32;
        if (coeff3 > 127) coeff3 = 127;
        
        coeff4 = coeff1 + 48;
        if (coeff4 > 127) coeff4 = 127;
        


        temp1 = input + ((global allpass_state1 * coeff1) >> 7);
        allpass1 = temp1 - ((global allpass_state1 * coeff1) >> 7);
        global allpass_state1 = temp1;
        

        temp2 = allpass1 + ((global allpass_state2 * coeff2) >> 7);
        allpass2 = temp2 - ((global allpass_state2 * coeff2) >> 7);
        global allpass_state2 = temp2;
        

        temp3 = allpass2 + ((global allpass_state3 * coeff3) >> 7);
        allpass3 = temp3 - ((global allpass_state3 * coeff3) >> 7);
        global allpass_state3 = temp3;
        

        temp4 = allpass3 + ((global allpass_state4 * coeff4) >> 7);
        allpass4 = temp4 - ((global allpass_state4 * coeff4) >> 7);
        global allpass_state4 = temp4;
        

        global feedback_sample = allpass4;
        

        phased_output = allpass4;
        

        output = ((input * (255 - mix)) + (phased_output * mix)) >> 8;
        

        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        

        global signal[0] = output;
        global signal[1] = output;
        

        global displayLEDs[0] = lfo_val << 1;
        global displayLEDs[1] = coeff1 << 1;
        global displayLEDs[2] = (feedback >> 2);
        global displayLEDs[3] = (mix >> 2);
        
        yield();
    }
}

```

## How It Works

**All-Pass Filtering**: Four all-pass filters in series with LFO-modulated coefficients create phase shifts without amplitude changes.

**LFO Modulation**: A triangle wave smoothly varies the all-pass filter coefficients, creating the characteristic sweep.

**Feedback Loop**: Adds resonance and intensity by feeding the all-pass output back to the input.

**Phase Relationship**: All-pass filters maintain amplitude while shifting phase, creating the classic phaser "notch" effect when mixed with the original signal.

**Parameter Control**:
- **Control 1**: LFO rate (faster = quicker sweeps)
- **Control 2**: Modulation depth (higher = wider sweeps)
- **Control 3**: Feedback (higher = more resonance)
- **Control 4**: Dry/wet mix (blend original with phased)

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 64;
global params[SWITCHES_PARAM_INDEX] = 128;
global params[OPERATOR_1_PARAM_INDEX] = 64;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;


global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 200;
global params[OPERATOR_1_PARAM_INDEX] = 120;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 180;
```

## Try These Changes

- **Adjust filter spacing**: Modify coefficient offsets (16, 32, 48) for different notch spacing
- **Different LFO shapes**: Use sawtooth or sine waves for different sweep characters
- **Stereo phasing**: Use different LFO phases for left/right channels
- **Tempo sync**: Sync LFO rate to musical timing

## Related Techniques

- **[Chorus Effect](chorus-effect.md)**: Related modulation-based effect
- **[Basic Filter](../fundamentals/basic-filter.md)**: Filter implementation fundamentals

---
*Part of the [Permut8 Cookbook](../index.md) series*