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

## Your First Firmware (10 minutes)

Let's create a simple bit crusher from scratch.

### 1. Create a New File
Create `bitcrush.impala` with this code:

```impala
// Bit Crusher - Your First Permut8 Firmware
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield

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
        A0: { Name: "Light Crush", Operator1: "2" }
        A1: { Name: "Heavy Crush", Operator1: "6" }
    }
    Firmware: {
        Name: "bitcrush"
        Code: {
[PASTE YOUR CLEANED GAZL CONTENT HERE]
 }
    }
}
```

### 3. Prepare GAZL for Bank
**Remove the first line** from your compiled `bitcrush.gazl`:
1. Open `bitcrush.gazl` in any text editor
2. Delete the first line: `; Compiled with Impala version 1.0`
3. Save the file

### 4. Create Firmware Bank
Create `bitcrush.p8bank` with this **exact format** (note the header):
```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Light Crush", Operator1: "2" }
        A1: { Name: "Heavy Crush", Operator1: "6" }
    }
    Firmware: {
        Name: "bitcrush"
        Code: {
[PASTE YOUR CLEANED GAZL CONTENT HERE]
 }
    }
}
```

**⚠️ Critical**: 
- Header MUST be `Permut8BankV2:` (not `bitcrush.p8bank:`)
- Paste your entire cleaned `bitcrush.gazl` content between `Code: {` and ` }`

### 5. Load and Test
1. Load bank: File → Load Bank → `bitcrush.p8bank`
2. Select A0 preset (Light Crush) or A1 (Heavy Crush)
3. Play some audio through Permut8
4. Turn **knob 4** (not knob 1!) - hear the bit crushing!

**Congratulations!** You just created working DSP firmware. Knob 4 now controls bit depth, creating that classic lo-fi digital sound.

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