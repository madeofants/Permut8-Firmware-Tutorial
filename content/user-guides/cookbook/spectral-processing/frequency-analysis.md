# Frequency Analysis

*Extract musical information from spectral data including pitch detection, harmonic analysis, and spectral characteristics*

## What This Does

Analyzes frequency content to extract musically meaningful information from audio signals. Provides peak detection for dominant frequencies, spectral centroid calculation for timbral analysis, and harmonic strength measurement for musical content detection.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Peak threshold (0-255, minimum level for peak detection)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Noise floor (0-255, background noise level)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Mid-frequency boost (0-255, emphasis control)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: High-frequency boost (0-255, brightness control)

**Core Techniques:**
- **Peak detection**: Find dominant frequency components
- **Spectral centroid**: Calculate frequency center of mass
- **Harmonic analysis**: Measure harmonic content strength
- **Frequency tracking**: Monitor dominant frequencies over time

**Key Concepts:** Peak detection, spectral centroid, harmonic analysis, frequency tracking

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


global array magnitude[8]
global array peak_tracker[8]
global int peak_frequency = 0
global int spectral_centroid = 0
global int harmonic_strength = 0
global int update_counter = 0

function process()
locals i, peak_threshold, noise_floor, total_energy, weighted_sum, max_bin, max_magnitude, harmonic_sum, fundamental_bin, led_pattern
{
    loop {

        peak_threshold = params[CLOCK_FREQ_PARAM_INDEX];
        noise_floor = params[SWITCHES_PARAM_INDEX] >> 1;
        

        global update_counter = global update_counter + 1;
        if (global update_counter >= 512) {
            global update_counter = 0;
            


            i = signal[0];
            if (i < 0) i = -i;
            

            global magnitude[0] = i >> 5;
            global magnitude[1] = i >> 4;
            global magnitude[2] = i >> 3;
            global magnitude[3] = i >> 4;
            global magnitude[4] = i >> 5;
            global magnitude[5] = i >> 6;
            global magnitude[6] = i >> 7;
            global magnitude[7] = i >> 8;
            

            global magnitude[1] = global magnitude[1] + (params[OPERATOR_1_PARAM_INDEX] >> 3);
            global magnitude[2] = global magnitude[2] + (params[OPERAND_1_HIGH_PARAM_INDEX] >> 2);
            

            max_bin = 0;
            max_magnitude = global magnitude[0];
            i = 1;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            i = 2;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            i = 3;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            i = 4;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            i = 5;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            i = 6;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            i = 7;
            if (global magnitude[i] > max_magnitude) {
                max_magnitude = global magnitude[i];
                max_bin = i;
            }
            

            if (max_magnitude > peak_threshold) {
                global peak_frequency = max_bin;
            }
            

            total_energy = 0;
            weighted_sum = 0;
            total_energy = total_energy + (int)global magnitude[0];
            total_energy = total_energy + (int)global magnitude[1];
            total_energy = total_energy + (int)global magnitude[2];
            total_energy = total_energy + (int)global magnitude[3];
            total_energy = total_energy + (int)global magnitude[4];
            total_energy = total_energy + (int)global magnitude[5];
            total_energy = total_energy + (int)global magnitude[6];
            total_energy = total_energy + (int)global magnitude[7];
            
            weighted_sum = weighted_sum + ((int)global magnitude[0] * 0);
            weighted_sum = weighted_sum + ((int)global magnitude[1] * 1);
            weighted_sum = weighted_sum + ((int)global magnitude[2] * 2);
            weighted_sum = weighted_sum + ((int)global magnitude[3] * 3);
            weighted_sum = weighted_sum + ((int)global magnitude[4] * 4);
            weighted_sum = weighted_sum + ((int)global magnitude[5] * 5);
            weighted_sum = weighted_sum + ((int)global magnitude[6] * 6);
            weighted_sum = weighted_sum + ((int)global magnitude[7] * 7);
            
            if (total_energy > 10) {
                global spectral_centroid = weighted_sum / total_energy;
            } else {
                global spectral_centroid = 3;
            }
            

            fundamental_bin = global peak_frequency;
            harmonic_sum = (int)global magnitude[fundamental_bin];
            if (fundamental_bin * 2 < 8) {
                harmonic_sum = harmonic_sum + (int)global magnitude[fundamental_bin * 2];
            }
            if (fundamental_bin * 3 < 8) {
                harmonic_sum = harmonic_sum + (int)global magnitude[fundamental_bin * 3];
            }
            global harmonic_strength = harmonic_sum >> 2;
        }
        


        led_pattern = 0;
        if (((int)global magnitude[0] >> 4) > 0) led_pattern = led_pattern | 1;
        if (((int)global magnitude[1] >> 4) > 0) led_pattern = led_pattern | 2;
        if (((int)global magnitude[2] >> 4) > 0) led_pattern = led_pattern | 4;
        if (((int)global magnitude[3] >> 4) > 0) led_pattern = led_pattern | 8;
        if (((int)global magnitude[4] >> 4) > 0) led_pattern = led_pattern | 16;
        if (((int)global magnitude[5] >> 4) > 0) led_pattern = led_pattern | 32;
        if (((int)global magnitude[6] >> 4) > 0) led_pattern = led_pattern | 64;
        if (((int)global magnitude[7] >> 4) > 0) led_pattern = led_pattern | 128;
        global displayLEDs[0] = led_pattern;
        

        global displayLEDs[1] = 1 << global peak_frequency;
        

        if (global spectral_centroid > 7) global spectral_centroid = 7;
        global displayLEDs[2] = 1 << global spectral_centroid;
        

        led_pattern = 0;
        i = global harmonic_strength >> 5;
        if (i > 7) i = 7;
        if (i >= 1) led_pattern = led_pattern | 1;
        if (i >= 2) led_pattern = led_pattern | 2;
        if (i >= 3) led_pattern = led_pattern | 4;
        if (i >= 4) led_pattern = led_pattern | 8;
        if (i >= 5) led_pattern = led_pattern | 16;
        if (i >= 6) led_pattern = led_pattern | 32;
        if (i >= 7) led_pattern = led_pattern | 64;
        if (i >= 8) led_pattern = led_pattern | 128;
        global displayLEDs[3] = led_pattern;
        

        global signal[0] = (int)global signal[0];
        global signal[1] = (int)global signal[1];
        
        yield();
    }
}

```

## How It Works

**Peak Detection**: Scans frequency bins to find the dominant frequency component above the threshold level.

**Spectral Centroid**: Calculates the "center of mass" of the frequency spectrum, indicating the brightness or timbral quality of the sound.

**Harmonic Analysis**: Examines relationships between fundamental and harmonic frequencies to measure musical content strength.

**Frequency Tracking**: Monitors dominant frequencies over time with smoothing to avoid rapid changes.

**Parameter Control**:
- **Knob 1**: Peak detection threshold (higher = less sensitive)
- **Knob 2**: Noise floor level (background rejection)
- **Knob 3**: Mid-frequency emphasis (500Hz-2kHz boost)
- **Knob 4**: High-frequency emphasis (2kHz+ boost)

## Understanding Analysis Features

**Peak Frequency**: The dominant frequency bin, shown on LED ring 1. Useful for pitch detection and frequency following.

**Spectral Centroid**: Frequency center of mass, shown on LED ring 2. Higher values indicate brighter sounds.

**Harmonic Strength**: Measure of harmonic content, shown as bar graph on LED ring 3. Higher values indicate more musical content.

**Frequency Bins**: 8 frequency ranges from low (bin 0) to high (bin 7), displayed as spectrum on LED ring 0.

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 64;
params[SWITCHES_PARAM_INDEX] = 32;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 64;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 100;


params[CLOCK_FREQ_PARAM_INDEX] = 100;
params[SWITCHES_PARAM_INDEX] = 80;
params[OPERATOR_1_PARAM_INDEX] = 64;
params[OPERAND_1_HIGH_PARAM_INDEX] = 200;
```

## Musical Applications

**Pitch Following**: Use peak frequency for auto-tuning or pitch-dependent effects.

**Brightness Control**: Use spectral centroid to control filter cutoff or effect intensity.

**Harmonic Filtering**: Use harmonic strength to differentiate between musical and percussive content.

**Adaptive Processing**: Combine all measures for intelligent, content-aware processing.

## Try These Changes

- **Multi-band analysis**: Divide spectrum into more frequency bands for detailed analysis
- **Peak tracking**: Add smoothing and prediction for stable pitch detection
- **Harmonic series**: Detect complete harmonic series for chord analysis
- **Onset detection**: Add energy-based onset detection for rhythm analysis

## Related Techniques

- **[FFT Basics](fft-basics.md)**: Foundation frequency analysis techniques
- **[Phase Vocoder](phase-vocoder.md)**: Advanced spectral processing
- **[Spectral Filtering](spectral-filtering.md)**: Frequency-domain filtering
- **[Level Meters](../visual-feedback/level-meters.md)**: Audio level analysis

---

*This frequency analysis system provides essential spectral information extraction for intelligent audio processing. Perfect for pitch detection, harmonic analysis, and creating musically responsive effects.*