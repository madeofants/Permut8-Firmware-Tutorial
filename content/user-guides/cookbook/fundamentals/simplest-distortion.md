# Your First Distortion Effect

*From clean audio to guitar pedal sound in 15 minutes - Progressive distortion tutorial*

---

## What You'll Build

By the end of this tutorial, you'll have:
- A working distortion effect that sounds like a real guitar pedal
- Understanding of how different math creates different distortion sounds
- Control over distortion amount using hardware knobs
- Foundation for building any distortion-based effect

**Prerequisites**: [How DSP Affects Sound](#how-dsp-affects-sound), [Getting Audio In and Out](#getting-audio-in-and-out)  
**Time**: 15 minutes hands-on  
**Next Tutorial**: [Audio Engineering for Programmers](#audio-engineering-for-programmers)

---

## The Journey: Clean → Harsh → Musical

We'll build distortion in three progressive steps:

1. **Step 1**: Basic gain boost (2 minutes) - Make it louder
2. **Step 2**: Safe clipping (5 minutes) - Prevent harsh overload  
3. **Step 3**: Musical curves (8 minutes) - Sound like real guitar pedals

Each step builds on the previous one, so you'll always have working audio.

---

## Step 1: Basic Gain Boost (2 minutes)

### The Simplest Distortion

The most basic distortion is just **making audio louder than it should be**:

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

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function process() {
    loop {

        signal[0] = signal[0] * 3;
        signal[1] = signal[1] * 3;
        
        yield();
    }
}

```

### Try It Right Now

1. **Compile**: `PikaCmd.exe compile basic_gain.impala`
2. **Load**: Load `basic_gain.gazl` via plugin interface
3. **Play** some audio and **listen**

**What You'll Hear**: Much louder audio that starts to sound harsh and buzzy when the input is loud. This harshness IS distortion - you're hearing the audio system struggle with numbers that are too big.

### Why This Works

- **Quiet parts** (small numbers): `100 * 3 = 300` → Still clean
- **Loud parts** (big numbers): `1000 * 3 = 3000` → Too big! Gets automatically limited to 2047
- **The limiting creates distortion** - that harsh, buzzy sound

**Key Insight**: Distortion happens when audio numbers get too big for the system to handle cleanly.

---

## Step 2: Safe Clipping (5 minutes)

The basic gain boost works, but it's unpredictable. Sometimes it's clean, sometimes harsh. Let's take control.

### Controlled Clipping

Instead of hoping the system limits our audio safely, **we'll do the limiting ourselves**:

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
extern native yield

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function process() {
    loop {

        int distortionKnob = (int)global params[CLOCK_FREQ_PARAM_INDEX];
        int gainAmount = 1 + (distortionKnob / 32);
        

        int leftGained = signal[0] * gainAmount;
        int rightGained = signal[1] * gainAmount;
        

        if (leftGained > 2047) leftGained = 2047;
        if (leftGained < -2047) leftGained = -2047;
        if (rightGained > 2047) rightGained = 2047;
        if (rightGained < -2047) rightGained = -2047;
        

        signal[0] = leftGained;
        signal[1] = rightGained;
        

        displayLEDs[0] = distortionKnob;
        
        yield();
    }
}
```

### Try the Controlled Version

1. **Compile and load** this new version
2. **Turn Clock Frequency Knob** from left (clean) to right (distorted)
3. **Listen** to how the distortion becomes predictable and controlled

**What You'll Hear**: 
- **Clock Frequency Knob left**: Clean audio (1x gain, no clipping)
- **Clock Frequency Knob middle**: Mild distortion (moderate gain, some clipping)
- **Clock Frequency Knob right**: Heavy distortion (high gain, lots of clipping)

### Why This Is Better

- **Predictable**: You control exactly when distortion starts
- **Safe**: Never damages speakers or ears with unexpected volume spikes
- **Musical**: Distortion amount follows your knob movements
- **Visual**: LED shows current distortion setting

**Key Insight**: Professional distortion effects control the clipping instead of letting it happen randomly.

---

## Step 3: Musical Curves (8 minutes)

Hard clipping sounds harsh and digital. Real guitar pedals use **soft clipping** that sounds warm and musical.

### Understanding Clipping Curves

Different clipping shapes create different sounds:

```
Hard Clipping (harsh):          Soft Clipping (warm):
     ____                            ____
    |                               /
----+----  →  _____|_____          /
    |              |               |
    ____           ____            ____
```

### Soft Clipping Implementation

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
extern native yield

global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]

function softClip(int input, int threshold) {

    if (input > threshold) {
        int excess = input - threshold;
        return threshold + (excess / 4);
    } else if (input < -threshold) {
        int excess = input + threshold;
        return -threshold + (excess / 4);
    } else {
        return input;
    }
}

function process() {
    loop {

        int driveKnob = (int)global params[CLOCK_FREQ_PARAM_INDEX];
        int toneKnob = (int)global params[SWITCHES_PARAM_INDEX];
        

        int gainAmount = 1 + (driveKnob / 36);
        

        int clipThreshold = 500 + ((toneKnob * 1300) / 255);
        

        int leftGained = signal[0] * gainAmount;
        int rightGained = signal[1] * gainAmount;
        

        int leftClipped = softClip(leftGained, clipThreshold);
        int rightClipped = softClip(rightGained, clipThreshold);
        

        if (leftClipped > 2047) leftClipped = 2047;
        if (leftClipped < -2047) leftClipped = -2047;
        if (rightClipped > 2047) rightClipped = 2047;  
        if (rightClipped < -2047) rightClipped = -2047;
        

        signal[0] = leftClipped;
        signal[1] = rightClipped;
        

        displayLEDs[0] = driveKnob;
        displayLEDs[1] = toneKnob;
        
        yield();
    }
}
```

### Try Your Musical Distortion

1. **Compile and load** the soft clipping version
2. **Experiment with both knobs**:
   - **Clock Frequency Knob** (Drive): Amount of distortion
   - **Mode Switches** (Tone): Character of distortion
3. **Listen** for the warm, musical quality

**What You'll Hear**:
- **Low drive**: Clean or very mild overdrive
- **High drive**: Rich, warm distortion like vintage tube amps
- **Low tone**: Gentle, smooth clipping
- **High tone**: Brighter, more aggressive clipping

### Why This Sounds Better

#### **Soft vs Hard Clipping**:
```impala

if (signal > 1000) signal = 1000;


if (signal > 1000) {
    excess = signal - 1000;
    signal = 1000 + (excess / 4);
}
```

#### **The Magic**:
- **Hard clipping**: Immediate cutoff → harsh sound
- **Soft clipping**: Gradual compression → warm sound
- **Variable threshold**: Different tone characters
- **Gain staging**: Professional volume control

---

## Understanding Your Distortion Pedal

### What You Built

You now have a professional-quality distortion effect with:

1. **Drive Control** (Clock Frequency Knob): How much distortion
2. **Tone Control** (Mode Switches): Character of distortion  
3. **Soft Clipping**: Musical, warm sound
4. **Safety Limiting**: No damage or surprises
5. **Visual Feedback**: LED shows settings

### How It Compares to Commercial Pedals

**Your firmware** vs **$200 Distortion Pedal**:
- ✅ **Gain staging**: Professional volume control
- ✅ **Soft clipping**: Warm, musical distortion  
- ✅ **Tone shaping**: Variable clipping character
- ✅ **Safety features**: No damage or surprises
- ✅ **Real-time control**: Immediate response to knobs

**You built the core of a professional distortion pedal!**

---

## Advanced Variations

Now that you understand the fundamentals, try these modifications:

### 1. Asymmetrical Clipping
```impala

if (input > threshold) {
    return threshold + ((input - threshold) / 4);
} else if (input < -threshold) {
    return -threshold + ((input + threshold) / 2);
}
```

### 2. Multiple Stages
```impala

int stage1 = softClip(input * gain1, threshold1);
int stage2 = softClip(stage1 * gain2, threshold2);
```

### 3. Frequency-Dependent Distortion
```impala


```

---

## The Distortion Spectrum

You now understand how different approaches create different sounds:

### **Clean**: `signal = signal`
- No processing
- Original audio unchanged

### **Volume**: `signal = signal * gain`  
- Louder but clean (until clipping)
- Linear volume control

### **Hard Distortion**: `clamp(signal * gain, -limit, +limit)`
- Harsh, digital sound
- Immediate cutoff

### **Soft Distortion**: `softClip(signal * gain, threshold)`
- Warm, musical sound  
- Gradual compression

### **Professional Distortion**: Multiple stages + tone shaping
- Complex harmonic content
- Musical and controllable

---

## Key Concepts Learned

### 1. Distortion Is Controlled Overload
- Make audio too loud → System limits it → Creates distortion
- Control when/how limiting happens → Control distortion character

### 2. Clipping Shapes Define Sound
- **Hard clipping**: Immediate cutoff → harsh sound
- **Soft clipping**: Gradual compression → warm sound  
- **Asymmetrical**: Different positive/negative → unique character

### 3. Professional Features
- **Gain staging**: Control how much signal hits the distortion
- **Threshold control**: Adjust where distortion begins
- **Safety limiting**: Prevent damage and surprises
- **Visual feedback**: Show users what's happening

### 4. Real Guitar Pedal Architecture
- Input gain → Soft clipping → Tone shaping → Output limiting
- Multiple controls for musical flexibility
- Warm, musical algorithms instead of harsh digital

---

## What's Next?

### **Immediate Next Steps**:
1. **[Audio Engineering for Programmers](#audio-engineering-for-programmers)** - Professional concepts
2. **[Waveshaper Distortion](#waveshaper-distortion)** - Advanced mathematical approaches
3. **[Parameter Mapping](#parameter-mapping)** - Professional parameter design

### **Building on Distortion**:
- **[Multi-band Compressor](#multi-band-compressor)** - Frequency-specific processing
- **[Chorus Effect](#chorus-effect)** - Modulation-based effects
- **[Complete Development Workflow](#complete-development-workflow)** - Professional practices

### **Advanced Distortion**:
- **[Optimization Basics](#optimization-basics)** - Performance improvement
- **[Advanced Memory Management](#advanced-memory-management)** - Complex algorithms

---

## Quick Reference

### **Basic Distortion Pattern**:
```impala

int gained = signal[0] * gainAmount;


int clipped = softClip(gained, threshold);


if (clipped > 2047) clipped = 2047;
if (clipped < -2047) clipped = -2047;


signal[0] = clipped;
```

### **Soft Clipping Function**:
```impala
function softClip(int input, int threshold) {
    if (input > threshold) {
        return threshold + ((input - threshold) / compressionRatio);
    } else if (input < -threshold) {
        return -threshold + ((input + threshold) / compressionRatio);
    }
    return input;
}
```

### **Professional Controls**:
- **Drive/Gain**: How much signal hits the distortion
- **Tone/Threshold**: Where and how distortion begins  
- **Output Level**: Final volume control
- **Safety Limiting**: Prevent damage

You now understand the fundamentals of distortion and have built a professional-quality effect! This knowledge applies to all overdrive, distortion, and saturation effects.

---

*Next: [Audio Engineering for Programmers](#audio-engineering-for-programmers) - Essential audio concepts in programming terms*