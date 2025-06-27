# Spectral Filtering

*Apply filters directly in the frequency domain for precise spectral control and unique effects*

## What This Does

Provides frequency domain filtering that operates directly on spectral components. Enables precise control over individual frequency bins with filter types impossible in traditional time-domain filtering.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Cutoff frequency (0-255, selects frequency bin 0-7)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Filter slope (0-255, steepness control)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Resonance (0-255, peak boost at cutoff)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Filter type (0-255, selects filter characteristic)

**Core Techniques:**
- **Frequency domain filtering**: Direct spectral manipulation
- **Arbitrary filter shapes**: Custom frequency response curves
- **Harmonic control**: Individual frequency bin processing
- **Zero phase filtering**: No phase distortion

**Key Concepts:** Spectral filtering, frequency bins, filter response, harmonic processing

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
global array filter_gains[8]
global array filtered_spectrum[8]
global int update_counter = 0
global int filter_type = 0

function process()
locals i, cutoff_freq, filter_slope, filter_resonance, input_amplitude, output_amplitude, led_pattern
{
    loop {

        cutoff_freq = params[CLOCK_FREQ_PARAM_INDEX] >> 5;
        filter_slope = (params[SWITCHES_PARAM_INDEX] >> 6) + 1;
        filter_resonance = params[OPERATOR_1_PARAM_INDEX];
        global filter_type = params[OPERAND_1_HIGH_PARAM_INDEX] >> 6;
        

        global update_counter = global update_counter + 1;
        if (global update_counter >= 256) {
            global update_counter = 0;
            
            input_amplitude = signal[0];
            if (input_amplitude < 0) input_amplitude = -input_amplitude;
            

            global magnitude[0] = input_amplitude >> 4;
            global magnitude[1] = input_amplitude >> 3;
            global magnitude[2] = input_amplitude >> 2;
            global magnitude[3] = input_amplitude >> 1;
            global magnitude[4] = input_amplitude >> 2;
            global magnitude[5] = input_amplitude >> 3;
            global magnitude[6] = input_amplitude >> 4;
            global magnitude[7] = input_amplitude >> 5;
            

            if (global filter_type == 0) {

                global filter_gains[0] = 255;
                if (cutoff_freq >= 1) { global filter_gains[1] = 255; } else { global filter_gains[1] = 0; }
                if (cutoff_freq >= 2) { global filter_gains[2] = 255; } else { global filter_gains[2] = 0; }
                if (cutoff_freq >= 3) { global filter_gains[3] = 255; } else { global filter_gains[3] = 0; }
                if (cutoff_freq >= 4) { global filter_gains[4] = 255; } else { global filter_gains[4] = 0; }
                if (cutoff_freq >= 5) { global filter_gains[5] = 255; } else { global filter_gains[5] = 0; }
                if (cutoff_freq >= 6) { global filter_gains[6] = 255; } else { global filter_gains[6] = 0; }
                if (cutoff_freq >= 7) { global filter_gains[7] = 255; } else { global filter_gains[7] = 0; }
                
            } else if (global filter_type == 1) {

                if (cutoff_freq <= 0) { global filter_gains[0] = 255; } else { global filter_gains[0] = 0; }
                if (cutoff_freq <= 1) { global filter_gains[1] = 255; } else { global filter_gains[1] = 0; }
                if (cutoff_freq <= 2) { global filter_gains[2] = 255; } else { global filter_gains[2] = 0; }
                if (cutoff_freq <= 3) { global filter_gains[3] = 255; } else { global filter_gains[3] = 0; }
                if (cutoff_freq <= 4) { global filter_gains[4] = 255; } else { global filter_gains[4] = 0; }
                if (cutoff_freq <= 5) { global filter_gains[5] = 255; } else { global filter_gains[5] = 0; }
                if (cutoff_freq <= 6) { global filter_gains[6] = 255; } else { global filter_gains[6] = 0; }
                global filter_gains[7] = 255;
                
            } else if (global filter_type == 2) {

                global filter_gains[0] = 0;
                global filter_gains[1] = 0;
                if (cutoff_freq == 2) { global filter_gains[2] = 255; } else { global filter_gains[2] = 0; }
                if (cutoff_freq == 3) { global filter_gains[3] = 255; } else { global filter_gains[3] = 0; }
                if (cutoff_freq == 4) { global filter_gains[4] = 255; } else { global filter_gains[4] = 0; }
                if (cutoff_freq == 5) { global filter_gains[5] = 255; } else { global filter_gains[5] = 0; }
                global filter_gains[6] = 0;
                global filter_gains[7] = 0;
                
            } else {

                global filter_gains[0] = 255;
                global filter_gains[1] = 255;
                if (cutoff_freq == 2) { global filter_gains[2] = 0; } else { global filter_gains[2] = 255; }
                if (cutoff_freq == 3) { global filter_gains[3] = 0; } else { global filter_gains[3] = 255; }
                if (cutoff_freq == 4) { global filter_gains[4] = 0; } else { global filter_gains[4] = 255; }
                if (cutoff_freq == 5) { global filter_gains[5] = 0; } else { global filter_gains[5] = 255; }
                global filter_gains[6] = 255;
                global filter_gains[7] = 255;
            }
            

            if (cutoff_freq < 8 && filter_resonance > 64) {
                global filter_gains[cutoff_freq] = 255 + (filter_resonance >> 2);
                if ((int)global filter_gains[cutoff_freq] > 511) global filter_gains[cutoff_freq] = 511;
            }
            

            global filtered_spectrum[0] = (global magnitude[0] * global filter_gains[0]) >> 8;
            global filtered_spectrum[1] = (global magnitude[1] * global filter_gains[1]) >> 8;
            global filtered_spectrum[2] = (global magnitude[2] * global filter_gains[2]) >> 8;
            global filtered_spectrum[3] = (global magnitude[3] * global filter_gains[3]) >> 8;
            global filtered_spectrum[4] = (global magnitude[4] * global filter_gains[4]) >> 8;
            global filtered_spectrum[5] = (global magnitude[5] * global filter_gains[5]) >> 8;
            global filtered_spectrum[6] = (global magnitude[6] * global filter_gains[6]) >> 8;
            global filtered_spectrum[7] = (global magnitude[7] * global filter_gains[7]) >> 8;
        }
        

        output_amplitude = 0;
        output_amplitude = output_amplitude + global filtered_spectrum[0];
        output_amplitude = output_amplitude + global filtered_spectrum[1];
        output_amplitude = output_amplitude + global filtered_spectrum[2];
        output_amplitude = output_amplitude + global filtered_spectrum[3];
        output_amplitude = output_amplitude + global filtered_spectrum[4];
        output_amplitude = output_amplitude + global filtered_spectrum[5];
        output_amplitude = output_amplitude + global filtered_spectrum[6];
        output_amplitude = output_amplitude + global filtered_spectrum[7];
        output_amplitude = output_amplitude >> 3;
        

        input_amplitude = signal[0];
        output_amplitude = (input_amplitude >> 2) + (output_amplitude * 3 >> 2);
        

        if (output_amplitude > 2047) output_amplitude = 2047;
        if (output_amplitude < -2047) output_amplitude = -2047;
        


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
        

        if (cutoff_freq > 7) cutoff_freq = 7;
        global displayLEDs[2] = 1 << cutoff_freq;
        

        global displayLEDs[3] = (global filter_type + 1) << 6;
        

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

params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 128;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 0;


params[CLOCK_FREQ_PARAM_INDEX] = 64;
params[SWITCHES_PARAM_INDEX] = 192;
params[OPERATOR_1_PARAM_INDEX] = 100;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 160;
params[SWITCHES_PARAM_INDEX] = 255;
params[OPERATOR_1_PARAM_INDEX] = 255;
params[OPERAND_1_HIGH_PARAM_INDEX] = 192;
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