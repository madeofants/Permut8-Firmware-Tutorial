# Add Controls to Any Effect - Complete Tutorial

## What This Tutorial Does
Learn how to add user controls to any audio effect. We'll take a basic tremolo effect and progressively add 4 different types of controls, explaining each technique so you can apply it to any effect.

## What You'll Learn
- Parameter mapping and scaling techniques
- Different control curve types (linear, exponential, musical)
- How to make controls feel natural and musical
- LED feedback for different parameter types
- Control combinations and interactions

---

## Step 1: Start with a Basic Effect

### 1.1 Create the Base Tremolo
Create `controlled_tremolo.impala` with this simple tremolo effect:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = PARAM_MID                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = PARAM_MAX         // Full LED brightness
const int LED_BRIGHTNESS_HALF = PARAM_SWITCH_THRESHOLD         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

// Tremolo Effect - We'll Add Controls To This
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

global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300

// Tremolo state
global int lfoPhase = 0         // Oscillator phase
global int tremoloRate = 100    // Fixed rate (we'll make this controllable)
global int tremoloDepth = PARAM_MID   // Fixed depth (we'll make this controllable)

function process()
locals int lfoValue, int amplitude
{
    loop {
        // Simple sine wave LFO for tremolo
        // Approximate sine with triangle wave for now
        int lfoValue = 0
        if (lfoPhase < AUDIO_QUARTER_RANGE) {
            lfoValue = (lfoPhase * 2)       // Rising
        } else {
            lfoValue = (AUDIO_FULL_RANGE - lfoPhase) * 2   // Falling  
        }
        
        // Convert to amplitude multiplier (0-PARAM_MAX)
        int amplitude = PARAM_MID + ((lfoValue * tremoloDepth) / AUDIO_FULL_RANGE)
        
        // Apply tremolo to audio
        signal[0] = (signal[0] * amplitude) / PARAM_MAX
        signal[1] = (signal[1] * amplitude) / PARAM_MAX
        
        // Update LFO phase
        lfoPhase = (lfoPhase + tremoloRate) % AUDIO_FULL_RANGE
        
        yield()
    }
}
```

### 1.2 Test the Basic Effect
1. Compile: `PikaCmd.exe -compile controlled_tremolo.impala`
2. Load: `patch controlled_tremolo.gazl`
3. You should hear a fixed tremolo effect (volume going up and down)

**What we have:** A working tremolo with fixed rate and depth. Now let's make it controllable!

---

## Step 2: Add Linear Rate Control

### 2.1 Understanding Parameter Mapping
Knobs give us values from 0-PARAM_MAX. We need to map this to useful tremolo rates:
- 0 = very slow (almost stopped)
- PARAM_MAX = very fast (rapid tremolo)

### 2.2 Add Rate Control
Replace the `process()` function:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = PARAM_MID                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = PARAM_MAX         // Full LED brightness
const int LED_BRIGHTNESS_HALF = PARAM_SWITCH_THRESHOLD         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

function process()
locals int rateParam, int lfoValue, int amplitude
{
    loop {
        // CONTROL 1: Rate from knob 1 (linear mapping)
        rateParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // Get knob value (0-PARAM_MAX)
        tremoloRate = 10 + (rateParam / 2)  // Map to 10-137 range
        
        // Same tremolo code as before
        int lfoValue = 0
        if (lfoPhase < AUDIO_QUARTER_RANGE) {
            lfoValue = (lfoPhase * 2)
        } else {
            lfoValue = (AUDIO_FULL_RANGE - lfoPhase) * 2
        }
        
        int amplitude = PARAM_MID + ((lfoValue * tremoloDepth) / AUDIO_FULL_RANGE)
        
        signal[0] = (signal[0] * amplitude) / PARAM_MAX
        signal[1] = (signal[1] * amplitude) / PARAM_MAX
        
        lfoPhase = (lfoPhase + tremoloRate) % AUDIO_FULL_RANGE
        
        yield()
    }
}
```

### 2.3 Test Linear Control
1. Compile and load
2. **Turn knob 1:** Rate should change smoothly from slow to fast
3. **Notice:** The control feels linear - each knob movement changes the rate by the same amount

**Linear mapping:** Simple but often not musical. Good for technical parameters.

---

## Step 3: Add Exponential Depth Control

### 3.1 Why Exponential?
Volume and depth controls feel more natural when they use exponential curves because human hearing is logarithmic. A knob that goes from "barely audible" to "full effect" smoothly needs exponential mapping.

### 3.2 Add Exponential Depth Control
Replace `process()` again:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = PARAM_MID                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = PARAM_MAX         // Full LED brightness
const int LED_BRIGHTNESS_HALF = PARAM_SWITCH_THRESHOLD         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

function process()
locals int rateParam, int depthParam, int depthSquared, int lfoValue, int amplitude
{
    loop {
        // CONTROL 1: Rate (linear)
        rateParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        tremoloRate = 10 + (rateParam / 2)
        
        // CONTROL 2: Depth (exponential curve)
        depthParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]  // Get knob value (0-PARAM_MAX)
        
        // Create exponential curve: depth = param^2 / PARAM_MAX
        depthSquared = (depthParam * depthParam) / PARAM_MAX
        tremoloDepth = depthSquared / 2         // Scale to usable range
        
        // Tremolo processing
        int lfoValue = 0
        if (lfoPhase < AUDIO_QUARTER_RANGE) {
            lfoValue = (lfoPhase * 2)
        } else {
            lfoValue = (AUDIO_FULL_RANGE - lfoPhase) * 2
        }
        
        int amplitude = PARAM_MID + ((lfoValue * tremoloDepth) / AUDIO_FULL_RANGE)
        
        signal[0] = (signal[0] * amplitude) / PARAM_MAX
        signal[1] = (signal[1] * amplitude) / PARAM_MAX
        
        lfoPhase = (lfoPhase + tremoloRate) % AUDIO_FULL_RANGE
        
        yield()
    }
}
```

### 3.3 Test Exponential Control
1. Compile and load
2. **Turn knob 2 slowly:** Notice how the first half does very little, then it ramps up quickly
3. **Compare to knob 1:** Linear vs exponential feel

**Exponential mapping:** More natural for intensity/volume controls. The effect "comes alive" as you turn the knob up.

---

## Step 4: Add Musical Frequency Control

### 4.1 Musical vs Technical Frequency
Musicians think in musical intervals (octaves), not linear frequency. A musical frequency control doubles the frequency for each octave.

### 4.2 Add Musical Rate Control
Let's make knob 1 more musical. Replace `process()`:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

function process()
locals int rateParam, int octaves, int musicalRate, int depthParam, int depthSquared, int lfoValue, int amplitude
{
    loop {
        // CONTROL 1: Rate (musical/exponential)
        rateParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        
        // Musical mapping: each 32 knob units = double the rate
        octaves = rateParam / 32                    // 0-7 octaves
        int baseRate = 20                               // Starting rate
        musicalRate = baseRate << (octaves / 2)     // Approximate doubling
        tremoloRate = musicalRate + (rateParam % 32)    // Fine tuning
        
        // CONTROL 2: Depth (exponential) 
        depthParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        depthSquared = (depthParam * depthParam) / PARAM_MAX
        tremoloDepth = depthSquared / 2
        
        // Tremolo processing
        int lfoValue = 0
        if (lfoPhase < AUDIO_QUARTER_RANGE) {
            lfoValue = (lfoPhase * 2)
        } else {
            lfoValue = (AUDIO_FULL_RANGE - lfoPhase) * 2
        }
        
        int amplitude = PARAM_MID + ((lfoValue * tremoloDepth) / AUDIO_FULL_RANGE)
        
        signal[0] = (signal[0] * amplitude) / PARAM_MAX
        signal[1] = (signal[1] * amplitude) / PARAM_MAX
        
        lfoPhase = (lfoPhase + tremoloRate) % AUDIO_FULL_RANGE
        
        yield()
    }
}
```

### 4.3 Test Musical Control
1. Compile and load
2. **Turn knob 1:** Now the rate jumps in musical intervals instead of linear steps
3. **Notice:** More useful musical speeds, easier to find tempo-related rates

**Musical mapping:** Best for frequency/time-based parameters. Matches how musicians think about pitch and tempo relationships.

---

## Step 5: Add Multi-Range Control

### 5.1 Different Ranges for Different Uses
Sometimes you want one knob to access completely different ranges. We'll make knob 3 switch between "subtle" and "extreme" tremolo modes.

### 5.2 Add Mode Switching Control
Replace `process()` with this enhanced version:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

function process()
locals int rateParam, int octaves, int musicalRate, int depthParam, int depthSquared, int modeParam, int finalDepth, int currentMode, int lfoValue, int amplitude
{
    loop {
        // CONTROL 1: Rate (musical)
        rateParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        octaves = rateParam / 32
        int baseRate = 20
        musicalRate = baseRate << (octaves / 2)
        tremoloRate = musicalRate + (rateParam % 32)
        
        // CONTROL 2: Depth (exponential)
        depthParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        depthSquared = (depthParam * depthParam) / PARAM_MAX
        tremoloDepth = depthSquared / 2
        
        // CONTROL 3: Mode switching (multi-range)
        modeParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]  // Get knob value
        
        finalDepth = 0
        if (modeParam < 85) {
            // Mode 1: Subtle (0-33% of knob range)
            finalDepth = tremoloDepth / 4        // Quarter intensity
        } else if (modeParam < 170) {
            // Mode 2: Normal (33-66% of knob range) 
            finalDepth = tremoloDepth            // Normal intensity
        } else {
            // Mode 3: Extreme (66-100% of knob range)
            finalDepth = tremoloDepth * 2        // Double intensity
            if (finalDepth > PARAM_MAX) finalDepth = PARAM_MAX
        }
        
        // Tremolo processing with final depth
        int lfoValue = 0
        if (lfoPhase < AUDIO_QUARTER_RANGE) {
            lfoValue = (lfoPhase * 2)
        } else {
            lfoValue = (AUDIO_FULL_RANGE - lfoPhase) * 2
        }
        
        int amplitude = PARAM_MID + ((lfoValue * finalDepth) / AUDIO_FULL_RANGE)
        
        signal[0] = (signal[0] * amplitude) / PARAM_MAX
        signal[1] = (signal[1] * amplitude) / PARAM_MAX
        
        lfoPhase = (lfoPhase + tremoloRate) % AUDIO_FULL_RANGE
        
        yield()
    }
}
```

### 5.3 Test Multi-Range Control
1. Compile and load
2. **Test knob 3 in three positions:**
   - Left third: Subtle tremolo
   - Middle third: Normal tremolo  
   - Right third: Extreme tremolo
3. **Adjust knob 2** in each mode to feel the different intensity ranges

**Multi-range mapping:** Perfect for "character" or "mode" controls. One knob accesses completely different behaviors.

---

## Step 6: Add Smart LED Feedback

### 6.1 LED Feedback Strategy
Different control types need different LED feedback:
- Rate: Moving pattern
- Depth: Intensity
- Mode: Position indicator

### 6.2 Complete Code with LED Feedback
Replace `process()` one final time:

```impala
function process()
locals int rateParam, int octaves, int musicalRate, int depthParam, int depthSquared, int modeParam, int finalDepth, int currentMode, int lfoValue, int amplitude, int ratePosition, int depthLEDs, int activity
{
    loop {
        // CONTROL 1: Rate (musical)
        rateParam = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        octaves = rateParam / 32
        int baseRate = 20
        musicalRate = baseRate << (octaves / 2)
        tremoloRate = musicalRate + (rateParam % 32)
        
        // CONTROL 2: Depth (exponential)
        depthParam = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        depthSquared = (depthParam * depthParam) / PARAM_MAX
        tremoloDepth = depthSquared / 2
        
        // CONTROL 3: Mode (multi-range)
        modeParam = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        finalDepth = 0
        currentMode = 0
        
        if (modeParam < 85) {
            finalDepth = tremoloDepth / 4
            currentMode = 1  // Subtle mode
        } else if (modeParam < 170) {
            finalDepth = tremoloDepth
            currentMode = 2  // Normal mode
        } else {
            finalDepth = tremoloDepth * 2
            if (finalDepth > PARAM_MAX) finalDepth = PARAM_MAX
            currentMode = 3  // Extreme mode
        }
        
        // Tremolo processing
        int lfoValue = 0
        if (lfoPhase < AUDIO_QUARTER_RANGE) {
            lfoValue = (lfoPhase * 2)
        } else {
            lfoValue = (AUDIO_FULL_RANGE - lfoPhase) * 2
        }
        
        int amplitude = PARAM_MID + ((lfoValue * finalDepth) / AUDIO_FULL_RANGE)
        
        signal[0] = (signal[0] * amplitude) / PARAM_MAX
        signal[1] = (signal[1] * amplitude) / PARAM_MAX
        
        // LED FEEDBACK for different control types
        
        // LED 1: Rate visualization (moving dot)
        ratePosition = (lfoPhase / 8192) % 8    // 0-7 position
        displayLEDs[0] = 1 << ratePosition
        
        // LED 2: Depth visualization (intensity bar)
        depthLEDs = 0
        if (finalDepth > 200) depthLEDs = 0xFF      // All 8 LEDs
        else if (finalDepth > 150) depthLEDs = 0x7F // 7 LEDs
        else if (finalDepth > 100) depthLEDs = 0x3F // 6 LEDs
        else if (finalDepth > 70) depthLEDs = 0x1F  // 5 LEDs
        else if (finalDepth > 50) depthLEDs = 0x0F  // 4 LEDs
        else if (finalDepth > 30) depthLEDs = 0x07  // 3 LEDs
        else if (finalDepth > 15) depthLEDs = 0x03  // 2 LEDs
        else if (finalDepth > 5) depthLEDs = 0x01   // 1 LED
        displayLEDs[1] = depthLEDs
        
        // LED 3: Mode visualization (position indicator)
        if (currentMode == 1) displayLEDs[2] = 0x07        // First 3 LEDs
        else if (currentMode == 2) displayLEDs[2] = 0x38   // Middle 3 LEDs  
        else displayLEDs[2] = 0xC0                          // Last 2 LEDs
        
        // LED 4: Combined activity (flashing with tremolo)
        activity = (amplitude > 150) ? 0xFF : 0x00
        displayLEDs[3] = activity
        
        lfoPhase = (lfoPhase + tremoloRate) % AUDIO_FULL_RANGE
        
        yield()
    }
}
```

### 6.3 Test Complete Control System
1. Compile and load final version
2. **Watch LEDs while adjusting controls:**
   - LED 1: Shows tremolo rate as moving dot
   - LED 2: Shows depth as bar graph
   - LED 3: Shows mode as position
   - LED 4: Flashes with the tremolo
3. **Try all combinations** to see how the controls interact

---

## Step 7: Understanding Control Design Principles

### 7.1 Summary of Techniques You Learned

| Control Type | When to Use | Formula | Example |
|-------------|-------------|---------|---------|
| **Linear** | Technical parameters | `output = min + (param * range / PARAM_MAX)` | Filter cutoff frequency |
| **Exponential** | Volume/intensity | `output = (param * param) / PARAM_MAX` | Effect depth, gain |
| **Musical** | Frequency/tempo | `output = base << (param / steps)` | LFO rate, delay time |
| **Multi-range** | Mode switching | `if/else` ranges | Character, algorithm select |

### 7.2 LED Feedback Patterns

| Pattern | Code | Best For |
|---------|------|----------|
| **Moving dot** | `1 << position` | Rate, position, time |
| **Bar graph** | `(1 << count) - 1` | Intensity, level, amount |
| **Position** | Fixed patterns | Mode, selection, state |
| **Activity** | Flash on signal | Processing activity |

### 7.3 Control Interaction Guidelines
- **Independent controls:** Each knob does one thing clearly
- **Multiplicative effects:** Depth × mode works well
- **Avoid conflicts:** Don't let controls fight each other
- **Provide feedback:** User should see what each control does

---

## Apply These Techniques to Any Effect

### 7.4 Universal Control Pattern
You can add controls to ANY effect using this pattern:

```impala
// ===== STANDARD PERMUT8 CONSTANTS =====

// Parameter System Constants
const int PARAM_MAX = 255                    // Maximum knob/parameter value (8-bit)
const int PARAM_MIN = 0                      // Minimum knob/parameter value
const int PARAM_MID = 128                    // Parameter midpoint for bipolar controls
const int PARAM_SWITCH_THRESHOLD = 127       // Boolean parameter on/off threshold

// Audio Sample Range Constants (12-bit signed audio)
const int AUDIO_MAX = 2047                   // Maximum audio sample value (+12-bit)
const int AUDIO_MIN = -2047                  // Minimum audio sample value (-12-bit)
const int AUDIO_ZERO = 0                     // Audio silence/center value

// Sample Rate Constants
const int SAMPLE_RATE_44K1 = 44100          // Standard audio sample rate (Hz)
const int SAMPLE_RATE_HALF = 22050          // Half sample rate (0.5 second buffer at 44.1kHz)
const int SAMPLE_RATE_QUARTER = 11025       // Quarter sample rate (0.25 second buffer)

// Audio Scaling Constants (16-bit ranges for phase accumulators)
const int AUDIO_FULL_RANGE = 65536          // 16-bit full scale range (0-65535)
const int AUDIO_HALF_RANGE = 32768          // 16-bit half scale (bipolar center)
const int AUDIO_QUARTER_RANGE = 16384       // 16-bit quarter scale (triangle wave peaks)

// Mathematical Constants
const float PI = 3.14159265                 // Mathematical pi constant
const float TWO_PI = 6.28318531             // 2 * pi (full circle radians)
const float PI_OVER_2 = 1.57079633          // pi/2 (quarter circle radians)

// Buffer Size Constants (powers of 2 for efficiency)
const int SMALL_BUFFER = 128                // Small buffer size
const int MEDIUM_BUFFER = 512               // Medium buffer size  
const int LARGE_BUFFER = 1024               // Large buffer size
const int MAX_BUFFER = 2048                 // Maximum buffer size

// Bit Manipulation Constants
const int BITS_PER_BYTE = 8                 // Standard byte size
const int SHIFT_DIVIDE_BY_2 = 1             // Bit shift for divide by 2
const int SHIFT_DIVIDE_BY_4 = 2             // Bit shift for divide by 4
const int SHIFT_DIVIDE_BY_8 = 3             // Bit shift for divide by 8

// LED Display Constants
const int LED_OFF = 0x00                    // All LEDs off
const int LED_ALL_ON = 0xFF                 // All 8 LEDs on
const int LED_SINGLE = 0x01                 // Single LED pattern
const int LED_DOUBLE = 0x03                 // Two LED pattern
const int LED_QUAD = 0x0F                   // Four LED pattern
const int LED_BRIGHTNESS_FULL = 255         // Full LED brightness
const int LED_BRIGHTNESS_HALF = 127         // Half LED brightness

// Musical/Timing Constants
const int STANDARD_BPM = 120                // Standard tempo reference
const int QUARTER_NOTE_DIVISIONS = 4        // Divisions per quarter note
const int SEMITONES_PER_OCTAVE = 12         // Musical semitones in octave
const float A4_FREQUENCY = 440.0            // A4 reference frequency (Hz)

function process()
locals int param1, int param2, int usefulValue1, int usefulValue2
{
    loop {
        // 1. READ PARAMETERS
        param1 = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]  // Get raw knob values
        param2 = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        
        // 2. MAP TO USEFUL RANGES  
        usefulValue1 = mapToRange(param1)    // Apply mapping technique
        usefulValue2 = mapToRange(param2)
        
        // 3. APPLY TO EFFECT
        // ... your effect code using usefulValue1, usefulValue2 ...
        
        // 4. PROVIDE FEEDBACK
        displayLEDs[0] = visualizeParameter(usefulValue1)
        
        yield()
    }
}
```

### 7.5 Quick Reference for Adding Controls

**To any delay effect:**
- Linear: Delay time (0-1000 samples)
- Exponential: Feedback amount  
- Musical: Delay time in musical note values

**To any filter effect:**
- Musical: Cutoff frequency (musical intervals)
- Exponential: Resonance amount
- Linear: Filter type selection

**To any modulation effect:**
- Musical: LFO rate
- Exponential: Modulation depth
- Multi-range: Waveform selection

### 7.6 Testing Your Controls
1. **Does each control do something obvious?**
2. **Do the ranges feel musical and useful?**
3. **Can you see what each control is doing?**
4. **Do the controls work well together?**

---

## What's Next?

### Try These Projects:
1. **Add controls to the delay cookbook recipe** - Apply these techniques to make the delay more controllable
2. **Create a multi-mode filter** - Use multi-range control for low-pass/high-pass/band-pass switching
3. **Build a complex modulation source** - Use all four techniques for a super-flexible LFO

### Learn More:
- 📖 [Make a Delay](../cookbook/audio-effects/make-a-delay.md) - Apply control techniques to delay effects
- 📖 [Control LEDs](../cookbook/visual-feedback/control-leds.md) - Advanced LED feedback patterns
- 📖 [Read Knobs](../cookbook/parameters/read-knobs.md) - More parameter handling techniques

**You now know how to make ANY effect controllable!** These four mapping techniques (linear, exponential, musical, multi-range) plus smart LED feedback will work for any audio effect you want to build.
