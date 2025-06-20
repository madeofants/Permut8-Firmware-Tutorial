# How DSP Affects Sound

*Understanding how code changes create audio effects - Foundation tutorial for complete beginners (20 minutes)*

---

## What You'll Learn

By the end of this tutorial, you'll understand:
- What audio samples are and how numbers become sound
- How changing numbers in code changes what you hear
- The fundamental relationship between programming and audio effects
- Your first working sound modification

**Prerequisites**: None - this is for complete audio programming beginners  
**Time**: 20 minutes reading + 5 minutes hands-on  
**Next Tutorial**: [Getting Audio In and Out](#getting-audio-in-and-out)

---

## Part 1: Numbers Become Sound (5 minutes)

### The Magic Translation

When you hear music from your computer, something amazing is happening: **numbers are being turned into sound waves**. Every fraction of a second, thousands of numbers flow from your software to your speakers, and those numbers control exactly what you hear.

### What is an Audio Sample?

An **audio sample** is just a number that represents the position of a speaker cone at one tiny moment in time.

```
Positive numbers → Speaker pushes out → You hear sound
Negative numbers → Speaker pulls in → You hear sound  
Zero → Speaker stays still → Silence
```

### Permut8's Two Approaches to Audio

**Before we dive into code**, it's important to understand that Permut8 has **two fundamentally different ways** to affect sound:

#### **Approach 1: Original Operator System**
```
Audio Input → 128k Delay Memory → [Operators manipulate read positions] → Audio Output
```
- **How it works**: Audio is stored in memory, operators control where and how it's read back
- **Effects**: Delays, pitch shifting, modulation, granular textures
- **Examples**: Using MUL operator for pitch, OSC for flanging, SUB for delays

#### **Approach 2: Custom Firmware (Direct Processing)**  
```
Audio Input → [Your code processes samples directly] → Audio Output
```
- **How it works**: Bypass the delay system, process audio samples with your own algorithms
- **Effects**: Distortion, filtering, compression, bit crushing, anything you can code
- **Examples**: Mathematical effects, custom algorithms, novel processors

### **Both Are Powerful - This Tutorial Shows Approach 2**

This tutorial focuses on **direct audio processing** (Approach 2) because it's easier to understand the immediate relationship between code and sound. Once you master this, you can learn the operator system for more complex time-based effects.

### **Direct Processing with Custom Firmware**

In custom firmware (Approach 2), audio samples are integers from **-2047 to +2047**:

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

extern native yield

global array signal[2]  // [left channel, right channel]
global array params[PARAM_COUNT]  // Hardware knob values (0-255)

function process() {
    loop {
        // signal[0] = some number between -2047 and +2047
        // signal[1] = some number between -2047 and +2047
        yield();  // Send these numbers to the speakers
    }
}

```

**Key Insight**: Every time your code runs, it puts two numbers into `signal[0]` and `signal[1]`. Those numbers immediately become the sound you hear through your left and right speakers.

---

## Part 2: Changing Numbers Changes Sound (10 minutes)

Now for the exciting part: **when you change the numbers in code, you change what people hear**. This is the fundamental principle of Digital Signal Processing (DSP).

### Basic Sound Changes

Here are the most fundamental ways code affects sound:

#### 1. Make it Louder (Multiply by Bigger Number)
```impala
signal[0] = signal[0] * 2;  // Twice as loud
signal[1] = signal[1] * 2;  // Both channels
```
**What Happens**: Every audio sample gets bigger → Speaker moves more → Sound is louder

#### 2. Make it Quieter (Multiply by Smaller Number)
```impala
signal[0] = signal[0] / 2;  // Half as loud
signal[1] = signal[1] / 2;  // Both channels
```
**What Happens**: Every audio sample gets smaller → Speaker moves less → Sound is quieter

#### 3. Add Distortion (Push Beyond Limits)
```impala
signal[0] = signal[0] * 5;  // Way too loud!
// Permut8 automatically prevents damage by limiting to ±2047
// But this creates distortion - harsh, buzzy sound
```
**What Happens**: Numbers try to go beyond ±2047 → Get "clipped" → Creates distortion

#### 4. Mix Two Sounds (Add Numbers)
```impala
int originalSound = signal[0];
int synthesizedSound = 1000;  // A constant tone
signal[0] = originalSound + synthesizedSound;  // Mix them!
```
**What Happens**: Two sound sources combine → You hear both at once

#### 5. Create Echo (Use Old Numbers)
```impala
global array delayBuffer[1000];  // Store old audio
global int delayPos = 0;

// In your process() loop:
int currentAudio = signal[0];
int oldAudio = delayBuffer[delayPos];  // Audio from 1000 samples ago

signal[0] = currentAudio + (oldAudio / 2);  // Mix current + old = echo!

delayBuffer[delayPos] = currentAudio;  // Remember this audio for later
delayPos = (delayPos + 1) % 1000;      // Move to next position
```
**What Happens**: You hear current audio + audio from the past → Echo effect!

### The Pattern

Do you see the pattern? **Every audio effect is just a different way of calculating numbers**:

- **Volume**: Multiply samples
- **Distortion**: Make samples too big
- **Mixing**: Add samples together  
- **Echo**: Use old samples
- **Filtering**: Average nearby samples
- **Tremolo**: Multiply by changing numbers
- **Ring Modulation**: Multiply by oscillating numbers

**Programming + Math = Any Sound Effect You Can Imagine**

---

## Part 3: Your First Sound Change (5 minutes)

Let's make your first audio modification! This will prove that code changes immediately affect what you hear.

### Complete Working Example

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
extern native yield

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function process() {
    loop {
        // Read the current audio coming into Permut8
        int leftInput = signal[0];
        int rightInput = signal[1];
        
        // CHANGE THE SOUND: Make it quieter using Clock Frequency Knob
        int volumeKnob = (int)global params[CLOCK_FREQ_PARAM_INDEX];  // 0-255 from hardware
        int volumeAmount = volumeKnob + 1;  // 1-256 (never zero)
        
        // Apply the volume change
        signal[0] = (leftInput * volumeAmount) / 256;
        signal[1] = (rightInput * volumeAmount) / 256;
        
        // Visual feedback: Show the volume on LED display
        displayLEDs[0] = volumeKnob;
        
        yield();  // Send the modified audio to speakers
    }
}
```

### What This Code Does

1. **Reads** the incoming audio samples
2. **Reads** Clock Frequency Knob position (0-255)
3. **Calculates** a volume multiplier (1-256)
4. **Multiplies** each audio sample by the volume amount
5. **Shows** the current volume on the LED display
6. **Outputs** the modified audio

### Try It!

1. **Compile** this code: `PikaCmd.exe compile volume_control.impala`
2. **Create and load bank**: File → Load Bank → `volume_control.p8bank`
3. **Select A0 preset**
4. **Play** some audio through Permut8
5. **Turn Clock Frequency Knob** and hear the volume change in real-time!

**You just modified sound with code!** Turn the knob left (quieter) and right (louder). The LED display shows exactly what's happening.

---

## Understanding What Just Happened

### The DSP Loop

Every time through the `loop`, your code:
1. **Receives** new audio samples (what's coming in)
2. **Modifies** those samples (your effect processing)
3. **Outputs** the modified samples (what people hear)
4. **Repeats** 44,100 times per second!

### Real-Time Processing

This happens **44,100 times every second**. That's why turning the knob immediately changes the sound - your code is running constantly, modifying every single audio sample as it flows through Permut8.

### From Simple to Complex

The volume control you just built uses the same fundamental principles as professional audio effects:

- **Professional EQ**: Different math for different frequencies
- **Professional Reverb**: Complex delay and mixing calculations  
- **Professional Compression**: Dynamic volume calculations
- **Professional Distortion**: Controlled sample limiting and shaping

**Every audio effect is built from these same building blocks: reading samples, doing math, outputting results.**

---

## Key Concepts Learned

### 1. Audio Samples Are Numbers
- Sound = streams of numbers flowing to speakers
- In Permut8: integers from -2047 to +2047
- Every number controls speaker position at one moment

### 2. Code Changes = Sound Changes  
- Multiply samples → Volume changes
- Add samples → Mixing effects
- Limit samples → Distortion effects
- Delay samples → Echo effects

### 3. Real-Time Processing
- Your code runs 44,100 times per second
- Every sample gets processed individually
- Changes happen immediately when you modify code

### 4. Effects Are Math
- Volume = multiplication
- Distortion = limiting  
- Echo = delayed addition
- Complex effects = combinations of simple math

---

## What's Next?

Now that you understand how code affects sound, you're ready for:

### **Immediate Next Steps**:
1. **[Getting Audio In and Out](#getting-audio-in-and-out)** - Learn the basic I/O structure
2. **[Your First Distortion Effect](#simplest-distortion)** - Build a working guitar effect
3. **[Audio Engineering for Programmers](#audio-engineering-for-programmers)** - Professional concepts

### **Advanced Learning Path**:
- **[Control Something with Knobs](#read-knobs)** - Hardware interface
- **[Complete Development Workflow](#complete-development-workflow)** - Professional practices
- **[Debug Your Plugin](#debug-your-plugin)** - Troubleshooting skills

---

## Quick Reference

### **Essential Pattern for All Effects**:
```impala
function process() {
    loop {
        // 1. Read current audio
        int input = signal[0];
        
        // 2. Do some math to change it
        int output = input * someModification;
        
        // 3. Send modified audio to speakers
        signal[0] = output;
        
        yield();  // Repeat 44,100 times per second
    }
}
```

### **Remember**: 
- **Every effect** is just different math applied to audio samples
- **Code changes** immediately become **sound changes**
- **Start simple** and build complexity gradually
- **Real-time** means your code affects every sample as it flows through

You now understand the fundamental relationship between programming and audio. Every professional audio effect started with these same basic concepts!

---

*Next: [Getting Audio In and Out](#getting-audio-in-and-out) - Learn the foundational I/O structure for building effects*