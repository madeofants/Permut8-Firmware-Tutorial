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

**Why the different commands?** See [Compiler Troubleshooting Guide](#compiler-troubleshooting-guide) for the technical explanation.

### 3. Create and Load Firmware Bank
1. Open Permut8 in your DAW
2. Create a firmware bank:
   - Package your `ringmod_code.gazl` into `ringmod.p8bank`
   - Add preset configuration (A0: "Ring Modulator")
3. Load bank: File → Load Bank → `ringmod.p8bank`
4. Select A0 preset

**You just loaded custom firmware!** The ring modulator is now running.

## Your First Firmware (15 minutes)

Let's create a **simple volume control effect** that gives you immediate audio feedback and shows the basic structure of Permut8 firmware.

### 1. Create a New File
Create `volume_control.impala` with this code:

**Simple Volume Control - Immediate Audio Feedback**

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield


const int CLOCK_FREQ_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int PARAM_COUNT


readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "VOLUME |------- GAIN CONTROL -------|",
    "",
    "",
    "",
    ""
}

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
locals int volume, int inputL, int inputR, int outputL, int outputR
{
    loop {

        volume = (int)global params[OPERAND_2_HIGH_PARAM_INDEX] * 2;
        

        inputL = (int)global signal[0];
        inputR = (int)global signal[1];
        

        outputL = (inputL * volume) / 255;
        outputR = (inputR * volume) / 255;
        

        if (outputL > 2047) outputL = 2047;
        if (outputL < -2047) outputL = -2047;
        if (outputR > 2047) outputR = 2047;
        if (outputR < -2047) outputR = -2047;
        

        global signal[0] = outputL;
        global signal[1] = outputR;
        

        global displayLEDs[0] = volume >> 1;
        

        if (outputL > 1000) {
            global displayLEDs[1] = 0xFF;
        } else {
            global displayLEDs[1] = 0x00;
        }
        

        if (outputR > 1000) {
            global displayLEDs[2] = 0xFF;
        } else {
            global displayLEDs[2] = 0x00;
        }
        

        if (volume > 200) {
            global displayLEDs[3] = 0xFF;
        } else {
            global displayLEDs[3] = 0x00;
        }
        
        yield();
    }
}
```

### **Understanding What Just Happened**

This simple firmware demonstrates the core concepts of Permut8 programming:

#### **The Audio Flow**:
```
Audio Input → Volume Calculation → Audio Output
```
- **Input**: `global signal[0]` and `global signal[1]` contain incoming audio
- **Processing**: Multiply by volume value from knob
- **Output**: Write processed audio back to `global signal[0]` and `global signal[1]`

#### **Parameter Control**:
- **`params[OPERAND_2_HIGH_PARAM_INDEX]`**: Gets knob position (0-255)
- **Volume Calculation**: `params[OPERAND_2_HIGH_PARAM_INDEX] * 2` gives 0-510 range (up to 2x boost)
- **Audio Scaling**: `(input * volume) / 255` applies the gain

#### **Visual Feedback**:
- **LED 0**: Shows current volume level
- **LED 1 & 2**: Flash when audio is present on left/right channels
- **LED 3**: Lights up when gain exceeds normal level (boost mode)

**The Key Insight**: You directly control audio processing - every sample passes through your code.

### 2. Compile Your Firmware
```bash
PikaCmd.exe -compile volume_control.impala
```

**If that doesn't work**, use the full command:
```bash
.\PikaCmd.exe impala.pika compile volume_control.impala volume_control.gazl
```

### 3. Create Firmware Bank

**Step 3a: Clean the GAZL File**
1. **Open `volume_control.gazl`** in a text editor
2. **Remove these specific lines that cause "Invalid mnemonic" errors:**
   - Header: `; Compiled with Impala version 1.0`
   - Separators: `;-----------------------------------------------------------------------------`
   - Inline comments: Any line containing `;` followed by your original Impala code
3. **Keep only the pure assembly instructions** - no lines starting with `;`

**Step 3b: Create the Bank File**
Create `volume_control.p8bank`:
```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Quiet", Operator1: "0" }
        A1: { Name: "Normal", Operator1: "0" }
        A2: { Name: "Loud", Operator1: "0" }
        A3: { Name: "Boost", Operator1: "0" }
    }
    Firmware: {
        Name: "volume_control"
        Code: {
[PASTE YOUR CLEANED GAZL CONTENT HERE]
 }
    }
}
```

### **Understanding the Presets**

Each preset has `Operator1: "0"` which means:
- **"0" = No built-in operator** - Your custom firmware handles everything
- **Different presets** suggest different volume levels to try
- **Same firmware** - Just different starting suggestions

### 4. Load and Test Your Volume Control

1. **Load the bank**: File → Load Bank → `volume_control.p8bank`
2. **Select A1 "Normal"** preset
3. **Play audio** through Permut8
4. **Turn Control 1** to hear immediate volume changes!

## How to Use Your Volume Control

### **What Just Happened?**
Your custom firmware **directly processes every audio sample**:

**Audio Flow**:
```
Audio Input → Volume Multiplication → Audio Output
```

**Real-time Processing**: Every audio sample is multiplied by your volume setting before output.

### **Control Guide**
- **Control 1**: Volume level (turn left = quieter, turn right = louder)
- **LEDs**: Visual feedback showing volume and audio activity

### **Preset Guide**
- **A0 "Quiet"**: Start with low volume
- **A1 "Normal"**: Unity gain (no change)
- **A2 "Loud"**: Increased volume
- **A3 "Boost"**: Maximum boost (can distort!)

### **Tips for New Users**
1. **Start with A1 "Normal"** and adjust Control 1 to hear changes
2. **Turn slowly** - volume changes are immediate
3. **Watch LED 3** - lights up when boosting beyond normal level
4. **Compare presets** - hear different starting volume levels

**Congratulations!** You just created your first custom firmware that directly controls audio processing in real-time.

## Modify Your Volume Control (5 minutes)

Let's add a simple modification to make the volume control more interesting.

### 1. Add Stereo Width Control
Replace the audio processing section with:
```impala

volume = (int)global params[OPERAND_1_HIGH_PARAM_INDEX] * 2;
int width = (int)global params[OPERAND_1_LOW_PARAM_INDEX];


inputL = (int)global signal[0];
inputR = (int)global signal[1];


outputL = (inputL * volume) / 255;
outputR = (inputR * volume) / 255;


int mono = (outputL + outputR) / 2;
int side = (outputL - outputR) / 2;


side = (side * width) / 255;


outputL = mono + side;
outputR = mono - side;
```

### 2. Update Interface Labels
```impala
readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "VOLUME |------- GAIN CONTROL -------|",
    "",
    "",
    "",
    "STEREO |------ WIDTH CONTROL ------|"
};
```

### 3. Compile and Test
```bash
PikaCmd.exe -compile volume_control.impala
```

Now you have both volume AND stereo width control!

## Understanding What You've Learned

### **Core Permut8 Programming Concepts**

**You've just learned the fundamentals**:

1. **Audio Processing**: Direct sample manipulation in real-time
2. **Parameter Control**: Using knobs to control your algorithms
3. **Visual Feedback**: LEDs that respond to your processing
4. **Custom Interface**: Clear labels instead of abstract controls

### **The Foundation**

**Every Permut8 firmware follows this pattern**:
```impala
function process() {
    loop {





        yield();
    }
}
```

**This is the building block** for every effect, from simple volume control to complex delays, filters, and synthesizers.

## What's Next?

### **Ready for More Effects?** Based on what you just built:

**Want simple, immediate effects?**
- 📖 [Getting Audio In and Out](tutorials/getting-audio-in-and-out.md) - Foundation I/O patterns (10 min)
- 📖 [Make Your First Sound](tutorials/make-your-first-sound.md) - Basic synthesis (15 min)
- 📖 [Simple Distortion](cookbook/audio-effects/bitcrusher.md) - Audio processing (15 min)
- 📖 [Make a Delay](cookbook/audio-effects/make-a-delay.md) - Memory-based effects (20 min)

**Curious about Permut8's unique features?**
- 📖 [Understanding Operators vs Custom Firmware](tutorials/understanding-operators-vs-custom-firmware.md) - The two approaches (25 min)
- 📖 [Understanding Permut8 Operators](tutorials/understanding-permut8-operators.md) - Built-in system (25 min)

**Ready for advanced effects?**
- 📖 [Advanced Custom Delay Tutorial](tutorials/advanced-custom-delay-tutorial.md) - Memory management (45 min)
- 📖 [Control Something with Knobs](tutorials/control-something-with-knobs.md) - Parameter mapping (20 min)

### **Choose Your Path:**

**New to Audio Programming?** → Start with cookbook recipes
**Want to Understand Permut8?** → Read the operator guides
**Ready to Build Complex Effects?** → Try the advanced tutorials

### **Professional Development:**
- 📖 [Complete Development Workflow](tutorials/complete-development-workflow.md) - Systematic methodology
- 📖 [Debug Your Plugin](tutorials/debug-your-plugin.md) - Essential troubleshooting

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
- **Still having trouble?** See [Compiler Troubleshooting Guide](#compiler-troubleshooting-guide)

**Runtime Issues:**
- **Firmware won't compile?** Check for missing semicolons and proper syntax
- **No sound?** Make sure you called `yield()` in your loop
- **LEDs not working?** Values should be 8-bit (0-255)

---

**Ready for more?** The cookbook has 24+ ready-to-use recipes. Each one is complete, working code you can copy and modify. Start with any effect that interests you!