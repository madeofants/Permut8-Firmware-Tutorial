# Basic Filter

*Shape frequency content with simple digital filters*

## What This Does

Filters selectively reduce or emphasize certain frequencies in audio signals. Use them to remove unwanted frequencies, shape tone character, or create classic synthesizer effects like resonant sweeps.

### **Approach: Custom Firmware (Direct Processing)**

This recipe demonstrates **Approach 2: Custom Firmware** - implementing digital filter algorithms with direct sample-by-sample processing.

**Why This Approach?**:
- **Filter algorithms** require precise mathematical operations on audio samples
- **State management** - filters need to remember previous values for recursive processing
- **Custom interface** - intuitive cutoff/resonance/type controls
- **Educational** - shows how digital filters work at the algorithm level

**How It Works**:
```
Audio Input → [Custom filter algorithm with state variables] → Audio Output
```
- Direct sample processing with recursive filter equations
- Custom state variables store filter memory between samples
- Multiple filter types selectable via parameter

**Alternative Approaches**:
- **Original operators**: No direct filtering operators, but could combine for effect
- **Operator modification**: Replace operator with custom filter (hybrid approach)
- **Hardware assistance**: Some filter operations could use bit manipulation operators

## Quick Reference

**Essential Parameters:**
- `params[CLOCK_FREQ_PARAM_INDEX]`: Cutoff frequency (0-255, controls filter frequency)
- `params[SWITCHES_PARAM_INDEX]`: Resonance (0-255, emphasis at cutoff)
- `params[OPERATOR_1_PARAM_INDEX]`: Filter type (0-255, low/high/band-pass)
- `params[OPERAND_1_HIGH_PARAM_INDEX]`: Dry/wet mix (0-255, blend control)

**Filter Types:**
- **Low-pass**: Removes high frequencies (creates warmth)
- **High-pass**: Removes low frequencies (adds clarity)
- **Band-pass**: Isolates middle frequencies (telephone effect)

**Key Concepts:** Frequency response, cutoff frequency, resonance, filter state

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


global int filter_state1 = 0
global int filter_state2 = 0

function process()
locals int cutoff, int resonance, int filter_type, int mix, int input, int filter_amount, int low_pass, int high_pass, int band_pass, int filtered, int output
{
    loop {

        cutoff = ((int)global params[CLOCK_FREQ_PARAM_INDEX] >> 3) + 1;
        resonance = ((int)global params[SWITCHES_PARAM_INDEX] >> 3) + 1;
        filter_type = ((int)global params[OPERATOR_1_PARAM_INDEX] >> 6);
        mix = (int)global params[OPERAND_1_HIGH_PARAM_INDEX];
        
        input = (int)global signal[0];
        

        global filter_state1 = global filter_state1 + ((input - global filter_state1) >> cutoff);
        low_pass = global filter_state1;
        

        high_pass = input - low_pass;
        

        global filter_state2 = global filter_state2 + ((high_pass - global filter_state2) >> cutoff);
        band_pass = global filter_state2;
        

        if (filter_type == 0) {
            filtered = low_pass;
        } else if (filter_type == 1) {
            filtered = high_pass;
        } else if (filter_type == 2) {
            filtered = band_pass;
        } else {
            filtered = input;
        }
        

        if (resonance > 1) {
            filter_amount = (filtered * resonance) >> 5;
            filtered = filtered + filter_amount;
            

            if (filtered > 2047) filtered = 2047;
            if (filtered < -2047) filtered = -2047;
        }
        

        output = ((input * (255 - mix)) + (filtered * mix)) >> 8;
        

        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        

        global signal[0] = output;
        global signal[1] = output;
        

        global displayLEDs[0] = cutoff << 3;
        global displayLEDs[1] = resonance << 3;
        global displayLEDs[2] = filter_type << 6;
        global displayLEDs[3] = (mix >> 2);
        
        yield();
    }
}
```

## How It Works

**One-Pole Filter**: Uses a simple recursive filter that mixes the current input with the previous output.

**Filter Types**:
- **Low-pass**: Smooth changes by averaging with previous values
- **High-pass**: Subtracts the low-pass from the input to get high frequencies
- **Band-pass**: Applies low-pass filtering to the high-pass output

**Cutoff Control**: Lower cutoff values = stronger filtering, higher values = more transparent.

**Resonance**: Adds feedback to emphasize frequencies near the cutoff point.

**Parameter Control**:
- **Control 1**: Cutoff frequency (lower = more filtering)
- **Control 2**: Resonance (higher = more emphasis)
- **Control 3**: Filter type (0-63=low, 64-127=high, 128-191=band, 192-255=bypass)
- **Control 4**: Dry/wet mix (blend filtered with original)

## Try These Settings

```impala

global params[CLOCK_FREQ_PARAM_INDEX] = 128;
global params[SWITCHES_PARAM_INDEX] = 64;
global params[OPERATOR_1_PARAM_INDEX] = 32;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 200;


global params[CLOCK_FREQ_PARAM_INDEX] = 200;
global params[SWITCHES_PARAM_INDEX] = 100;
global params[OPERATOR_1_PARAM_INDEX] = 100;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 150;


global params[CLOCK_FREQ_PARAM_INDEX] = 100;
global params[SWITCHES_PARAM_INDEX] = 150;
global params[OPERATOR_1_PARAM_INDEX] = 160;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 220;


global params[CLOCK_FREQ_PARAM_INDEX] = 50;
global params[SWITCHES_PARAM_INDEX] = 200;
global params[OPERATOR_1_PARAM_INDEX] = 32;
global params[OPERAND_1_HIGH_PARAM_INDEX] = 255;

```

## Understanding Filters

**Frequency Response**: Filters change the balance of frequencies in your signal. Low-pass filters make sounds warmer and darker, high-pass filters make them brighter and thinner.

**Cutoff Frequency**: The point where the filter starts to take effect. Above this frequency (low-pass) or below this frequency (high-pass), the signal is gradually reduced.

**Resonance**: Boosts frequencies right at the cutoff point, creating emphasis and character. High resonance can make filters "ring" or even self-oscillate.

**Filter Order**: This is a simple one-pole filter. Higher-order filters (two-pole, four-pole) have steeper slopes but require more computation.

## Try These Changes

- **Stereo filtering**: Use different cutoff frequencies for left and right channels
- **LFO modulation**: Slowly vary the cutoff frequency for automatic filter sweeps
- **Envelope control**: Link filter cutoff to input level for dynamic filtering
- **Multiple stages**: Chain two filters in series for steeper response

## Related Techniques

- **[Basic Oscillator](basic-oscillator.md)**: LFO sources for filter modulation
- **[Envelope Basics](envelope-basics.md)**: Dynamic filter control

---
*Part of the [Permut8 Cookbook](../index.md) series*