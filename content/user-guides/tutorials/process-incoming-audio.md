# Process Incoming Audio - Basic Audio Effects

## What This Tutorial Does
Learn how to modify incoming audio to create your first real audio effects. In 15 minutes, you'll build simple but effective audio processors that transform sound in real-time. This bridges the gap from basic plugins to real audio effects.

## What You'll Learn
- How to read, modify, and output audio samples
- Simple audio processing techniques for immediate results
- Building blocks for all audio effects
- Safe audio practices to prevent damage and artifacts
- Foundation concepts for filters, distortion, and dynamics

**Prerequisites**: [Getting Audio In and Out](getting-audio-in-and-out.md)  
**Time Required**: 15 minutes  
**Difficulty**: Beginner

---

## Step 1: Understanding Audio Processing

### 1.1 The Basic Audio Flow
**Every audio effect follows this pattern:**
```impala

int input = signal[0]


int processed = doSomethingTo(input)


signal[0] = processed
```

### 1.2 Audio Sample Range
**Permut8 audio samples are 12-bit signed integers:**
- **Range**: -2047 to +2047
- **Zero**: 0 (silence)
- **Positive**: Above zero (positive waveform)
- **Negative**: Below zero (negative waveform)

### 1.3 Safe Processing Rules
✅ **Always check for clipping**: Values outside ±2047 cause distortion  
✅ **Preserve both channels**: Process left and right independently  
✅ **Test with different audio**: Music, speech, silence, loud signals  
✅ **Start subtle**: Small changes sound more musical than extreme ones  

---

## Step 2: Your First Audio Effect - Simple Gain

### 2.1 Volume Control Effect
Create `simple_gain.impala`:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {

        int inputLeft = signal[0]
        int inputRight = signal[1]
        

        int gain = 128
        
        int outputLeft = (inputLeft * gain) / 128
        int outputRight = (inputRight * gain) / 128
        

        if (outputLeft > 2047) outputLeft = 2047
        else if (outputLeft < -2047) outputLeft = -2047
        
        if (outputRight > 2047) outputRight = 2047
        else if (outputRight < -2047) outputRight = -2047
        

        signal[0] = outputLeft
        signal[1] = outputRight
        
        yield()
    }
}
```

### 2.2 Test Gain Control
1. **Compile**: `PikaCmd.exe -compile simple_gain.impala`
2. **Load**: `patch simple_gain.gazl`
3. **Play audio** and listen
4. **Try different gain values**:
   - `gain = 64`: Half volume
   - `gain = 128`: Original volume
   - `gain = 256`: Double volume (may clip!)

**🎉 You just built your first audio processor!** You're modifying the audio signal in real-time.

---

## Step 3: Add Parameter Control

### 3.1 Knob-Controlled Gain
**Add hardware knob control to your gain effect:**

```impala
function process()
{
    loop {

        int inputLeft = signal[0]
        int inputRight = signal[1]
        

        int gainKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        


        int gain = (gainKnob * 2)
        

        int outputLeft = (inputLeft * gain) / 255
        int outputRight = (inputRight * gain) / 255
        

        if (outputLeft > 2047) outputLeft = 2047
        else if (outputLeft < -2047) outputLeft = -2047
        if (outputRight > 2047) outputRight = 2047
        else if (outputRight < -2047) outputRight = -2047
        

        displayLEDs[0] = gainKnob
        

        signal[0] = outputLeft
        signal[1] = outputRight
        
        yield()
    }
}
```

### 3.2 Test Interactive Gain
1. **Compile and load**
2. **Turn knob 1** while audio is playing
3. **Expected result**: Volume changes smoothly with knob position
4. **LED should show knob position**

**Now you have real-time, interactive audio processing!**

---

## Step 4: Simple High-Frequency Filter

### 4.1 Understanding Filtering
**A simple filter smooths out fast changes in audio:**
```impala



```

### 4.2 Build a Simple Low-Pass Filter
```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]


global int previousOutputLeft = 0
global int previousOutputRight = 0

function process()
{
    loop {

        int inputLeft = signal[0]
        int inputRight = signal[1]
        

        int filterKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        

        int filterAmount = filterKnob
        


        int filteredLeft = ((inputLeft * (255 - filterAmount)) + (previousOutputLeft * filterAmount)) / 255
        int filteredRight = ((inputRight * (255 - filterAmount)) + (previousOutputRight * filterAmount)) / 255
        

        previousOutputLeft = filteredLeft
        previousOutputRight = filteredRight
        

        displayLEDs[0] = filterKnob
        

        signal[0] = filteredLeft
        signal[1] = filteredRight
        
        yield()
    }
}
```

### 4.3 Test the Filter
1. **Compile and load**
2. **Turn knob 1** while playing audio with high frequencies (cymbals, vocals, etc.)
3. **Expected results**:
   - Knob left: Bright, clear sound
   - Knob right: Dull, muffled sound
4. **Notice**: Smooth transition between bright and dull

**You just built a real audio filter!** This is the foundation for all EQs and tone controls.

---

## Step 5: Simple Distortion Effect

### 5.1 Understanding Distortion
**Distortion clips (limits) audio to create harmonic content:**
```impala


```

### 5.2 Build Soft Clipping Distortion
```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {

        int inputLeft = signal[0]
        int inputRight = signal[1]
        

        int driveKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        

        int drive = 256 + (driveKnob * 7)
        

        int drivenLeft = (inputLeft * drive) / 256
        int drivenRight = (inputRight * drive) / 256
        

        int clippedLeft = drivenLeft
        if (drivenLeft > 1500) {
            clippedLeft = 1500 + ((drivenLeft - 1500) / 3)
        } else if (drivenLeft < -1500) {
            clippedLeft = -1500 + ((drivenLeft + 1500) / 3)
        }
        
        int clippedRight = drivenRight
        if (drivenRight > 1500) {
            clippedRight = 1500 + ((drivenRight - 1500) / 3)
        } else if (drivenRight < -1500) {
            clippedRight = -1500 + ((drivenRight + 1500) / 3)
        }
        

        if (clippedLeft > 2047) clippedLeft = 2047
        else if (clippedLeft < -2047) clippedLeft = -2047
        if (clippedRight > 2047) clippedRight = 2047
        else if (clippedRight < -2047) clippedRight = -2047
        

        displayLEDs[0] = driveKnob
        

        signal[0] = clippedLeft
        signal[1] = clippedRight
        
        yield()
    }
}
```

### 5.3 Test Distortion
1. **Compile and load**
2. **Turn knob 1** while playing music
3. **Expected results**:
   - Knob left: Clean sound
   - Knob right: Distorted, gritty sound
4. **Be careful**: Distortion can be loud - start at low volumes!

**You've created harmonic distortion!** This adds character and warmth to audio.

---

## Step 6: Combine Multiple Effects

### 6.1 Multi-Effect Processor
**Combine gain, filter, and distortion with multiple knobs:**

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

global int filterStateLeft = 0
global int filterStateRight = 0

function process()
{
    loop {

        int inputLeft = signal[0]
        int inputRight = signal[1]
        

        int gainKnob = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int filterKnob = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        int driveKnob = (int)global params[OPERAND_1_HIGH_PARAM_INDEX]
        int outputKnob = (int)global params[OPERAND_1_LOW_PARAM_INDEX]
        

        int gain = (gainKnob * 3) + 64
        int gainedLeft = (inputLeft * gain) / 256
        int gainedRight = (inputRight * gain) / 256
        

        int drive = 256 + (driveKnob * 4)
        int drivenLeft = (gainedLeft * drive) / 256
        int drivenRight = (gainedRight * drive) / 256
        

        if (drivenLeft > 1500) drivenLeft = 1500 + ((drivenLeft - 1500) / 3)
        else if (drivenLeft < -1500) drivenLeft = -1500 + ((drivenLeft + 1500) / 3)
        if (drivenRight > 1500) drivenRight = 1500 + ((drivenRight - 1500) / 3)
        else if (drivenRight < -1500) drivenRight = -1500 + ((drivenRight + 1500) / 3)
        

        int filterAmount = filterKnob
        filterStateLeft = ((drivenLeft * (255 - filterAmount)) + (filterStateLeft * filterAmount)) / 255
        filterStateRight = ((drivenRight * (255 - filterAmount)) + (filterStateRight * filterAmount)) / 255
        

        int outputLevel = outputKnob
        int finalLeft = (filterStateLeft * outputLevel) / 255
        int finalRight = (filterStateRight * outputLevel) / 255
        

        if (finalLeft > 2047) finalLeft = 2047
        else if (finalLeft < -2047) finalLeft = -2047
        if (finalRight > 2047) finalRight = 2047
        else if (finalRight < -2047) finalRight = -2047
        

        displayLEDs[0] = gainKnob
        displayLEDs[1] = filterKnob
        displayLEDs[2] = driveKnob
        displayLEDs[3] = outputKnob
        

        signal[0] = finalLeft
        signal[1] = finalRight
        
        yield()
    }
}
```

### 6.2 Test Multi-Effect Chain
1. **Compile and load**
2. **Experiment with all 4 knobs**:
   - Knob 1: Input gain (how hard you drive the effect)
   - Knob 2: Filter (brightness/dullness)
   - Knob 3: Distortion (clean to gritty)
   - Knob 4: Output level (final volume)
3. **Try combinations**: Low gain + high drive = gentle saturation

**You've built a complete multi-stage audio processor!**

---

## Step 7: Audio Processing Techniques

### 7.1 Common Processing Patterns

**Gain Staging:**
```impala

int processed = (input * effectAmount) / 256
int output = (processed * outputLevel) / 255
```

**State Management:**
```impala

global int previousValue = 0
int currentOutput = (input + previousValue) / 2
previousValue = currentOutput
```

**Parameter Scaling:**
```impala

int knobValue = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
int usefulValue = minRange + ((knobValue * (maxRange - minRange)) / 255)
```

### 7.2 Safety Practices

**Always Clip Outputs:**
```impala
if (output > 2047) output = 2047
else if (output < -2047) output = -2047
```

**Test with Different Audio:**
- Music with wide frequency content
- Pure tones to test specific frequencies
- Silence to check for noise
- Very loud signals to test clipping

**Start Subtle:**
```impala

int processed = (input * 7 + effect * 1) / 8


int processed = effect
```

---

## Step 8: What You've Accomplished

### 8.1 Audio Processing Skills
✅ **Real-time audio modification** with immediate results  
✅ **Multi-stage effect chains** combining multiple processes  
✅ **Parameter control** with hardware knob integration  
✅ **Safe audio practices** preventing clipping and artifacts  
✅ **Foundation techniques** for all audio effects  

### 8.2 Essential Processing Concepts
**Audio Flow Management:**
- Reading, processing, and outputting audio samples
- Multi-stage processing chains with proper gain staging
- State management for effects that remember previous samples
- Real-time parameter control with smooth response

**Mathematical Processing:**
- Amplitude scaling for gain and volume control
- Filter mathematics for frequency shaping
- Clipping algorithms for harmonic generation
- Parameter mapping for musical control ranges

---

## Step 9: Building on Audio Processing

### 9.1 Effect Categories You Can Now Build

**Dynamic Effects:**
```impala

if (input > threshold) output = input / ratio
else output = input


if (input < threshold) output = 0
else output = input
```

**Time-Based Effects:**
```impala

delayBuffer[writePos] = input
output = input + delayBuffer[readPos]



```

**Frequency Effects:**
```impala



```

### 9.2 Ready for Advanced Processing
**Build on your audio processing foundation:**
- 📖 [Simple Delay Explained](simple-delay-explained.md) - Add time-based processing
- 📖 [Build Your First Filter](build-your-first-filter.md) - Advanced frequency processing
- 📖 [Gain and Volume](../cookbook/fundamentals/gain-and-volume.md) - Professional gain control
- 📖 [Basic Filter](../cookbook/fundamentals/basic-filter.md) - Filter design principles

### 9.3 Professional Audio Processing
**Your processing foundation enables:**
- Multi-band EQ and dynamic processors
- Complex modulation and synthesis
- Professional mixing and mastering tools
- Creative sound design and effects
- Real-time performance instruments

**🎉 You're now an audio processor designer!** You understand how to transform audio in real-time, the fundamental skill behind all audio effects, instruments, and processing tools. Every professional audio plugin uses these same basic concepts you've just mastered.