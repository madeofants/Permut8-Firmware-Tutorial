# Multi-Band Compressor

*Split audio into frequency bands and compress each independently*

## What This Does

Creates a simple 2-band compressor that splits audio into low and high frequencies and applies different compression to each band. This allows for more precise dynamic control - for example, compressing bass heavily while leaving highs untouched.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Low band threshold (0-255, bass compression level)
- `params[1]`: High band threshold (0-255, treble compression level)
- `params[2]`: Crossover frequency (0-255, where to split bass/treble)
- `params[3]`: Output gain (0-255, level compensation)

**Key Concepts:** Frequency splitting, independent compression, band recombination

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple multi-band state
global int low_envelope = 0     // Low band envelope
global int high_envelope = 0    // High band envelope
global int low_gain = 255       // Low band gain reduction
global int high_gain = 255      // High band gain reduction
global int filter_state = 0     // Simple filter state

function process()
locals int crossover, int low_thresh, int high_thresh, int output_gain, int input, int low_band, int high_band, int compressed_low, int compressed_high, int output, int low_level, int high_level, int overage, int target_gain
{
    loop {
        // Read parameters
        low_thresh = ((int)global params[0] << 3) + 512;    // 512-2560 range
        high_thresh = ((int)global params[1] << 3) + 512;   // 512-2560 range
        crossover = ((int)global params[2] >> 4) + 1;       // 1-16 filter strength
        output_gain = ((int)global params[3] >> 1) + 128;   // 128-255 gain
        
        input = (int)global signal[0];
        
        // Simple frequency splitting using one-pole filters
        // Low band: low-pass filter (keeps bass)
        global filter_state = global filter_state + ((input - global filter_state) >> crossover);
        low_band = global filter_state;
        
        // High band: subtract low from input (keeps treble)
        high_band = input - low_band;
        
        // Simple envelope followers for each band
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
        
        // Calculate gain reduction for low band
        if (global low_envelope > low_thresh) {
            overage = global low_envelope - low_thresh;
            target_gain = 255 - (overage >> 3);  // Simple 8:1 ratio
            if (target_gain < 128) target_gain = 128;
            
            if (target_gain < global low_gain) {
                global low_gain = global low_gain - ((global low_gain - target_gain) >> 2);
            } else {
                global low_gain = global low_gain + ((target_gain - global low_gain) >> 4);
            }
        } else {
            global low_gain = global low_gain + ((255 - global low_gain) >> 4);
        }
        
        // Calculate gain reduction for high band
        if (global high_envelope > high_thresh) {
            overage = global high_envelope - high_thresh;
            target_gain = 255 - (overage >> 3);  // Simple 8:1 ratio
            if (target_gain < 128) target_gain = 128;
            
            if (target_gain < global high_gain) {
                global high_gain = global high_gain - ((global high_gain - target_gain) >> 2);
            } else {
                global high_gain = global high_gain + ((target_gain - global high_gain) >> 4);
            }
        } else {
            global high_gain = global high_gain + ((255 - global high_gain) >> 4);
        }
        
        // Apply compression to each band
        compressed_low = (low_band * global low_gain) >> 8;
        compressed_high = (high_band * global high_gain) >> 8;
        
        // Recombine bands
        output = compressed_low + compressed_high;
        
        // Apply output gain
        output = (output * output_gain) >> 8;
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Output result
        global signal[0] = output;
        global signal[1] = output;
        
        // Show compression activity on LEDs
        global displayLEDs[0] = 255 - global low_gain;   // Low band gain reduction
        global displayLEDs[1] = 255 - global high_gain;  // High band gain reduction
        global displayLEDs[2] = global low_envelope >> 3; // Low band level
        global displayLEDs[3] = global high_envelope >> 3; // High band level
        
        yield();
    }
}
```

## How It Works

**Frequency Splitting**: Uses a simple one-pole low-pass filter to separate bass from treble.

**Independent Compression**: Each band has its own envelope follower and gain reduction.

**Band Recombination**: Compressed bands are simply added back together.

**Parameter Control**:
- **Knob 1**: Low band threshold (higher = less bass compression)
- **Knob 2**: High band threshold (higher = less treble compression)
- **Knob 3**: Crossover frequency (higher = more bass in low band)
- **Knob 4**: Output gain (compensate for compression)

**LED Feedback**: Shows gain reduction and levels for both bands.

## Try These Settings

```impala
// Heavy bass compression, light treble
params[0] = 100;  // Low threshold
params[1] = 200;  // High threshold  
params[2] = 128;  // Medium crossover
params[3] = 180;  // Some makeup gain

// Gentle overall compression
params[0] = 180;  // High low threshold
params[1] = 180;  // High high threshold
params[2] = 128;  // Medium crossover
params[3] = 160;  // Light makeup gain
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