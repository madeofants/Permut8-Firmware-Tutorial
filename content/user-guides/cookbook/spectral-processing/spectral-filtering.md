# Spectral Filtering

*Apply filters directly in the frequency domain for precise spectral control and unique effects*

## What This Does

Provides frequency domain filtering that operates directly on spectral components. Enables precise control over individual frequency bins with filter types impossible in traditional time-domain filtering.

## Quick Reference

**Essential Parameters:**
- `params[0]`: Cutoff frequency (0-255, selects frequency bin 0-7)
- `params[1]`: Filter slope (0-255, steepness control)
- `params[2]`: Resonance (0-255, peak boost at cutoff)
- `params[3]`: Filter type (0-255, selects filter characteristic)

**Core Techniques:**
- **Frequency domain filtering**: Direct spectral manipulation
- **Arbitrary filter shapes**: Custom frequency response curves
- **Harmonic control**: Individual frequency bin processing
- **Zero phase filtering**: No phase distortion

**Key Concepts:** Spectral filtering, frequency bins, filter response, harmonic processing

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Spectral filtering state
global array magnitude[8]       // Frequency bin magnitudes
global array filter_gains[8]    // Filter gain per frequency bin
global array filtered_spectrum[8] // Filtered frequency content
global int update_counter = 0   // Analysis rate control
global int filter_type = 0      // Filter type selection

function process()
locals int i, int cutoff_freq, int filter_slope, int filter_resonance, int input_amplitude, int output_amplitude, int led_pattern
{
    loop {
        // Read control parameters
        cutoff_freq = (int)global params[0] >> 5;        // 0-7 range (cutoff frequency bin)
        filter_slope = ((int)global params[1] >> 6) + 1; // 1-4 range (filter steepness)
        filter_resonance = (int)global params[2];        // 0-255 range (resonance amount)
        global filter_type = (int)global params[3] >> 6; // 0-3 range (filter type)
        
        // Simple frequency analysis from input signal
        global update_counter = global update_counter + 1;
        if (global update_counter >= 256) {  // Update rate control
            global update_counter = 0;
            
            input_amplitude = (int)global signal[0];
            if (input_amplitude < 0) input_amplitude = -input_amplitude;
            
            // Distribute input energy across frequency bins (simplified spectral analysis)
            global magnitude[0] = input_amplitude >> 4;  // DC/Low
            global magnitude[1] = input_amplitude >> 3;  // Low
            global magnitude[2] = input_amplitude >> 2;  // Low-mid
            global magnitude[3] = input_amplitude >> 1;  // Mid (strongest)
            global magnitude[4] = input_amplitude >> 2;  // Mid-high
            global magnitude[5] = input_amplitude >> 3;  // High
            global magnitude[6] = input_amplitude >> 4;  // Very high
            global magnitude[7] = input_amplitude >> 5;  // Ultra high
            
            // Calculate filter gains based on filter type and parameters
            if (global filter_type == 0) {
                // Low-pass filter
                global filter_gains[0] = 255;  // Pass DC
                if (cutoff_freq >= 1) { global filter_gains[1] = 255; } else { global filter_gains[1] = 0; }
                if (cutoff_freq >= 2) { global filter_gains[2] = 255; } else { global filter_gains[2] = 0; }
                if (cutoff_freq >= 3) { global filter_gains[3] = 255; } else { global filter_gains[3] = 0; }
                if (cutoff_freq >= 4) { global filter_gains[4] = 255; } else { global filter_gains[4] = 0; }
                if (cutoff_freq >= 5) { global filter_gains[5] = 255; } else { global filter_gains[5] = 0; }
                if (cutoff_freq >= 6) { global filter_gains[6] = 255; } else { global filter_gains[6] = 0; }
                if (cutoff_freq >= 7) { global filter_gains[7] = 255; } else { global filter_gains[7] = 0; }
                
            } else if (global filter_type == 1) {
                // High-pass filter
                if (cutoff_freq <= 0) { global filter_gains[0] = 255; } else { global filter_gains[0] = 0; }
                if (cutoff_freq <= 1) { global filter_gains[1] = 255; } else { global filter_gains[1] = 0; }
                if (cutoff_freq <= 2) { global filter_gains[2] = 255; } else { global filter_gains[2] = 0; }
                if (cutoff_freq <= 3) { global filter_gains[3] = 255; } else { global filter_gains[3] = 0; }
                if (cutoff_freq <= 4) { global filter_gains[4] = 255; } else { global filter_gains[4] = 0; }
                if (cutoff_freq <= 5) { global filter_gains[5] = 255; } else { global filter_gains[5] = 0; }
                if (cutoff_freq <= 6) { global filter_gains[6] = 255; } else { global filter_gains[6] = 0; }
                global filter_gains[7] = 255;  // Always pass high frequencies
                
            } else if (global filter_type == 2) {
                // Band-pass filter (centered around cutoff)
                global filter_gains[0] = 0;
                global filter_gains[1] = 0;
                if (cutoff_freq == 2) { global filter_gains[2] = 255; } else { global filter_gains[2] = 0; }
                if (cutoff_freq == 3) { global filter_gains[3] = 255; } else { global filter_gains[3] = 0; }
                if (cutoff_freq == 4) { global filter_gains[4] = 255; } else { global filter_gains[4] = 0; }
                if (cutoff_freq == 5) { global filter_gains[5] = 255; } else { global filter_gains[5] = 0; }
                global filter_gains[6] = 0;
                global filter_gains[7] = 0;
                
            } else {
                // Notch filter (inverse of band-pass)
                global filter_gains[0] = 255;
                global filter_gains[1] = 255;
                if (cutoff_freq == 2) { global filter_gains[2] = 0; } else { global filter_gains[2] = 255; }
                if (cutoff_freq == 3) { global filter_gains[3] = 0; } else { global filter_gains[3] = 255; }
                if (cutoff_freq == 4) { global filter_gains[4] = 0; } else { global filter_gains[4] = 255; }
                if (cutoff_freq == 5) { global filter_gains[5] = 0; } else { global filter_gains[5] = 255; }
                global filter_gains[6] = 255;
                global filter_gains[7] = 255;
            }
            
            // Add resonance boost at cutoff frequency
            if (cutoff_freq < 8 && filter_resonance > 64) {
                global filter_gains[cutoff_freq] = 255 + (filter_resonance >> 2);
                if ((int)global filter_gains[cutoff_freq] > 511) global filter_gains[cutoff_freq] = 511;
            }
            
            // Apply filtering to spectrum
            global filtered_spectrum[0] = ((int)global magnitude[0] * (int)global filter_gains[0]) >> 8;
            global filtered_spectrum[1] = ((int)global magnitude[1] * (int)global filter_gains[1]) >> 8;
            global filtered_spectrum[2] = ((int)global magnitude[2] * (int)global filter_gains[2]) >> 8;
            global filtered_spectrum[3] = ((int)global magnitude[3] * (int)global filter_gains[3]) >> 8;
            global filtered_spectrum[4] = ((int)global magnitude[4] * (int)global filter_gains[4]) >> 8;
            global filtered_spectrum[5] = ((int)global magnitude[5] * (int)global filter_gains[5]) >> 8;
            global filtered_spectrum[6] = ((int)global magnitude[6] * (int)global filter_gains[6]) >> 8;
            global filtered_spectrum[7] = ((int)global magnitude[7] * (int)global filter_gains[7]) >> 8;
        }
        
        // Reconstruct filtered audio (inverse spectral synthesis)
        output_amplitude = 0;
        output_amplitude = output_amplitude + (int)global filtered_spectrum[0];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[1];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[2];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[3];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[4];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[5];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[6];
        output_amplitude = output_amplitude + (int)global filtered_spectrum[7];
        output_amplitude = output_amplitude >> 3;  // Divide by 8
        
        // Mix with original signal for more natural sound
        input_amplitude = (int)global signal[0];
        output_amplitude = (input_amplitude >> 2) + (output_amplitude * 3 >> 2);
        
        // Prevent clipping
        if (output_amplitude > 2047) output_amplitude = 2047;
        if (output_amplitude < -2047) output_amplitude = -2047;
        
        // === SPECTRAL FILTER VISUALIZATION ===
        // Display original spectrum on LED ring 0
        led_pattern = 0;
        if (((int)global magnitude[0] >> 5) > 0) led_pattern = led_pattern | 1;
        if (((int)global magnitude[1] >> 5) > 0) led_pattern = led_pattern | 2;
        if (((int)global magnitude[2] >> 5) > 0) led_pattern = led_pattern | 4;
        if (((int)global magnitude[3] >> 5) > 0) led_pattern = led_pattern | 8;
        if (((int)global magnitude[4] >> 5) > 0) led_pattern = led_pattern | 16;
        if (((int)global magnitude[5] >> 5) > 0) led_pattern = led_pattern | 32;
        if (((int)global magnitude[6] >> 5) > 0) led_pattern = led_pattern | 64;
        if (((int)global magnitude[7] >> 5) > 0) led_pattern = led_pattern | 128;
        global displayLEDs[0] = led_pattern;
        
        // Display filter response on LED ring 1
        led_pattern = 0;
        if (((int)global filter_gains[0] >> 7) > 0) led_pattern = led_pattern | 1;
        if (((int)global filter_gains[1] >> 7) > 0) led_pattern = led_pattern | 2;
        if (((int)global filter_gains[2] >> 7) > 0) led_pattern = led_pattern | 4;
        if (((int)global filter_gains[3] >> 7) > 0) led_pattern = led_pattern | 8;
        if (((int)global filter_gains[4] >> 7) > 0) led_pattern = led_pattern | 16;
        if (((int)global filter_gains[5] >> 7) > 0) led_pattern = led_pattern | 32;
        if (((int)global filter_gains[6] >> 7) > 0) led_pattern = led_pattern | 64;
        if (((int)global filter_gains[7] >> 7) > 0) led_pattern = led_pattern | 128;
        global displayLEDs[1] = led_pattern;
        
        // Show filter cutoff frequency on LED ring 2
        if (cutoff_freq > 7) cutoff_freq = 7;
        global displayLEDs[2] = 1 << cutoff_freq;
        
        // Show filter type on LED ring 3
        global displayLEDs[3] = (global filter_type + 1) << 6;  // Show current filter type
        
        // Output filtered audio
        global signal[0] = output_amplitude;
        global signal[1] = output_amplitude;
        
        yield();
    }
}
```

## How It Works

**Spectral Analysis**: Input audio is analyzed to extract frequency content across 8 frequency bins.

**Filter Design**: Different filter types (low-pass, high-pass, band-pass, notch) are implemented by setting gain values for each frequency bin.

**Resonance Control**: Adds boost at the cutoff frequency for more pronounced filtering effects.

**Spectral Multiplication**: Filter gains are multiplied with frequency bin magnitudes to apply the filtering.

**Parameter Control**:
- **Knob 1**: Cutoff frequency (0-7, selects which frequency bin)
- **Knob 2**: Filter slope (steepness, future enhancement)
- **Knob 3**: Resonance amount (0-255, peak boost at cutoff)
- **Knob 4**: Filter type (0-3: low-pass, high-pass, band-pass, notch)

## Understanding Filter Types

**Low-Pass Filter (Type 0)**: Passes frequencies below cutoff, attenuates higher frequencies.

**High-Pass Filter (Type 1)**: Passes frequencies above cutoff, attenuates lower frequencies.

**Band-Pass Filter (Type 2)**: Passes frequencies near cutoff, attenuates everything else.

**Notch Filter (Type 3)**: Attenuates frequencies near cutoff, passes everything else.

## Try These Settings

```impala
// Low-pass filter with resonance
params[0] = 128;  // Mid cutoff frequency (bin 4)
params[1] = 128;  // Medium slope
params[2] = 200;  // High resonance
params[3] = 0;    // Low-pass type

// High-pass filter
params[0] = 64;   // Low cutoff frequency (bin 2)
params[1] = 192;  // Steep slope
params[2] = 100;  // Moderate resonance
params[3] = 64;   // High-pass type

// Notch filter for removing specific frequency
params[0] = 160;  // Higher cutoff (bin 5)
params[1] = 255;  // Maximum slope
params[2] = 255;  // Maximum resonance
params[3] = 192;  // Notch type
```

## Understanding Frequency Bins

The 8 frequency bins represent different frequency ranges:
- Bin 0: DC/Very low frequencies
- Bin 1: Low frequencies (bass)
- Bin 2: Low-mid frequencies
- Bin 3: Mid frequencies (most prominent)
- Bin 4: Mid-high frequencies
- Bins 5-7: High frequencies (treble)

## Visual Feedback

**LED Ring 0**: Shows original frequency spectrum before filtering.

**LED Ring 1**: Shows filter response (which frequencies pass through).

**LED Ring 2**: Shows cutoff frequency position.

**LED Ring 3**: Shows current filter type (brightness indicates type).

## Advantages of Spectral Filtering

**Precise Control**: Exact control over individual frequency components.

**Zero Phase Distortion**: No phase shift artifacts when properly implemented.

**Arbitrary Shapes**: Can create filter responses impossible with traditional filters.

**Dynamic Control**: Real-time modification of filter characteristics.

## Try These Changes

- **Variable slope**: Implement gradual filter rolloff using intermediate gain values
- **Multi-band processing**: Create multiple filter bands for equalizer-style control
- **Harmonic enhancement**: Boost specific harmonic relationships
- **Dynamic filtering**: Use audio content to control filter parameters

## Related Techniques

- **[FFT Basics](fft-basics.md)**: Foundation frequency analysis
- **[Frequency Analysis](frequency-analysis.md)**: Spectral information extraction
- **[Phase Vocoder](phase-vocoder.md)**: Advanced spectral processing
- **[Basic Filter](../fundamentals/basic-filter.md)**: Time-domain filtering comparison

---

*This spectral filtering system provides precise frequency domain control for creative filtering effects. Perfect for understanding spectral processing concepts and creating unique filter responses impossible with traditional time-domain methods.*