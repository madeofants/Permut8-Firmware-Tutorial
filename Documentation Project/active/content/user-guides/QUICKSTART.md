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

Let's create a **simple delay effect** that shows the **direct connection** between Permut8's operator system and custom firmware.

### **Understanding Permut8's Core System**

Before we build, let's understand what makes Permut8 special:

**The Heart**: 128 kilowords of delay memory with moving read/write heads
- **Write position (red dot)**: Where incoming audio is stored continuously
- **Read positions (green dots)**: Where audio is played back from 
- **Two instructions**: Manipulate the read positions to create effects

**How Delays Work in Permut8**:
```
Audio Input → [Write to memory] → [Read from memory at offset] → Audio Output + Original
```
- **Write**: Current audio goes into memory at write position
- **Read**: Audio from X samples ago comes out of memory 
- **Mix**: Delayed audio + original audio = echo effect

**Original vs Custom Approach** (Same Effect, Different Methods):

#### **Original: SUB Operator (Built-in)**
- **Instruction 1**: SUB operator with delay time operand
- **Hardware manages**: Memory read/write automatically
- **Interface**: Set delay time via switches/LED displays
- **Efficiency**: Hardware-optimized, very fast

#### **Custom: Manual Implementation (What We'll Build)**
- **Our firmware**: Manually manage memory read/write
- **Direct control**: Every aspect of the delay algorithm
- **Interface**: Custom knob labels and behaviors
- **Learning**: See exactly how delays work inside

### 1. Create a New File
Create `custom_delay.impala` with this code:

**Custom Delay - Shows Connection to SUB Operator**

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield
extern native read
extern native write

// Interface override: Transform operator interface into custom delay controls
readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "DELAY |---- TIME (INSTRUCTION 1 HIGH) ----|",
    "",
    "",
    "",
    "DELAY |-- FEEDBACK (INSTRUCTION 1 LOW) --|"
}

global array signal[2]
global array params[8]
global array displayLEDs[4]

// Delay state (what SUB operator manages automatically)
global int writePosition = 0
global array tempBuffer[2]

function process()
locals int delayTime, int feedback, int input, int delayed, int output
{
    loop {
        // Same parameters that SUB operator uses, but with custom control
        delayTime = ((int)global params[3] * 500 / 255) + 50;  // 50-550 samples (Instruction 1 High)
        feedback = ((int)global params[4] * 200 / 255);         // 0-200 feedback (Instruction 1 Low)
        
        // Manual delay processing (what SUB operator does automatically)
        input = (int)global signal[0];
        
        // Read delayed sample from memory (read position = write position - delay time)
        int readPosition = global writePosition - delayTime;
        if (readPosition < 0) readPosition += 65536;  // Wrap around
        
        read(readPosition, 1, global tempBuffer);
        delayed = global tempBuffer[0];
        
        // Create echo: original + delayed signal
        output = input + (delayed * feedback / 255);
        
        // Prevent clipping
        if (output > 2047) output = 2047;
        if (output < -2047) output = -2047;
        
        // Write current input + feedback to memory for next cycle
        global tempBuffer[0] = input + (delayed * feedback / 255);
        write(global writePosition, 1, global tempBuffer);
        
        // Advance write position (what hardware manages automatically)
        global writePosition = (global writePosition + 1) % 65536;
        
        // Output the echo
        global signal[0] = output;
        global signal[1] = output;  // Mono delay
        
        // Visual feedback showing delay activity
        global displayLEDs[0] = delayTime >> 2;        // Show delay time
        global displayLEDs[1] = feedback;              // Show feedback amount
        global displayLEDs[2] = (delayed > 0) ? 0xFF : 0x00;  // Activity indicator
        global displayLEDs[3] = (global writePosition >> 8) & 0xFF;  // Position indicator
        
        yield();
    }
}
```

### **The Operator Connection - Same Parameters, Different Approach**

This firmware shows the **direct relationship** between custom firmware and Permut8's built-in operators:

#### **What SUB Operator Does Automatically**:
- **Memory Management**: Hardware tracks write position automatically
- **Read Positioning**: SUB operand directly controls read offset  
- **Efficiency**: Optimized in hardware, very fast

#### **What Our Custom Firmware Does Manually**:
- **Manual Memory**: We track `writePosition` ourselves
- **Manual Reading**: We calculate `readPosition = writePosition - delayTime`
- **Same Parameters**: `params[3]` (Instruction 1 High) controls delay time in both approaches
- **Same Effect**: Both create delay, just different implementations

#### **Interface Transformation**:
- **Original**: `params[3]` controlled via switches/LED display showing hex values
- **Custom**: Same `params[3]` becomes direct "DELAY TIME" knob via `panelTextRows`
- **User Experience**: Intuitive delay control instead of abstract operand values

**The Key Insight**: Both approaches use the **same parameter system** (`params[3]`, `params[4]`), but custom firmware gives you complete control over what those parameters mean and how they're processed.

### 2. Compile Your Firmware
```bash
PikaCmd.exe -compile custom_delay.impala
```

**If that doesn't work**, use the full command:
```bash
.\PikaCmd.exe impala.pika compile custom_delay.impala custom_delay.gazl
```

### 3. Create Firmware Bank

**Step 3a: Clean the GAZL File**
Before creating the bank, you need to clean the compiled GAZL file:

1. **Open `custom_delay.gazl`** in a text editor
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
Create `custom_delay.p8bank` with this **exact format** (note the header):
```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Short Slap Delay", Operator1: "8" }
        A1: { Name: "Medium Echo", Operator1: "8" }
        A2: { Name: "Long Ambient", Operator1: "8" }
        A3: { Name: "Feedback Madness", Operator1: "8" }
    }
    Firmware: {
        Name: "custom_delay"
        Code: {
[PASTE YOUR CLEANED GAZL CONTENT HERE]
 }
    }
}
```

### **Understanding the Operators in Your Presets**

You might notice each preset has `Operator1: "8"`. This is **significant** - here's why:

**What "8" Means**:
- **Operator1: "8"** = **SUB operator** (Subtract - creates delays)
- This is the **same operator** that would create delays using the built-in system
- **Our custom firmware ignores it** - we're implementing delay manually instead
- **But the connection is clear**: We're doing the same job as SUB operator

**The Operator Connection**:
- **Built-in SUB**: `Operator1: "8"` + operand values create automatic delays
- **Our Custom**: Manual implementation of what SUB does automatically
- **Same Parameters**: Both use `params[3]` for delay time, `params[4]` for feedback
- **Same Result**: Both create delay effects, just different approaches

**Why Use SUB "8" in Presets?**:
1. **Shows Intent**: Makes it clear this is a delay effect
2. **User Expectation**: Users familiar with SUB will understand immediately  
3. **Learning Connection**: Demonstrates relationship between operators and custom code
4. **Future Compatibility**: Could switch to built-in SUB by removing custom firmware

**The Bigger Picture**: This demonstrates how custom firmware can **replace** or **enhance** built-in operators while using the same parameter system and interface concepts.

### 4. Load and Test Your Custom Delay

1. **Load the bank**: File → Load Bank → `custom_delay.p8bank`
2. **Select a preset** to start with
3. **Play audio** through Permut8
4. **Turn the operator knobs** to hear the delay effect!

## How to Use Your Custom Delay

### **What Just Happened?**
Your custom firmware **manually implemented** what the SUB operator does automatically:

**Normal SUB Operator Flow**:
```
Audio Input → Delay Memory → [SUB operator subtracts offset] → Audio Output + Original
```

**Your Custom Delay Flow**:
```
Audio Input → [Manual memory read/write with offset] → Audio Output + Original
```

**Same Result, Different Method**: Both create delay effects, but now you understand exactly how delays work inside Permut8's memory system.

### **Interface Transformation**
- **Original**: Instruction 1 operands set by switches/LED displays showing hex values
- **Your Firmware**: Same parameters become intuitive "DELAY TIME" and "FEEDBACK" controls
- **Visual**: Clear labels instead of abstract hex operand values

### **The Memory Connection**
Your code manually does what SUB operator handles automatically:
- **Write Position**: You track `writePosition` manually vs. hardware automatic
- **Read Position**: You calculate `writePosition - delayTime` vs. SUB operand subtraction
- **Memory Management**: You use `read()` and `write()` vs. hardware optimization

### **Preset Guide**
- **A0 "Short Slap Delay"**: Quick echo, good for drums and percussion
- **A1 "Medium Echo"**: Classic delay, perfect for vocals and instruments
- **A2 "Long Ambient"**: Spacious delays for atmospheric effects
- **A3 "Feedback Madness"**: High feedback for experimental sounds

### **Control Guide**
- **Control 1 (Delay Time)**: Adjust Instruction 1 High Operand position for delay time
- **Control 2 (Feedback)**: Adjust Instruction 1 Low Operand position for feedback amount
- **LED Display**: Shows delay time, feedback amount, and activity

**Note**: This custom firmware transforms the operand controls (normally set via LED displays and switches) into direct effect controls. The **Operator Control 1** and **Operator Control 2** are not used.

### **Tips for New Users**
1. **Start with A0** and adjust Control 1 (Instruction 1 High Operand) slowly to hear delay time changes
2. **Add feedback** with Control 2 (Instruction 1 Low Operand) to create multiple echoes
3. **Watch LEDs** - they show delay parameters and memory activity
4. **Compare to built-in**: Try the same settings with SUB operator

### **The Learning Connection**
This delay effect shows you:
- **How delay memory works** - the foundation of all Permut8 effects
- **Parameter relationships** - same `params[3]` and `params[4]` as SUB operator
- **Custom vs. built-in** - both approaches, same results
- **Interface control** - how to make complex parameters user-friendly

**Congratulations!** You just created a delay effect that manually implements what Permut8's SUB operator does automatically, showing the direct connection between operators and custom firmware.

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