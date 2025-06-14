# Phaser Effect

*Create sweeping "whoosh" sounds with modulated filtering*

## What This Does

Creates the classic phaser effect by using a simple variable filter with LFO modulation. The moving filter frequency creates characteristic sweeping sounds - from subtle movement to dramatic jet-plane effects.

## Quick Reference

**Essential Parameters:**
- `params[0]`: LFO rate (0-255, sweep speed)
- `params[1]`: Modulation depth (0-255, sweep range)
- `params[2]`: Feedback amount (0-255, intensity)
- `params[3]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Variable filtering, LFO modulation, feedback loops, phase relationships

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// All-pass phaser state
global int lfo_phase = 0        // LFO phase accumulator
global int allpass_state1 = 0   // First all-pass filter state
global int allpass_state2 = 0   // Second all-pass filter state
global int allpass_state3 = 0   // Third all-pass filter state
global int allpass_state4 = 0   // Fourth all-pass filter state
global int feedback_sample = 0  // Feedback delay sample

function process()
locals int rate
locals int depth
locals int feedback
locals int mix
locals int lfo_val
locals int coeff1
locals int coeff2
locals int coeff3
locals int coeff4
locals int input
locals int temp1
locals int temp2
locals int temp3
locals int temp4
locals int allpass1
locals int allpass2
locals int allpass3
locals int allpass4
locals int phased_output
locals int output
{
    loop {
        // Read parameters
        rate = ((int)global params[0] >> 4) + 1;     // 1-16 LFO rate
        depth = ((int)global params[1] >> 2) + 1;    // 1-64 modulation depth
        feedback = (int)global params[2];            // 0-255 feedback amount
        mix = (int)global params[3];                 // 0-255 dry/wet mix
        
        input = (int)global signal[0];
        
        // Add feedback for resonance with safety bounds
        input = input + ((global feedback_sample * feedback) >> 9);  // Extra shift for safety
        if (input > 2047) input = 2047;
        if (input < -2047) input = -2047;
        
        // Simple triangle LFO
        global lfo_phase = (global lfo_phase + rate) & 255;
        if (global lfo_phase < 128) {
            lfo_val = global lfo_phase;              // Rising: 0 to 127
        } else {
            lfo_val = 255 - global lfo_phase;       // Falling: 127 to 0
        }
        
        // Calculate all-pass filter coefficients based on LFO
        coeff1 = (lfo_val * depth) >> 6;        // 0-127 range
        if (coeff1 > 127) coeff1 = 127;
        
        coeff2 = coeff1 + 16;                   // Offset coefficient
        if (coeff2 > 127) coeff2 = 127;
        
        coeff3 = coeff1 + 32;                   // Further offset
        if (coeff3 > 127) coeff3 = 127;
        
        coeff4 = coeff1 + 48;                   // Maximum offset
        if (coeff4 > 127) coeff4 = 127;
        
        // Four all-pass filters in series for rich phasing
        // First all-pass filter
        temp1 = input + ((global allpass_state1 * coeff1) >> 7);
        allpass1 = temp1 - ((global allpass_state1 * coeff1) >> 7);
        global allpass_state1 = temp1;
        
        // Second all-pass filter
        temp2 = allpass1 + ((global allpass_state2 * coeff2) >> 7);
        allpass2 = temp2 - ((global allpass_state2 * coeff2) >> 7);
        global allpass_state2 = temp2;
        
        // Third all-pass filter
        temp3 = allpass2 + ((global allpass_state3 * coeff3) >> 7);
        allpass3 = temp3 - ((global allpass_state3 * coeff3) >> 7);
        global allpass_state3 = temp3;
        
        // Fourth all-pass filter
        temp4 = allpass3 + ((global allpass_state4 * coeff4) >> 7);
        allpass4 = temp4 - ((global allpass_state4 * coeff4) >> 7);
        global allpass_state4 = temp4;
        
        // Store for feedback
        global feedback_sample = allpass4;
        
        // Mix all-pass output with original for phasing effect
        phased_output = allpass4;
        
        // Mix dry and wet signals
        output = ((input * (255 - mix)) + (phased_output * mix)) >> 8;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show activity on LEDs
        global displayLEDs[0] = lfo_val << 1;         // LFO position
        global displayLEDs[1] = coeff1 << 1;          // All-pass coefficient
        global displayLEDs[2] = (feedback >> 2);      // Feedback amount
        global displayLEDs[3] = (mix >> 2);           // Mix level
        
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
- **Knob 1**: LFO rate (faster = quicker sweeps)
- **Knob 2**: Modulation depth (higher = wider sweeps)
- **Knob 3**: Feedback (higher = more resonance)
- **Knob 4**: Dry/wet mix (blend original with phased)

## Try These Settings

```impala
// Slow, gentle phasing
params[0] = 64;   // Slow rate
params[1] = 128;  // Medium depth
params[2] = 64;   // Light feedback
params[3] = 128;  // 50% mix

// Fast, dramatic phasing
params[0] = 200;  // Fast rate
params[1] = 200;  // Deep modulation
params[2] = 120;  // Moderate feedback (safer than 150)
params[3] = 180;  // Mostly wet
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