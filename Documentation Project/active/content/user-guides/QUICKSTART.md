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

**If you get an error**, try this instead:
```bash
.\PikaCmd.exe impala.pika compile ringmod_code.impala ringmod_code.gazl
```

You should see `ringmod_code.gazl` created - that's your compiled firmware!

**Why the different commands?** See [Compiler Troubleshooting Guide](../tutorials/compiler-troubleshooting-guide.md) for the technical explanation.

### 3. Create and Load Firmware Bank
1. Open Permut8 in your DAW
2. Create a firmware bank:
   - Package your `ringmod_code.gazl` into `ringmod.p8bank`
   - Add preset configuration (A0: "Ring Modulator")
3. Load bank: File → Load Bank → `ringmod.p8bank`
4. Select A0 preset

**You just loaded custom firmware!** The ring modulator is now running.

## Your First Firmware (15 minutes)

Let's create a simple bit crusher and understand how Permut8's operator system works.

### **Understanding Permut8's Core System**

Before we build, let's understand what makes Permut8 special:

**The Heart**: 128 kilowords of delay memory with moving read/write heads
- **Write position (red dot)**: Where incoming audio is stored
- **Read positions (green dots)**: Where audio is played back from
- **Two instructions**: Manipulate the read positions to create effects

**How Effects Work**: All Permut8 effects come from creatively moving where audio is read from memory:
- **Delays**: Read from behind the write position
- **Pitch effects**: Read at different speeds than writing  
- **Modulation**: Constantly move the read positions
- **Our bitcrusher**: Will use **custom firmware** to bypass this system and process audio directly

**Original vs Custom Firmware**:
- **Original**: Use operators (AND, MUL, OSC, etc.) + operands to manipulate read positions
- **Custom**: Take complete control and implement any algorithm you want

### 1. Create a New File
Create `bitcrush.impala` with this code:

**Bit Crusher - Your First Permut8 Firmware**

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield

readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "BIT |------ CRUSH AMOUNT (INSTRUCTION 1) ------|",
    "",
    "",
    "",
    ""
}

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
locals int bits, int shift, int mask
{
    loop {
        bits = ((int) global params[3] >> 5) + 1;
        shift = 12 - bits;
        mask = 0xFFF0 << shift;
        
        global displayLEDs[0] = 1 << (bits - 1);
        
        global signal[0] = ((int) global signal[0]) & mask;
        global signal[1] = ((int) global signal[1]) & mask;
        
        yield();
    }
}
```

**Interface Architecture**: This custom firmware demonstrates Permut8's interface override system:

- **Original Interface**: Instruction 1 High Operand (`params[3]`) set via switches/LED display (0-255)
- **Custom Override**: Same parameter becomes direct knob control with custom label
- **Visual Transform**: `panelTextRows[3]` replaces hex display with "CRUSH AMOUNT" 
- **Data Flow**: User knob → `params[3]` → bit depth calculation → LED feedback

The parameter access is identical (`params[3]`), but the user experience is completely transformed.

### 2. Compile Your Firmware
```bash
PikaCmd.exe -compile bitcrush.impala
```

**If that doesn't work**, use the full command:
```bash
.\PikaCmd.exe impala.pika compile bitcrush.impala bitcrush.gazl
```

### 3. Create Firmware Bank

**Step 3a: Clean the GAZL File**
Before creating the bank, you need to clean the compiled GAZL file:

1. **Open `bitcrush.gazl`** in a text editor
2. **Remove the compiler comment line** (if present):
   ```
   ; Compiled with Impala version 1.0
   ```
3. **Remove any separator lines** like:
   ```
   ;-----------------------------------------------------------------------------
   ```
4. **Keep only the pure assembly code**

**Step 3b: Create the Bank File**
Create `bitcrush.p8bank` with this **exact format** (note the header):
```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Subtle Bit Reduction", Operator1: "2" }
        A1: { Name: "Lo-Fi Crunch", Operator1: "6" }
        A2: { Name: "Extreme Decimation", Operator1: "8" }
        A3: { Name: "Clean High-Res", Operator1: "0" }
    }
    Firmware: {
        Name: "bitcrush"
        Code: {
[PASTE YOUR CLEANED GAZL CONTENT HERE]
 }
    }
}
```

### **Understanding the Operators in Your Presets**

You might notice each preset has an `Operator1` value. Here's what they do:

**What These Numbers Mean**:
- These are **operator codes** that would normally control how Permut8 manipulates read positions
- **Our custom firmware ignores them** - we're doing direct audio processing instead
- **They're required** for proper bank format, but won't affect our bitcrusher

**Normal Permut8 Operators**:
- **Operator1: "0"** = NOP (No Operation - bypass)
- **Operator1: "2"** = MUL (Multiply - changes pitch/speed)  
- **Operator1: "6"** = XOR (Bit manipulation of read positions)
- **Operator1: "8"** = SUB (Subtract - creates delays)

**Why This Matters**: Understanding these helps you:
1. **Design better custom firmware** - Know what users expect
2. **Mix approaches** - Combine original operators with custom processing
3. **Learn effect building** - See how Permut8 naturally thinks about audio

### 3. Prepare GAZL for Bank
**Remove the first line** from your compiled `bitcrush.gazl`:
1. Open `bitcrush.gazl` in any text editor
2. Delete the first line: `; Compiled with Impala version 1.0`
3. Save the file

### 4. Load and Test Your Bitcrusher

1. **Load the bank**: File → Load Bank → `bitcrush.p8bank`
2. **Select a preset** to start with
3. **Play audio** through Permut8
4. **Turn the knob** to hear the bitcrushing effect!

## How to Use Your Bitcrusher

### **What Just Happened?**
Your custom firmware **completely bypassed** Permut8's normal operator system:

**Normal Permut8 Flow**:
```
Audio Input → Delay Memory → [Operators manipulate read positions] → Audio Output
```

**Your Custom Bitcrusher Flow**:
```
Audio Input → [Direct bit manipulation in code] → Audio Output
```

**Why This Matters**: You took **complete control** of the audio processing instead of using Permut8's built-in read/write head manipulation system.

### **Interface Transformation**
- **Normal**: Instruction 1 High Operand set by switches (for operators like MUL, AND, etc.)
- **Your Firmware**: Same parameter becomes direct "bit depth" knob control
- **Visual**: LED display shows "CRUSH AMOUNT" instead of hex operand value

### **Preset Guide**
- **A0 "Subtle Bit Reduction"**: Start here - gentle lo-fi character, maintains clarity
- **A1 "Lo-Fi Crunch"**: Classic 90s digital sound, crunchy but musical  
- **A2 "Extreme Decimation"**: Aggressive digital distortion, harsh and pixelated
- **A3 "Clean High-Res"**: Minimal processing, slight coloration

### **Sound Guide**
- **Full left (1-2 bits)**: Harsh, pixelated, extreme digital distortion
- **Center (4-5 bits)**: Classic lo-fi sound, crunchy but musical
- **Full right (7-8 bits)**: Subtle warmth, barely noticeable effect

### **Tips for New Users**
1. **Start with preset A0** and turn the knob slowly
2. **Watch the LED display** - it shows you the current bit depth visually
3. **Try with different input levels** - louder input makes the effect more obvious
4. **Combine with other effects** - bitcrushing works great before reverb or delay

### **Expected Behavior**
- **Immediate response**: Effect changes in real-time as you turn the knob
- **LED feedback**: Display pattern changes to show current bit depth
- **Audio range**: From subtle lo-fi warmth to extreme digital destruction

**Congratulations!** You just created working DSP firmware with a custom interface that converts complex operand controls into an intuitive effect knob.

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

## Understanding What You've Learned

### **Two Approaches to Permut8 Effects**

**You've just seen both approaches**:

1. **Ring Modulator (Existing)**: Uses Permut8's **original operator system**
   - Manipulates read/write positions in delay memory
   - Effects come from **where** and **how** audio is read back
   - Uses operators like MUL (pitch), SUB (delay), OSC (modulation)

2. **Bitcrusher (Your Custom)**: Uses **direct audio processing**
   - Bypasses the delay memory system entirely  
   - Processes audio samples directly in code
   - Full control over every aspect of the algorithm

### **Why Both Matter**

**Original Operators**: 
- **Efficient** - Built into hardware, very fast
- **Musical** - Designed for natural delay/modulation effects
- **Limited** - Can only do read/write head manipulation

**Custom Firmware**:
- **Unlimited** - Any algorithm you can code
- **Educational** - Learn by implementing from scratch
- **Flexible** - Mix approaches or create entirely new effects

### **The Big Picture**
Permut8 is **both** a sophisticated delay manipulation system **and** a programmable audio processor. Master both approaches to become a complete Permut8 developer.

## What's Next?

### **New to Audio Programming?** Start with the foundation:
1. 📖 [How DSP Affects Sound](../cookbook/fundamentals/how-dsp-affects-sound.md) - Understand how code creates audio effects (20 min)
2. 📖 [Getting Audio In and Out](../tutorials/getting-audio-in-and-out.md) - Foundation I/O tutorial (10 min)
3. 📖 [Your First Distortion Effect](../cookbook/fundamentals/simplest-distortion.md) - Progressive effect building (15 min)

### **Want to Master Permut8's Operator System?** 
📖 [Understanding Permut8 Operators](../tutorials/understanding-permut8-operators.md) - Complete guide to the instruction system and effect building (25 min)

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

**Bank Loading Issues:**
- **"Invalid data format (unsupported version?)"** → Check bank header format:
  - Must start with `Permut8BankV2: {` (not filename-based header)
  - Header format is case-sensitive and exact
- **"Invalid mnemonic: Compiled"** → Clean your GAZL file:
  - Remove compiler comment: `; Compiled with Impala version 1.0`
  - Remove from first line of .gazl file before creating bank
- **"Invalid mnemonic" with dashes** → Remove separator lines:
  - Remove lines like `;-----------------------------------------------------------------------------`
  - Keep only pure assembly code in bank

**Compilation Issues:**
- **Command not recognized?** Try `.\PikaCmd.exe impala.pika compile input.impala output.gazl`
- **"Cannot open file for reading"?** You need the script: `.\PikaCmd.exe impala.pika compile ...`
- **Still having trouble?** See [Compiler Troubleshooting Guide](../tutorials/compiler-troubleshooting-guide.md)

**Runtime Issues:**
- **Firmware won't compile?** Check for missing semicolons and proper syntax
- **No sound?** Make sure you called `yield()` in your loop
- **LEDs not working?** Values should be 8-bit (0-255)

---

**Ready for more?** The cookbook has 24+ ready-to-use recipes. Each one is complete, working code you can copy and modify. Start with any effect that interests you!