# Bitcrusher

*Create digital distortion effects through bit depth reduction and sample rate downsampling*

## What This Does

Generates digital distortion by reducing the bit depth and sample rate of audio signals, creating characteristic lo-fi artifacts, digital stepping, and harmonic distortion. Perfect for vintage sampler emulation and modern digital textures.

### **Approach: Custom Firmware (Direct Processing)**

This recipe demonstrates **Approach 2: Custom Firmware** - completely bypassing Permut8's delay memory system to process audio samples directly with bit manipulation algorithms.

**Why This Approach?**:
- **Bit crushing** requires sample-by-sample mathematical processing
- **Direct control** over quantization and sample rate algorithms  
- **Custom interface** needed for intuitive bit depth and rate controls
- **Real-time processing** without delay memory dependencies

**Alternative Approaches**:
- **Original operators**: Could use AND operator for bit masking, but lacks sample rate control
- **Operator modification**: Could enhance AND operator, but custom firmware provides better control

### **Interface Architecture**

This effect uses all four instruction operands as custom knob controls:

**Original Interface**: Each operand controlled via scrollable LED displays + bit switches  
**Custom Firmware**: Direct knob controls with custom labels via `panelTextRows`

**Suggested Panel Layout**:
```impala
readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "CRUSH |-- BIT DEPTH --| |--- DRY/WET ---|",  // params[3] & params[6]
    "",
    "",
    "",
    "CRUSH |-- RATE DIV ---| |--- GAIN -----|"   // params[4] & params[7]
};
```

## Quick Reference

**Essential Parameters:**
- `params[3]`: Bit depth (Instruction 1 High Operand, 0-255, controls quantization amount)
- `params[4]`: Sample rate reduction (Instruction 1 Low Operand, 0-255, hold factor) 
- `params[6]`: Dry/wet mix (Instruction 2 High Operand, 0-255, blend control)
- `params[7]`: Output gain (Instruction 2 Low Operand, 0-255, level compensation)

**Key Concepts:** Quantization distortion, sample-and-hold, digital artifacts, aliasing effects

**Common Settings:**
```impala
// Vintage sampler: moderate crushing with character
int vintage_bits = 180, vintage_rate = 60, vintage_mix = 200, vintage_gain = 220

// Lo-fi texture: heavy digital artifacts
int lofi_bits = 100, lofi_rate = 120, lofi_mix = 180, lofi_gain = 240

// Extreme digital: maximum destruction
int extreme_bits = 30, extreme_rate = 200, extreme_mix = 255, extreme_gain = 200
```

## Complete Code

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Standard global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Parameter values (0-255)
global array displayLEDs[4]     // LED displays

// Simple bitcrusher state
global int hold_left = 0         // Held sample for left channel
global int hold_right = 0        // Held sample for right channel
global int hold_counter = 0      // Counter for sample rate reduction

function process()
locals int bits
locals int rate_div
locals int mix
locals int gain
locals int crushed_left
locals int crushed_right
locals int shift_amount
locals int dry_left
locals int dry_right
locals int wet_left
locals int wet_right
locals int output_left
locals int output_right
{
    loop {
        // Read parameters (Instruction operands)
        bits = ((int)global params[3] >> 4) + 1;        // 1-16 effective bit depth (Instruction 1 High)
        rate_div = ((int)global params[4] >> 3) + 1;    // 1-32 rate division (Instruction 1 Low)
        mix = (int)global params[6];                    // 0-255 dry/wet mix (Instruction 2 High)
        gain = ((int)global params[7] >> 1) + 64;       // 64-191 output gain (Instruction 2 Low)
        
        // Sample rate reduction (hold samples)
        global hold_counter = global hold_counter + 1;
        if (global hold_counter >= rate_div) {
            global hold_counter = 0;
            global hold_left = (int)global signal[0];
            global hold_right = (int)global signal[1];
        }
        
        // Calculate bit reduction for 12-bit audio (-2047 to 2047)
        shift_amount = 12 - bits;                       // Amount to shift for quantization
        if (shift_amount < 0) shift_amount = 0;         // Prevent negative shifts
        if (shift_amount > 11) shift_amount = 11;       // Prevent excessive shifts
        
        // Bit depth reduction through shift quantization
        crushed_left = (global hold_left >> shift_amount) << shift_amount;
        crushed_right = (global hold_right >> shift_amount) << shift_amount;
        
        // Store dry signals
        dry_left = (int)global signal[0];
        dry_right = (int)global signal[1];
        
        // Apply output gain to wet signals
        wet_left = (crushed_left * gain) >> 7;          // Apply gain with scaling
        wet_right = (crushed_right * gain) >> 7;
        
        // Clip gained signals to valid range
        if (wet_left > 2047) wet_left = 2047;
        if (wet_left < -2047) wet_left = -2047;
        if (wet_right > 2047) wet_right = 2047;
        if (wet_right < -2047) wet_right = -2047;
        
        // Mix dry and wet signals
        output_left = ((dry_left * (255 - mix)) + (wet_left * mix)) >> 8;
        output_right = ((dry_right * (255 - mix)) + (wet_right * mix)) >> 8;
        
        // Output final mixed audio
        global signal[0] = output_left;
        global signal[1] = output_right;
        
        // Show activity on LEDs with bounds checking
        global displayLEDs[0] = ((bits - 1) << 4) & 255;      // Show effective bit depth
        global displayLEDs[1] = ((rate_div - 1) << 3) & 255;  // Show rate reduction
        global displayLEDs[2] = mix;                          // Show dry/wet mix
        global displayLEDs[3] = (gain - 64) << 1;             // Show output gain
        
        yield();
    }
}
```

## How It Works

**Bit Depth Reduction**: Uses right-shift quantization to reduce effective bit depth from 12-bit to 1-16 bits, creating digital stepping artifacts.

**Sample Rate Reduction**: Holds samples for multiple cycles (1-32x), creating characteristic stepping and aliasing effects.

**Dry/Wet Mixing**: Blends original signal with crushed signal for controlled intensity.

**Output Gain**: Compensates for level changes caused by bit reduction and provides creative gain staging.

**Parameter Control**:
- **Control 1**: Bit depth (1-16 effective bits) 
- **Control 2**: Sample rate reduction (1-32x)
- **Control 3**: Dry/wet mix (0% = clean, 100% = crushed)
- **Control 4**: Output gain (compensate for level changes)

**LED Feedback**: Shows bit depth, rate reduction, mix level, and output gain.

## Try These Settings

```impala
// Vintage lo-fi (moderate crushing)
params[0] = 128;  // 8-bit depth
params[1] = 64;   // 8x rate reduction  
params[2] = 180;  // 70% wet mix
params[3] = 200;  // +6dB gain compensation

// Extreme digital destruction  
params[0] = 32;   // 2-bit depth
params[1] = 200;  // 25x rate reduction
params[2] = 255;  // 100% wet
params[3] = 255;  // Maximum gain
```
