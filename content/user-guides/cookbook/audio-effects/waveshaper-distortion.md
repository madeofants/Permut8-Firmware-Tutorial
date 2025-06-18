# Waveshaper Distortion

*Create harmonic distortion by reshaping audio waveforms*

## What This Does

Creates distortion by applying mathematical curves to reshape the audio waveform. Generates everything from subtle tube warmth to aggressive clipping effects by pushing audio through different waveshaping functions.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Input drive (0-255, controls distortion intensity)
- `params[1]`: Distortion type (0-255, selects waveshaping curve)
- `params[2]`: Output level (0-255, compensates for volume changes)
- `params[3]`: Dry/wet mix (0-255, blend control)

**Key Concepts:** Waveshaping curves, harmonic generation, clipping algorithms, drive control

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

function process()
locals int drive, int dist_type, int output_level, int mix, int input, int driven, int shaped, int output, int mask
{
    loop {
        // Read parameters
        drive = ((int)global params[0] >> 2) + 1;     // 1-64 drive amount
        dist_type = ((int)global params[1] >> 6);     // 0-3 distortion types
        output_level = ((int)global params[2] >> 1) + 64;  // 64-191 output gain
        mix = (int)global params[3];                  // 0-255 dry/wet mix
        
        input = (int)global signal[0];
        
        // Apply input drive
        driven = input * drive;
        
        // Prevent overflow before waveshaping
        if (driven > 2047) driven = 2047;
        if (driven < -2047) driven = -2047;
        
        // Apply waveshaping based on type
        if (dist_type == 0) {
            // Soft clipping - gentle saturation
            if (driven > 1365) {
                shaped = 1365 + ((driven - 1365) >> 2);  // Compress highs
            } else if (driven < -1365) {
                shaped = -1365 + ((driven + 1365) >> 2); // Compress lows
            } else {
                shaped = driven;  // Linear in middle
            }
            
        } else if (dist_type == 1) {
            // Hard clipping - aggressive limiting
            if (driven > 1024) {
                shaped = 1024;
            } else if (driven < -1024) {
                shaped = -1024;
            } else {
                shaped = driven;
            }
            
        } else if (dist_type == 2) {
            // Bit reduction - digital artifacts
            mask = 0xFFF0;  // Remove lower 4 bits
            shaped = driven & mask;
            
        } else {
            // Fold-back - wrap around at limits
            if (driven > 1024) {
                shaped = 2048 - driven;  // Fold back down
            } else if (driven < -1024) {
                shaped = -2048 + driven; // Fold back up (corrected sign)
            } else {
                shaped = driven;
            }
        }
        
        // Apply output level compensation
        shaped = (shaped * output_level) >> 8;
        
        // Prevent final clipping
        if (shaped > 2047) shaped = 2047;
        if (shaped < -2047) shaped = -2047;
        
        // Mix dry and wet signals
        output = ((input * (255 - mix)) + (shaped * mix)) >> 8;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show activity on LEDs with optimized scaling
        global displayLEDs[0] = (drive - 1) << 2;              // Drive level (0-252)
        global displayLEDs[1] = dist_type << 6;                // Distortion type (0,64,128,192)
        global displayLEDs[2] = (output_level - 64) << 1;      // Output gain (0-254)
        global displayLEDs[3] = (mix >> 2);                    // Mix level (0-63)
        
        yield();
    }
}
```

## How It Works

**Input Drive**: Amplifies the signal before waveshaping to control distortion intensity.

**Waveshaping Types**:
- **Type 0 (Soft Clip)**: Gentle compression at high levels, preserves dynamics
- **Type 1 (Hard Clip)**: Aggressive limiting, creates square-wave harmonics
- **Type 2 (Bit Crush)**: Digital artifacts by removing bit resolution
- **Type 3 (Fold-back)**: Wraps signal around at limits for unique textures

**Output Compensation**: Adjusts level after distortion to maintain consistent volume.

**Parameter Control**:
- **Control 1**: Drive (higher = more distortion)
- **Control 2**: Type (0-63=soft, 64-127=hard, 128-191=bit, 192-255=fold)
- **Control 3**: Output level (compensate for volume changes)
- **Control 4**: Dry/wet mix (blend clean with distorted)

## Try These Settings

```impala
// Subtle tube warmth
params[0] = 100;  // Light drive
params[1] = 32;   // Soft clipping
params[2] = 180;  // Boost output
params[3] = 150;  // Blend with dry

// Heavy rock distortion
params[0] = 200;  // High drive
params[1] = 100;  // Hard clipping
params[2] = 140;  // Lower output
params[3] = 220;  // Mostly distorted

// Digital glitch
params[0] = 150;  // Medium drive
params[1] = 160;  // Bit crushing
params[2] = 200;  // Boost output
params[3] = 180;  // Mostly wet

// Experimental texture
params[0] = 180;  // High drive
params[1] = 220;  // Fold-back
params[2] = 160;  // Medium output
params[3] = 200;  // Mostly processed
```

## Understanding Waveshaping

**Harmonic Generation**: Waveshaping creates new frequencies (harmonics) not present in the original signal by applying non-linear functions.

**Drive vs. Output**: Drive controls how hard you push into the waveshaper (distortion amount), while output compensates for the resulting volume changes.

**Waveshaping Curves**: Different mathematical functions create different harmonic content:
- **Linear**: No distortion (straight line)
- **Soft curves**: Gentle, musical harmonics
- **Hard edges**: Aggressive, buzzy harmonics
- **Fold-back**: Unique, metallic textures

## Try These Changes

- **Multiple stages**: Apply waveshaping twice for more complex distortion
- **Frequency-dependent**: Apply different amounts to high vs low frequencies
- **Dynamic waveshaping**: Vary the curve based on input level
- **Stereo processing**: Different waveshaping for left/right channels

## Related Techniques

- **[Gain and Volume](../fundamentals/gain-and-volume.md)**: Level control fundamentals
- **[Bitcrusher](bitcrusher.md)**: Related digital distortion effects

---
*Part of the [Permut8 Cookbook](../index.md) series*