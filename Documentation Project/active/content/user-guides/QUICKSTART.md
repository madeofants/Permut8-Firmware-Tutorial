# Permut8 Firmware in 30 Minutes

Get your first custom firmware running on Permut8 in just 30 minutes!

## What is Firmware? (For Complete Beginners)

If you're new to audio programming, here's what you need to know:

### **Firmware vs Plugins**
- **Regular Audio Plugin**: Software that processes audio on your computer
- **Permut8 Firmware**: Code that runs directly on Permut8 hardware for ultra-low latency

### **Why Firmware?**
- **No Computer Latency**: Audio processing happens instantly on dedicated hardware
- **Real-time Performance**: Perfect for live performance and recording
- **Custom Effects**: Create effects that don't exist anywhere else
- **Hardware Integration**: Direct control from knobs and LEDs

### **What You're Actually Doing**
When you write Permut8 firmware, you're creating instructions that tell the Permut8 hardware exactly how to modify audio signals in real-time. Every knob turn, every audio sample, every LED - your code controls it all.

**Think of it like this**: Instead of installing software on your computer, you're programming the brain of a dedicated audio computer that lives inside Permut8.

## Five-Minute Setup

### 1. Check Your Installation
Navigate to your Permut8 Firmware Code directory and verify you have:
```
Permut8 Firmware Code/
├── PikaCmd.exe           # The Impala compiler
├── ringmod_code.impala   # Example firmware
└── linsub_code.impala    # Example firmware
```

### 2. Test the Compiler
Open a command prompt/terminal in this directory and run:
```bash
PikaCmd.exe -compile ringmod_code.impala
```

You should see `ringmod_code.gazl` created - that's your compiled firmware!

### 3. Create and Load Firmware Bank
1. Open Permut8 in your DAW
2. Create a firmware bank:
   - Package your `ringmod_code.gazl` into `ringmod.p8bank`
   - Add preset configuration (A0: "Ring Modulator")
3. Load bank: File → Load Bank → `ringmod.p8bank`
4. Select A0 preset

**You just loaded custom firmware!** The ring modulator is now running.

## Your First Firmware (10 minutes)

Let's create a simple bit crusher from scratch.

### 1. Create a New File
Create `bitcrush.impala` with this code:

```impala
// Bit Crusher - Your First Permut8 Firmware
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

// Required native function declarations
extern native yield             // Return control to Permut8 audio engine

// Panel text (optional but cool!)
readonly array panelTextRows[8] = {
    "",
    "BIT |-------- CRUSH AMOUNT (MORE BITS = LESS CRUSH) --------|",
    "",
    "",
    "",
    "",
    "",
    ""
}

// Global variables
global array signal[2]          // Left/Right audio samples
global array params[8]          // Knob values
global array displayLEDs[4]     // LED displays

// Main processing function
function process()
locals int bits, int shift, int mask
{
    loop {
        // Read bit depth from first knob (0-255 mapped to 1-12 bits)
        bits = ((int) global params[3] >> 5) + 1;  // 1-8 bits
        shift = 12 - bits;
        mask = 0xFFF0 << shift;
        
        // Light up LEDs to show bit depth
        global displayLEDs[0] = 1 << (bits - 1);
        
        // Process audio: reduce bit depth
        global signal[0] = ((int) global signal[0]) & mask;
        global signal[1] = ((int) global signal[1]) & mask;
        
        // Return control to Permut8
        yield();
    }
}
```

### 2. Compile Your Firmware
```bash
PikaCmd.exe -compile bitcrush.impala
```

### 3. Create Firmware Bank
Package your compiled firmware for distribution:
```
bitcrush.p8bank: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Light Crush", Operator1: "2" }
        A1: { Name: "Heavy Crush", Operator1: "6" }
    }
    Firmware: {
        Name: "bitcrush"
        Code: { /* compiled bitcrush.gazl */ }
    }
}
```

### 4. Load and Test
1. Load bank: File → Load Bank → `bitcrush.p8bank`
2. Select A0 preset (Light Crush) or A1 (Heavy Crush)
3. Play some audio through Permut8
4. Turn the first knob - hear the bit crushing!

**Congratulations!** You just created working DSP firmware. The first knob now controls bit depth, creating that classic lo-fi digital sound.

## Modify Existing Firmware (15 minutes)

Let's add LED animation to the ring modulator.

### 1. Copy the Original
Make a copy of `ringmod_code.impala` called `ringmod_leds.impala`

### 2. Find the LED Code
Look for this line (around line 272):
```impala
global displayLEDs[2] = 0x01 << ((cosL + 0x8000) >> (16 - 3));
```

### 3. Add Rainbow LED Animation
Replace that line with:
```impala
// Rainbow LED animation synced to modulation
global displayLEDs[0] = 0x01 << ((cosL + 0x8000) >> (16 - 3));
global displayLEDs[1] = 0x01 << ((cosR + 0x8000) >> (16 - 3));
global displayLEDs[2] = 0x01 << (((cosL + cosR) + 0x10000) >> (17 - 3));
global displayLEDs[3] = global displayLEDs[0] | global displayLEDs[1];
```

### 4. Compile and Load
```bash
PikaCmd.exe -compile ringmod_leds.impala
```
Load bank: File → Load Bank → `ringmod_leds.p8bank`

Now all four LED displays dance with the ring modulation!

### 5. Try More Modifications
- Change delay times: Find `delayL` and `delayR` calculations
- Adjust modulation shape: Look for the `cosTable` 
- Add parameter smoothing: Implement interpolation in `update()`

## What's Next?

### **New to Audio Programming?** Start with the foundation:
1. 📖 [How DSP Affects Sound](../cookbook/fundamentals/how-dsp-affects-sound.md) - Understand how code creates audio effects (20 min)
2. 📖 [Getting Audio In and Out](../tutorials/getting-audio-in-and-out.md) - Foundation I/O tutorial (10 min)
3. 📖 [Your First Distortion Effect](../cookbook/fundamentals/simplest-distortion.md) - Progressive effect building (15 min)

### **Ready for More Effects?** Based on what you just did:

**Created a bit crusher?** → Try these effects next:
- 📖 [Basic Filter](../cookbook/fundamentals/basic-filter.md) - Add resonance
- 📖 [Bitcrusher](../cookbook/audio-effects/bitcrusher.md) - More lo-fi options
- 📖 [Parameter Smoothing](../cookbook/parameters/parameter-smoothing.md) - Remove clicks

**Modified the ring mod?** → Explore these:
- 📖 [Control LEDs](../cookbook/visual-feedback/control-leds.md) - More patterns
- 📖 [Sync to Tempo](../cookbook/timing/sync-to-tempo.md) - Beat-synced effects
- 📖 [Make a Delay](../cookbook/audio-effects/make-a-delay.md) - Use the memory buffer

### **Understanding Permut8 Architecture:**

**Which firmware type should you choose?**
- **Full Patches** (like our bit crusher): Replace entire DSP engine, process audio samples directly
- **Mod Patches** (like linsub): Modify built-in operators, manipulate memory positions

📖 [Mod vs Full Architecture Guide](../tutorials/mod-vs-full-architecture-guide.md) - Critical decision guidance

### **Professional Development:**
- 📖 [Complete Development Workflow](../tutorials/complete-development-workflow.md) - Systematic methodology
- 📖 [Debug Your Plugin](../tutorials/debug-your-plugin.md) - Essential troubleshooting

### Quick Tips:
- `global signal[0]` = left channel, `global signal[1]` = right channel
- Audio samples range from -2047 to 2047 (12-bit)
- `yield()` returns control to Permut8 after each sample
- `global params[]` contains all knob values (0-255)

### Problems?
- Firmware won't compile? Check for missing semicolons
- No sound? Make sure you called `yield()` in your loop
- LEDs not working? Values should be 8-bit (0-255)

---

**Ready for more?** The cookbook has 24+ ready-to-use recipes. Each one is complete, working code you can copy and modify. Start with any effect that interests you!