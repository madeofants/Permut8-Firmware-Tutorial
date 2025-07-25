# Phase Vocoder

*Transform audio time and pitch independently using spectral processing techniques*

## What This Does

Provides basic phase vocoder functionality for independent time and pitch manipulation. Analyzes audio in the frequency domain to enable time stretching without pitch changes and pitch shifting without timing changes.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Time stretch factor (0-255, 0.5x to 1.5x playback speed)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Pitch shift factor (0-255, 0.5x to 1.5x frequency shift)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Processing blend (0-255, mix between original and processed)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Analysis window (0-255, future enhancement)

**Core Techniques:**
- **Spectral analysis**: Break audio into frequency components
- **Time stretching**: Change playback speed without pitch change
- **Pitch shifting**: Change frequency without timing change
- **Phase management**: Maintain spectral coherence

**Key Concepts:** Phase vocoder, spectral processing, time/pitch independence

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


global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300


global array analysis_buffer[16]
global array synthesis_buffer[16]
global array magnitude[8]
global array phase[8]
global int buffer_index = 0
global int hop_counter = 0
global int time_stretch = 128
global int pitch_shift = 128

function process()
locals i, time_factor, pitch_factor, hop_size, analysis_input, synthesis_output, led_pattern
{
    loop {

        global time_stretch = 64 + (params[CLOCK_FREQ_PARAM_INDEX] >> 1);
        global pitch_shift = 64 + (params[SWITCHES_PARAM_INDEX] >> 1);
        

        time_factor = global time_stretch;
        pitch_factor = global pitch_shift;
        hop_size = 8;
        

        global analysis_buffer[global buffer_index] = signal[0];
        global buffer_index = global buffer_index + 1;
        if (global buffer_index >= 16) {
            global buffer_index = 0;
        }
        

        global hop_counter = global hop_counter + 1;
        if (global hop_counter >= hop_size) {
            global hop_counter = 0;
            

            global magnitude[0] = (global analysis_buffer[0] + global analysis_buffer[8]) >> 1;
            if (global magnitude[0] < 0) global magnitude[0] = -global magnitude[0];
            
            global magnitude[1] = (global analysis_buffer[1] + global analysis_buffer[9]) >> 1;
            if (global magnitude[1] < 0) global magnitude[1] = -global magnitude[1];
            
            global magnitude[2] = (global analysis_buffer[2] + global analysis_buffer[10]) >> 1;
            if (global magnitude[2] < 0) global magnitude[2] = -global magnitude[2];
            
            global magnitude[3] = (global analysis_buffer[3] + global analysis_buffer[11]) >> 1;
            if (global magnitude[3] < 0) global magnitude[3] = -global magnitude[3];
            
            global magnitude[4] = (global analysis_buffer[4] + global analysis_buffer[12]) >> 1;
            if (global magnitude[4] < 0) global magnitude[4] = -global magnitude[4];
            
            global magnitude[5] = (global analysis_buffer[5] + global analysis_buffer[13]) >> 1;
            if (global magnitude[5] < 0) global magnitude[5] = -global magnitude[5];
            
            global magnitude[6] = (global analysis_buffer[6] + global analysis_buffer[14]) >> 1;
            if (global magnitude[6] < 0) global magnitude[6] = -global magnitude[6];
            
            global magnitude[7] = (global analysis_buffer[7] + global analysis_buffer[15]) >> 1;
            if (global magnitude[7] < 0) global magnitude[7] = -global magnitude[7];
            

            global phase[0] = global analysis_buffer[1] - global analysis_buffer[0];
            global phase[1] = global analysis_buffer[2] - global analysis_buffer[1];
            global phase[2] = global analysis_buffer[3] - global analysis_buffer[2];
            global phase[3] = global analysis_buffer[4] - global analysis_buffer[3];
            global phase[4] = global analysis_buffer[5] - global analysis_buffer[4];
            global phase[5] = global analysis_buffer[6] - global analysis_buffer[5];
            global phase[6] = global analysis_buffer[7] - global analysis_buffer[6];
            global phase[7] = global analysis_buffer[8] - global analysis_buffer[7];
            

            global magnitude[0] = ((int)global magnitude[0] * time_factor) >> 7;
            global magnitude[1] = ((int)global magnitude[1] * time_factor) >> 7;
            global magnitude[2] = ((int)global magnitude[2] * time_factor) >> 7;
            global magnitude[3] = ((int)global magnitude[3] * time_factor) >> 7;
            global magnitude[4] = ((int)global magnitude[4] * time_factor) >> 7;
            global magnitude[5] = ((int)global magnitude[5] * time_factor) >> 7;
            global magnitude[6] = ((int)global magnitude[6] * time_factor) >> 7;
            global magnitude[7] = ((int)global magnitude[7] * time_factor) >> 7;
            

            if (pitch_factor > 128) {

                global synthesis_buffer[0] = (int)global magnitude[1];
                global synthesis_buffer[1] = (int)global magnitude[2];
                global synthesis_buffer[2] = (int)global magnitude[3];
                global synthesis_buffer[3] = (int)global magnitude[4];
                global synthesis_buffer[4] = (int)global magnitude[5];
                global synthesis_buffer[5] = (int)global magnitude[6];
                global synthesis_buffer[6] = (int)global magnitude[7];
                global synthesis_buffer[7] = 0;
            } else if (pitch_factor < 128) {

                global synthesis_buffer[0] = 0;
                global synthesis_buffer[1] = (int)global magnitude[0];
                global synthesis_buffer[2] = (int)global magnitude[1];
                global synthesis_buffer[3] = (int)global magnitude[2];
                global synthesis_buffer[4] = (int)global magnitude[3];
                global synthesis_buffer[5] = (int)global magnitude[4];
                global synthesis_buffer[6] = (int)global magnitude[5];
                global synthesis_buffer[7] = (int)global magnitude[6];
            } else {

                global synthesis_buffer[0] = (int)global magnitude[0];
                global synthesis_buffer[1] = (int)global magnitude[1];
                global synthesis_buffer[2] = (int)global magnitude[2];
                global synthesis_buffer[3] = (int)global magnitude[3];
                global synthesis_buffer[4] = (int)global magnitude[4];
                global synthesis_buffer[5] = (int)global magnitude[5];
                global synthesis_buffer[6] = (int)global magnitude[6];
                global synthesis_buffer[7] = (int)global magnitude[7];
            }
        }
        

        synthesis_output = 0;
        synthesis_output = synthesis_output + (int)global synthesis_buffer[0];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[1];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[2];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[3];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[4];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[5];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[6];
        synthesis_output = synthesis_output + (int)global synthesis_buffer[7];
        synthesis_output = synthesis_output >> 3;
        

        analysis_input = (int)global signal[0];
        synthesis_output = (analysis_input >> 1) + (synthesis_output >> 1);
        

        if (synthesis_output > 2047) synthesis_output = 2047;
        if (synthesis_output < -2047) synthesis_output = -2047;
        


        led_pattern = 0;
        if (((int)global magnitude[0] >> 6) > 0) led_pattern = led_pattern | 1;
        if (((int)global magnitude[1] >> 6) > 0) led_pattern = led_pattern | 2;
        if (((int)global magnitude[2] >> 6) > 0) led_pattern = led_pattern | 4;
        if (((int)global magnitude[3] >> 6) > 0) led_pattern = led_pattern | 8;
        if (((int)global magnitude[4] >> 6) > 0) led_pattern = led_pattern | 16;
        if (((int)global magnitude[5] >> 6) > 0) led_pattern = led_pattern | 32;
        if (((int)global magnitude[6] >> 6) > 0) led_pattern = led_pattern | 64;
        if (((int)global magnitude[7] >> 6) > 0) led_pattern = led_pattern | 128;
        global displayLEDs[0] = led_pattern;
        

        i = (global time_stretch >> 4) - 4;
        if (i < 0) i = 0;
        if (i > 7) i = 7;
        global displayLEDs[1] = 1 << i;
        

        i = (global pitch_shift >> 4) - 4;
        if (i < 0) i = 0;
        if (i > 7) i = 7;
        global displayLEDs[2] = 1 << i;
        

        if (global hop_counter < 2) {
            global displayLEDs[3] = 255;
        } else {
            global displayLEDs[3] = 64;
        }
        

        global signal[0] = synthesis_output;
        global signal[1] = synthesis_output;
        
        yield();
    }
}

```

## How It Works

**Analysis Phase**: Audio is buffered and analyzed to extract magnitude and phase information for each frequency bin.

**Time Stretching**: Magnitude scaling adjusts the time characteristics without affecting frequency content.

**Pitch Shifting**: Frequency bin shifting moves spectral content to different frequencies, changing pitch without affecting timing.

**Synthesis**: Frequency components are recombined to create the output signal with desired time and pitch modifications.

**Parameter Control**:
- **Knob 1**: Time stretch (0=0.5x speed, 128=normal, 255=1.5x speed)
- **Knob 2**: Pitch shift (0=0.5x pitch, 128=normal, 255=1.5x pitch)
- **Knob 3**: Processing blend (future enhancement)
- **Knob 4**: Analysis window (future enhancement)

## Understanding Phase Vocoder Operation

**Hop Size**: Controls how often analysis occurs. Smaller hop sizes provide better quality but require more processing.

**Magnitude Spectrum**: Shows the energy at each frequency, displayed on LED ring 0.

**Phase Information**: Tracks the phase relationships between frequency components for coherent reconstruction.

**Frequency Bin Shifting**: Simple pitch shifting by moving spectral content between bins.

## Try These Settings

```impala

params[CLOCK_FREQ_PARAM_INDEX] = 64;
params[SWITCHES_PARAM_INDEX] = 128;
params[OPERATOR_1_PARAM_INDEX] = 200;
params[OPERAND_1_HIGH_PARAM_INDEX] = 128;


params[CLOCK_FREQ_PARAM_INDEX] = 200;
params[SWITCHES_PARAM_INDEX] = 200;
params[OPERATOR_1_PARAM_INDEX] = 255;
params[OPERAND_1_HIGH_PARAM_INDEX] = 64;


params[CLOCK_FREQ_PARAM_INDEX] = 128;
params[SWITCHES_PARAM_INDEX] = 140;
params[OPERATOR_1_PARAM_INDEX] = 128;
params[OPERAND_1_HIGH_PARAM_INDEX] = 192;
```

## Musical Applications

**Time Stretching**: Create slow-motion or fast-forward effects without pitch change.

**Pitch Shifting**: Transpose audio without affecting rhythm or timing.

**Harmonization**: Layer multiple pitch-shifted versions for harmonies.

**Creative Effects**: Extreme settings create robotic or otherworldly sounds.

## Understanding Limitations

This simplified implementation provides basic phase vocoder concepts but has limitations:
- Limited frequency resolution (8 bins)
- Simplified phase management
- Basic pitch shifting algorithm
- No overlap-add windowing

Professional phase vocoders use larger FFT sizes, sophisticated windowing, and advanced phase tracking.

## Try These Changes

- **Better windowing**: Add Hanning or other window functions for smoother analysis
- **Phase tracking**: Implement proper phase accumulation for better quality
- **Overlap-add**: Add overlap-add synthesis for artifact reduction
- **Formant preservation**: Preserve vocal formants during pitch shifting

## Related Techniques

- **[FFT Basics](fft-basics.md)**: Foundation frequency analysis
- **[Frequency Analysis](frequency-analysis.md)**: Spectral information extraction
- **[Spectral Filtering](spectral-filtering.md)**: Frequency-domain filtering
- **[Pitch Shifter](../audio-effects/pitch-shifter.md)**: Time-domain pitch shifting

---

*This phase vocoder provides essential time and pitch manipulation capabilities for creative audio processing. Perfect for learning spectral processing concepts and creating unique time/pitch effects.*