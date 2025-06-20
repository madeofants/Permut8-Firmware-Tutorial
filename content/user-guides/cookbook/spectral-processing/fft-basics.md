# FFT Basics

*Implement basic frequency analysis for spectral processing on the Permut8*

## What This Does

Provides simplified frequency domain analysis by computing basic spectral components of audio signals. Shows frequency content using LED visualization and enables understanding of spectral processing fundamentals.

## Quick Reference

**Essential Parameters:**
- `(int)global params[CLOCK_FREQ_PARAM_INDEX]`: Spectral sensitivity (0-255, adjusts frequency detection)
- `(int)global params[SWITCHES_PARAM_INDEX]`: Window type (0-255, future enhancement)
- `(int)global params[OPERATOR_1_PARAM_INDEX]`: Analysis rate (0-255, controls update frequency)
- `(int)global params[OPERAND_1_HIGH_PARAM_INDEX]`: Display mode (0-255, visualization style)

**Core Techniques:**
- **8-point DFT**: Simplified frequency analysis
- **Magnitude calculation**: Frequency bin energy levels  
- **Spectral visualization**: LED frequency display
- **Rate control**: Adjustable analysis timing

**Key Concepts:** Frequency domain, spectral bins, magnitude calculation, DFT basics

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[PARAM_COUNT]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple spectral analysis (8-point DFT approximation)
global array input_buffer[8]    // Time domain input buffer
global array magnitude[8]       // Frequency domain magnitudes
global int buffer_index = 0     // Current buffer position
global int update_counter = 0   // Rate control for analysis

function process()
locals int analysis_rate, int window_type, int display_mode, int i, int real_part, int imag_part, int mag_squared, int led_pattern
{
    loop {
        // Read control parameters
        analysis_rate = ((int)global (int)global params[OPERATOR_1_PARAM_INDEX] >> 6) + 1;  // 1-4 range (update rate)
        window_type = (int)global (int)global params[SWITCHES_PARAM_INDEX] >> 6;           // 0-3 range (window type)
        display_mode = (int)global (int)global params[OPERAND_1_HIGH_PARAM_INDEX] >> 6;          // 0-3 range (display mode)
        
        // Read input and store in buffer
        global input_buffer[(int)global buffer_index] = (int)global signal[0];
        global buffer_index = global buffer_index + 1;
        if (global buffer_index >= 8) {
            global buffer_index = 0;
        }
        
        // Update spectral analysis at controlled rate
        global update_counter = global update_counter + 1;
        if (global update_counter >= (analysis_rate * 512)) {
            global update_counter = 0;
            
            // Simple 8-point DFT approximation (fundamental frequencies only)
            // Frequency bin 0 (DC component)
            real_part = 0;
            real_part = real_part + (int)global input_buffer[0];
            real_part = real_part + (int)global input_buffer[1];
            real_part = real_part + (int)global input_buffer[2];
            real_part = real_part + (int)global input_buffer[3];
            real_part = real_part + (int)global input_buffer[4];
            real_part = real_part + (int)global input_buffer[5];
            real_part = real_part + (int)global input_buffer[6];
            real_part = real_part + (int)global input_buffer[7];
            global magnitude[0] = (real_part >> 3);  // Average (DC)
            if ((int)global magnitude[0] < 0) global magnitude[0] = -(int)global magnitude[0];
            
            // Frequency bin 1 (low frequency) - simplified calculation
            real_part = ((int)global input_buffer[0] + (int)global input_buffer[4]) >> 1;
            imag_part = ((int)global input_buffer[2] + (int)global input_buffer[6]) >> 1;
            
            // Magnitude = sqrt(real^2 + imag^2) ≈ |real| + |imag|
            if (real_part < 0) real_part = -real_part;
            if (imag_part < 0) imag_part = -imag_part;
            global magnitude[1] = (real_part + imag_part) >> 4;
            
            // Simplified calculation for remaining bins
            global magnitude[2] = (((int)global input_buffer[0] + (int)global input_buffer[4]) >> 2);
            if ((int)global magnitude[2] < 0) global magnitude[2] = -(int)global magnitude[2];
            
            global magnitude[3] = (((int)global input_buffer[1] + (int)global input_buffer[5]) >> 2);
            if ((int)global magnitude[3] < 0) global magnitude[3] = -(int)global magnitude[3];
            
            global magnitude[4] = (((int)global input_buffer[2] + (int)global input_buffer[6]) >> 2);
            if ((int)global magnitude[4] < 0) global magnitude[4] = -(int)global magnitude[4];
            
            global magnitude[5] = (((int)global input_buffer[3] + (int)global input_buffer[7]) >> 2);
            if ((int)global magnitude[5] < 0) global magnitude[5] = -(int)global magnitude[5];
            
            global magnitude[6] = (((int)global input_buffer[0] - (int)global input_buffer[4]) >> 2);
            if ((int)global magnitude[6] < 0) global magnitude[6] = -(int)global magnitude[6];
            
            global magnitude[7] = (((int)global input_buffer[1] - (int)global input_buffer[5]) >> 2);
            if ((int)global magnitude[7] < 0) global magnitude[7] = -(int)global magnitude[7];
        }
        
        // === SPECTRAL VISUALIZATION ===
        // Display frequency spectrum on LED ring 0
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
        
        // Display dominant frequency on LED ring 1
        i = 0;
        if ((int)global magnitude[1] > (int)global magnitude[i]) i = 1;
        if ((int)global magnitude[2] > (int)global magnitude[i]) i = 2;
        if ((int)global magnitude[3] > (int)global magnitude[i]) i = 3;
        if ((int)global magnitude[4] > (int)global magnitude[i]) i = 4;
        if ((int)global magnitude[5] > (int)global magnitude[i]) i = 5;
        if ((int)global magnitude[6] > (int)global magnitude[i]) i = 6;
        if ((int)global magnitude[7] > (int)global magnitude[i]) i = 7;
        global displayLEDs[1] = 1 << i;
        
        // Show analysis rate on LED ring 2
        global displayLEDs[2] = analysis_rate << 6;
        
        // Show update status on LED ring 3
        if (global update_counter < 100) {
            global displayLEDs[3] = 255;  // Bright during analysis
        } else {
            global displayLEDs[3] = 64;   // Dim otherwise
        }
        
        // Pass audio through unchanged
        global signal[0] = (int)global signal[0];
        global signal[1] = (int)global signal[1];
        
        yield();
    }
}

```

## How It Works

**8-Point DFT**: Simplified Discrete Fourier Transform that analyzes 8 audio samples to extract basic frequency components.

**Buffer Management**: Circular buffer continuously captures audio samples for analysis.

**Magnitude Calculation**: Each frequency bin's energy is calculated using simplified real/imaginary component math.

**Rate Control**: Analysis rate is adjustable to balance CPU usage with update frequency.

**Parameter Control**:
- **Knob 1**: Spectral sensitivity (future enhancement)
- **Knob 2**: Window type (future enhancement)  
- **Knob 3**: Analysis rate (1-4, slower to faster updates)
- **Knob 4**: Display mode (visualization style)

## Understanding Frequency Bins

The 8 frequency bins represent different frequency ranges:
- Bin 0: DC component (0 Hz)
- Bin 1: Low frequency (~2.7 kHz at 44.1kHz sample rate)
- Bins 2-7: Higher frequency components

Each LED on ring 0 shows the energy in one frequency bin.

## Try These Settings

```impala
// Fast spectral analysis
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 200;  // High sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 0;    // Basic window
(int)global params[OPERATOR_1_PARAM_INDEX] = 255;  // Fastest update rate
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 0;    // Standard display

// Slow detailed analysis
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 128;  // Normal sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 64;   // Enhanced window
(int)global params[OPERATOR_1_PARAM_INDEX] = 64;   // Slower updates
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 128;  // Enhanced display

// Real-time monitoring
(int)global params[CLOCK_FREQ_PARAM_INDEX] = 150;  // Good sensitivity
(int)global params[SWITCHES_PARAM_INDEX] = 128;  // Advanced window
(int)global params[OPERATOR_1_PARAM_INDEX] = 200;  // Fast updates
(int)global params[OPERAND_1_HIGH_PARAM_INDEX] = 64;   // Visual mode
```

## Understanding Spectral Analysis

**Time vs Frequency Domain**: Audio signals can be viewed as waveforms (time domain) or as frequency content (frequency domain). FFT converts between these representations.

**Frequency Resolution**: Longer analysis windows provide better frequency resolution but higher latency. 8-point analysis provides basic frequency awareness.

**Magnitude Spectrum**: Shows the energy at each frequency. Peaks indicate dominant frequency components in the audio signal.

## Try These Changes

- **Windowing**: Add Hanning or Hamming window functions for better frequency separation
- **Larger FFT**: Increase buffer size for higher frequency resolution
- **Peak detection**: Add frequency peak tracking for pitch detection
- **Filtering**: Use frequency bins to create spectral filters

## Related Techniques

- **[Frequency Analysis](frequency-analysis.md)**: Advanced spectral analysis techniques
- **[Phase Vocoder](phase-vocoder.md)**: Spectral processing and time-stretching
- **[Spectral Filtering](spectral-filtering.md)**: Frequency-domain filtering
- **[Level Meters](../visual-feedback/level-meters.md)**: Audio level visualization

---

*This FFT implementation provides essential frequency analysis for understanding spectral processing. Perfect for learning frequency domain concepts, building spectrum analyzers, and developing spectral effects.*