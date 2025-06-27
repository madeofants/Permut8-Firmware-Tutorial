# Custom Interface Bypass Tutorial
*Create effects that completely bypass Permut8's original UI elements*

## What This Tutorial Teaches

This tutorial demonstrates how to create effects that **completely ignore** Permut8's original interface system and create an entirely custom user experience:

- **Bypass all operator concepts** - No operators, operands, or instruction processing
- **Custom parameter meanings** - Transform knobs into direct effect controls
- **Custom LED behaviors** - Create visual feedback unrelated to operator system
- **Custom switch usage** - Use switches for effect-specific functions
- **Complete interface override** - Design your own control paradigm

### **Approach: Custom Firmware (Complete Bypass)**

This demonstrates **Approach 2: Custom Firmware** with complete interface override - ignoring all operator system concepts and creating a totally custom user experience.

**Why This Approach?**:
- **Creative freedom** - Design any interface that makes sense for your effect
- **User-friendly controls** - Make complex algorithms accessible with simple knobs
- **Modern interface design** - Create interfaces that match contemporary effects
- **Educational clarity** - Focus on the effect algorithm without operator complexity

## Complete Code: Custom Granular Effect

```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

extern native yield
extern native read
extern native write


const int PARAM_MAX = 255
const int BUFFER_SIZE = 4096
const int GRAIN_SIZE_MIN = 128
const int GRAIN_SIZE_MULT = 15
const int PITCH_MIN = 64
const int PITCH_MULT = 2
const int LED_MASK = 255


const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8


global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global clock
global clockFreqLimit


readonly array panelTextRows[8] = {
    "",
    "",
    "",
    "GRAIN |---- SIZE ---| |---- SPRAY ----|",
    "",
    "",
    "",
    "GRAIN |--- PITCH ---| |---- MIX -----|"
}


global array grainBuffer[BUFFER_SIZE]
global grainWritePos = 0
global grainSize = 512
global grainSpray = 100
global pitchShift = 256
global wetMix = 128
global grainPhase = 0
global randomSeed = 12345


function processGranularEffect() {
    locals switches, freezeMode, reverseMode, chorusMode, glitchMode, inputLeft, inputRight
    locals baseReadPos, sprayOffset, grainReadPos, grainSample, chorusPos, chorusSample
    locals wetLeft, wetRight, outputLeft, outputRight
    


    grainSize = (params[OPERAND_1_HIGH_PARAM_INDEX] * GRAIN_SIZE_MULT) + GRAIN_SIZE_MIN
    grainSpray = params[OPERAND_1_LOW_PARAM_INDEX]
    pitchShift = (params[OPERAND_2_HIGH_PARAM_INDEX] * PITCH_MULT) + PITCH_MIN
    wetMix = params[OPERAND_2_LOW_PARAM_INDEX]
    

    switches = params[SWITCHES_PARAM_INDEX]
    freezeMode = (switches & 0x01) != 0
    reverseMode = (switches & 0x02) != 0
    chorusMode = (switches & 0x04) != 0
    glitchMode = (switches & 0x08) != 0
    

    inputLeft = signal[0]
    inputRight = signal[1]
    


    if (!freezeMode) {
        grainBuffer[grainWritePos] = inputLeft
        grainWritePos = (grainWritePos + 1) % BUFFER_SIZE
    }
    

    baseReadPos = grainWritePos - grainSize
    sprayOffset = (customRandom() * grainSpray) / PARAM_MAX
    grainReadPos = baseReadPos + sprayOffset
    

    if (grainReadPos < 0) grainReadPos = grainReadPos + BUFFER_SIZE
    if (grainReadPos >= BUFFER_SIZE) grainReadPos = grainReadPos - BUFFER_SIZE
    

    grainSample = grainBuffer[grainReadPos]
    

    if (pitchShift != 256) {
        grainPhase = grainPhase + pitchShift
        if (grainPhase >= 256) {
            grainPhase = grainPhase - 256
            grainReadPos = (grainReadPos + 1) % BUFFER_SIZE
            grainSample = grainBuffer[grainReadPos]
        }
    }
    

    if (reverseMode) {
        grainSample = -grainSample
    }
    

    if (chorusMode) {
        chorusPos = (grainReadPos + (grainSize / 2)) % BUFFER_SIZE
        chorusSample = grainBuffer[chorusPos]
        grainSample = (grainSample + chorusSample) / 2
    }
    

    if (glitchMode && (customRandom() < 20)) {
        grainSample = (grainSample << 2) | (grainSample >> 10)
    }
    

    wetLeft = grainSample
    wetRight = grainSample
    
    outputLeft = ((inputLeft * (PARAM_MAX - wetMix)) + (wetLeft * wetMix)) >> 8
    outputRight = ((inputRight * (PARAM_MAX - wetMix)) + (wetRight * wetMix)) >> 8
    

    signal[0] = outputLeft
    signal[1] = outputRight
}


function customRandom() returns value {
    randomSeed = (randomSeed * 1103515245 + 12345) & 0x7FFFFFFF
    value = (randomSeed >> 16) & LED_MASK
}


function updateCustomLEDs() {
    locals sizePattern, ledCount, i, activityLevel, sprayPattern, pitchPattern, mixLevel, modeIndicators, switches
    

    sizePattern = 0
    ledCount = (grainSize >> 9) + 1
    for (i = 0; i < ledCount && i < 8; i++) {
        sizePattern |= (1 << i)
    }
    displayLEDs[0] = sizePattern
    

    activityLevel = (abs(signal[0]) + abs(signal[1])) >> 6
    sprayPattern = (grainSpray >> 3) & 0x1F
    displayLEDs[1] = (activityLevel << 5) | sprayPattern
    

    pitchPattern = 0
    if (pitchShift < 256) {

        pitchPattern = 0x0F >> ((256 - pitchShift) >> 6)
    } else {

        pitchPattern = 0xF0 >> ((pitchShift - 256) >> 6)
    }
    displayLEDs[2] = pitchPattern
    

    mixLevel = wetMix >> 3
    modeIndicators = 0
    

    switches = params[SWITCHES_PARAM_INDEX]
    if (switches & 0x01) modeIndicators |= 0x20
    if (switches & 0x02) modeIndicators |= 0x40
    if (switches & 0x04) modeIndicators |= 0x80
    
    displayLEDs[3] = mixLevel | modeIndicators
}


function process() {
    loop {
        processGranularEffect()
        updateCustomLEDs()
        yield()
    }
}


function update() {


    


    



}
```

## Custom Interface Design

### **Parameter Mapping (No Operator Concepts)**

| Parameter | Operator Meaning | Our Custom Meaning |
|-----------|------------------|-------------------|
| `params[CLOCK_FREQ_PARAM_INDEX]` | Clock Frequency | **IGNORED** |
| `params[SWITCHES_PARAM_INDEX]` | Switch States | **Custom switch functions** |
| `params[OPERATOR_1_PARAM_INDEX]` | Operator 1 Type | **IGNORED** |
| `params[OPERAND_1_HIGH_PARAM_INDEX]` | Instruction 1 High | **Grain Size (128-4000 samples)** |
| `params[OPERAND_1_LOW_PARAM_INDEX]` | Instruction 1 Low | **Grain Spray (0-255 randomness)** |
| `params[OPERATOR_2_PARAM_INDEX]` | Operator 2 Type | **IGNORED** |
| `params[OPERAND_2_HIGH_PARAM_INDEX]` | Instruction 2 High | **Pitch Shift (64-574 range)** |
| `params[OPERAND_2_LOW_PARAM_INDEX]` | Instruction 2 Low | **Dry/Wet Mix (0-255)** |

### **Custom Switch Functions**

```impala
switches = params[SWITCHES_PARAM_INDEX]
freezeMode = (switches & 0x01) != 0
reverseMode = (switches & 0x02) != 0
chorusMode = (switches & 0x04) != 0
glitchMode = (switches & 0x08) != 0
```

**Custom Switch Behaviors**:
- **Freeze**: Stops writing new audio to grain buffer
- **Reverse**: Inverts grain audio signal
- **Chorus**: Plays multiple grains simultaneously
- **Glitch**: Random digital corruption effects

### **Custom LED Patterns**

```impala
displayLEDs[0] =
displayLEDs[1] =
displayLEDs[2] =
displayLEDs[3] =
```

**LED Behaviors**:
- **Display 1**: Progressive bar showing grain size
- **Display 2**: Real-time audio activity combined with spray amount
- **Display 3**: Pitch shift visualization (center = normal, up/down = pitch)
- **Display 4**: Mix level with mode indicator LEDs

### **Interface Override**

```impala
readonly array panelTextRows[8] = {
    "",
    "",  
    "",
    "GRAIN |---- SIZE ---| |---- SPRAY ----|",
    "",
    "",
    "",
    "GRAIN |--- PITCH ---| |---- MIX -----|"
};
```

**Visual Transformation**:
- **Original**: Hex operand values on LED displays
- **Custom**: Clear "GRAIN SIZE", "SPRAY", "PITCH", "MIX" labels
- **User Experience**: Intuitive effect controls instead of abstract operators

## Bank Configuration

```
Permut8BankV2: {
    CurrentProgram: A0
    Programs: {
        A0: { Name: "Smooth Grains", Operator1: "0", Operator2: "0" }
        A1: { Name: "Glitch Grains", Operator1: "0", Operator2: "0" }
        A2: { Name: "Pitched Grains", Operator1: "0", Operator2: "0" }
        A3: { Name: "Frozen Grains", Operator1: "0", Operator2: "0" }
    }
    Firmware: {
        Name: "granular_bypass"
        Code: { [YOUR GAZL CODE] }
    }
}
```

**Note**: All operators set to NOP (0) because we completely ignore the operator system.

## Using the Custom Interface

### **Basic Operation**
1. **Load the bank** and select a preset
2. **Ignore operator interface** - our firmware takes complete control
3. **Use knobs directly**:
   - Control 1: Grain size (texture detail)
   - Control 2: Spray amount (randomness)
   - Control 3: Pitch shift (up/down pitch)
   - Control 4: Dry/wet mix

### **Switch Functions**
- **Switch 1 (Freeze)**: Hold current grain content
- **Switch 2 (Reverse)**: Flip grain audio
- **Switch 3 (Chorus)**: Layer multiple grains
- **Switch 4 (Glitch)**: Add digital corruption

### **LED Monitoring**
- **Watch all displays** for real-time effect feedback
- **LED patterns** show parameter states and audio activity
- **Mode indicators** show which switches are active

## Key Design Principles

### **Complete Independence**
- **No operator concepts** - firmware ignores all operator/operand meanings
- **Custom parameter semantics** - each knob has a specific, effect-related function
- **Original interface bypass** - users never interact with operator system
- **Modern UX design** - familiar knob-per-function interface

### **User-Centric Design**
- **Intuitive controls** - each knob directly affects one aspect of the effect
- **Clear labeling** - `panelTextRows` provides obvious parameter names
- **Visual feedback** - LEDs show parameter states and audio activity
- **Mode indication** - switches have clear, effect-specific functions

### **Algorithm Focus**
- **Effect-specific code** - granular algorithm designed for this interface
- **No operator constraints** - algorithm designed around the desired user experience
- **Custom behaviors** - switches and LEDs designed for the specific effect
- **Performance optimization** - code optimized for the specific algorithm, not generic operators

## Comparison: Original vs Custom Interface

### **Original Interface Approach**
```
User → Operator Selection → Operand Values → Generic Processing → Audio Output
```
- User selects SUB operator + sets operand values via switches
- Generic delay processing with limited customization
- Hex values on LED displays
- Abstract operator concepts

### **Custom Interface Approach**  
```
User → Direct Effect Controls → Custom Algorithm → Audio Output
```
- User directly controls grain size, spray, pitch, mix
- Specialized granular algorithm optimized for interface
- Clear parameter labels and visual feedback  
- Intuitive, effect-specific controls

## When to Use Custom Interface

### **Perfect For**:
- **Complex algorithms** that don't fit operator paradigm
- **Modern effect interfaces** with intuitive controls
- **Educational projects** focusing on algorithm understanding
- **Creative effects** that need custom user experience

### **Consider Original Interface When**:
- **Building standard effects** (delays, modulation, pitch)
- **Maintaining compatibility** with existing workflows
- **Learning operator system** concepts and relationships
- **Leveraging hardware optimization** of built-in operators

## Key Learning Points

### **Complete Creative Freedom**
- **Any interface design** - not constrained by operator concepts
- **Custom parameter meanings** - design controls around your algorithm
- **Modern UX patterns** - create interfaces users expect
- **Algorithm-specific optimization** - code designed for your exact use case

### **Interface Design Skills**
- **Parameter mapping** - translate hardware controls to effect parameters
- **Visual feedback design** - create meaningful LED patterns
- **User experience thinking** - design from user perspective
- **Switch utilization** - repurpose switches for effect-specific functions

**Result**: A granular effect that feels like a modern plugin with intuitive controls, completely bypassing Permut8's operator system while still using the same hardware interface.

---

*Previous: [Complete UI Control with Delay](complete-ui-control-with-delay.md) - Learn to use all UI elements*