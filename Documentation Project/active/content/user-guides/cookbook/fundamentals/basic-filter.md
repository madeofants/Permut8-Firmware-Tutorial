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
- `params[0]`: Cutoff frequency (0-255, controls filter frequency)
- `params[1]`: Resonance (0-255, emphasis at cutoff)
- `params[2]`: Filter type (0-255, low/high/band-pass)
- `params[3]`: Dry/wet mix (0-255, blend control)

**Filter Types:**
- **Low-pass**: Removes high frequencies (creates warmth)
- **High-pass**: Removes low frequencies (adds clarity)
- **Band-pass**: Isolates middle frequencies (telephone effect)

**Key Concepts:** Frequency response, cutoff frequency, resonance, filter state

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple filter state
global int filter_state1 = 0    // First filter state variable
global int filter_state2 = 0    // Second filter state variable

function process()
locals int cutoff, int resonance, int filter_type, int mix, int input, int filter_amount, int low_pass, int high_pass, int band_pass, int filtered, int output
{
    loop {
        // Read parameters
        cutoff = ((int)global params[0] >> 3) + 1;    // 1-32 filter strength
        resonance = ((int)global params[1] >> 3) + 1; // 1-32 resonance amount
        filter_type = ((int)global params[2] >> 6);   // 0-3 filter types
        mix = (int)global params[3];                  // 0-255 dry/wet mix
        
        input = (int)global signal[0];
        
        // Simple one-pole low-pass filter
        global filter_state1 = global filter_state1 + ((input - global filter_state1) >> cutoff);
        low_pass = global filter_state1;
        
        // High-pass = input - low-pass
        high_pass = input - low_pass;
        
        // Second filter stage for band-pass
        global filter_state2 = global filter_state2 + ((high_pass - global filter_state2) >> cutoff);
        band_pass = global filter_state2;
        
        // Select filter type
        if (filter_type == 0) {
            filtered = low_pass;       // Low-pass filter
        } else if (filter_type == 1) {
            filtered = high_pass;      // High-pass filter
        } else if (filter_type == 2) {
            filtered = band_pass;      // Band-pass filter
        } else {
            filtered = input;          // No filtering
        }
        
        // Add resonance (feedback)
        if (resonance > 1) {
            filter_amount = (filtered * resonance) >> 5;
            filtered = filtered + filter_amount;
            
            // Prevent resonance from getting too loud
            if (filtered > 2047) filtered = 2047;
            if (filtered < -2047) filtered = -2047;
        }
        
        // Mix dry and wet signals
        output = ((input * (255 - mix)) + (filtered * mix)) >> 8;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show activity on LEDs
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
// Warm low-pass
params[0] = 128;  // Medium cutoff
params[1] = 64;   // Light resonance
params[2] = 32;   // Low-pass
params[3] = 200;  // Mostly filtered

// Bright high-pass
params[0] = 200;  // High cutoff
params[1] = 100;  // Medium resonance
params[2] = 100;  // High-pass
params[3] = 150;  // Balanced mix

// Telephone effect
params[0] = 100;  // Low cutoff
params[1] = 150;  // Strong resonance
params[2] = 160;  // Band-pass
params[3] = 220;  // Mostly wet

// Classic synth sweep
params[0] = 50;   // Start low
params[1] = 200;  // High resonance
params[2] = 32;   // Low-pass
params[3] = 255;  // Full wet
// (slowly increase params[0] for sweep effect)
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