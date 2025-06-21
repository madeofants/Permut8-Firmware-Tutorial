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

// Audio and parameter constants
const int PARAM_MAX = 255
const int BUFFER_SIZE = 4096
const int GRAIN_SIZE_MIN = 128
const int GRAIN_SIZE_MULT = 15
const int PITCH_MIN = 64
const int PITCH_MULT = 2
const int LED_MASK = 255

// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX = 0
const int OPERAND_1_LOW_PARAM_INDEX = 1
const int OPERAND_2_LOW_PARAM_INDEX = 2
const int OPERAND_2_HIGH_PARAM_INDEX = 3
const int OPERATOR_1_PARAM_INDEX = 4
const int OPERATOR_2_PARAM_INDEX = 5
const int SWITCHES_PARAM_INDEX = 6
const int CLOCK_FREQ_PARAM_INDEX = 7
const int PARAM_COUNT = 8

// Required global variables (but with custom meanings)
global array signal[2]          // Audio input/output
global array params[PARAM_COUNT]          // Hardware controls with custom meanings
global array displayLEDs[4]     // Custom LED behaviors
global clock
global clockFreqLimit

// Completely custom interface labels
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

// Custom effect state (no operator concepts)
global array grainBuffer[BUFFER_SIZE]
global grainWritePos = 0
global grainSize = 512
global grainSpray = 100
global pitchShift = 256
global wetMix = 128
global grainPhase = 0
global randomSeed = 12345

// Custom granular processing (completely unrelated to operators)
function processGranularEffect() {
    locals switches, freezeMode, reverseMode, chorusMode, glitchMode, inputLeft, inputRight
    locals baseReadPos, sprayOffset, grainReadPos, grainSample, chorusPos, chorusSample
    locals wetLeft, wetRight, outputLeft, outputRight
    
    // === CUSTOM PARAMETER MAPPING ===
    // These parameters have NOTHING to do with operators/operands
    grainSize = (params[OPERAND_1_HIGH_PARAM_INDEX] * GRAIN_SIZE_MULT) + GRAIN_SIZE_MIN        // Control 1: 128-4000 samples
    grainSpray = params[OPERAND_1_LOW_PARAM_INDEX]                    // Control 2: 0-255 randomness
    pitchShift = (params[OPERAND_2_HIGH_PARAM_INDEX] * PITCH_MULT) + PITCH_MIN         // Control 3: 64-574 (pitch range)
    wetMix = params[OPERAND_2_LOW_PARAM_INDEX]                        // Control 4: 0-255 dry/wet
    
    // === CUSTOM SWITCH BEHAVIOR ===
    switches = params[SWITCHES_PARAM_INDEX]
    freezeMode = (switches & 0x01) != 0        // Switch 1: Freeze grains
    reverseMode = (switches & 0x02) != 0       // Switch 2: Reverse grains
    chorusMode = (switches & 0x04) != 0        // Switch 3: Chorus effect
    glitchMode = (switches & 0x08) != 0        // Switch 4: Glitch mode
    
    // === AUDIO INPUT ===
    inputLeft = signal[0]
    inputRight = signal[1]
    
    // === GRANULAR PROCESSING ===
    // Write input to grain buffer (unless frozen)
    if (!freezeMode) {
        grainBuffer[grainWritePos] = inputLeft
        grainWritePos = (grainWritePos + 1) % BUFFER_SIZE
    }
    
    // Calculate grain read position with randomness
    baseReadPos = grainWritePos - grainSize
    sprayOffset = (customRandom() * grainSpray) / PARAM_MAX
    grainReadPos = baseReadPos + sprayOffset
    
    // Handle wrapping
    if (grainReadPos < 0) grainReadPos = grainReadPos + BUFFER_SIZE
    if (grainReadPos >= BUFFER_SIZE) grainReadPos = grainReadPos - BUFFER_SIZE
    
    // Read grain with pitch shifting
    grainSample = grainBuffer[grainReadPos]
    
    // Apply pitch shifting by varying read rate
    if (pitchShift != 256) {
        grainPhase = grainPhase + pitchShift
        if (grainPhase >= 256) {
            grainPhase = grainPhase - 256
            grainReadPos = (grainReadPos + 1) % BUFFER_SIZE
            grainSample = grainBuffer[grainReadPos]
        }
    }
    
    // Apply reverse mode
    if (reverseMode) {
        grainSample = -grainSample
    }
    
    // Apply chorus mode (multiple grains)
    if (chorusMode) {
        chorusPos = (grainReadPos + (grainSize / 2)) % BUFFER_SIZE
        chorusSample = grainBuffer[chorusPos]
        grainSample = (grainSample + chorusSample) / 2
    }
    
    // Apply glitch mode (sample corruption)
    if (glitchMode && (customRandom() < 20)) {
        grainSample = (grainSample << 2) | (grainSample >> 10)  // Bit shift corruption
    }
    
    // === DRY/WET MIXING ===
    wetLeft = grainSample
    wetRight = grainSample  // Mono grain effect
    
    outputLeft = ((inputLeft * (PARAM_MAX - wetMix)) + (wetLeft * wetMix)) >> 8
    outputRight = ((inputRight * (PARAM_MAX - wetMix)) + (wetRight * wetMix)) >> 8
    
    // === OUTPUT ===
    signal[0] = outputLeft
    signal[1] = outputRight
}

// Custom random number generator (no relation to RND operator)
function customRandom() returns value {
    randomSeed = (randomSeed * 1103515245 + 12345) & 0x7FFFFFFF
    value = (randomSeed >> 16) & LED_MASK
}

// Custom LED animations (completely unrelated to operator feedback)
function updateCustomLEDs() {
    locals sizePattern, ledCount, i, activityLevel, sprayPattern, pitchPattern, mixLevel, modeIndicators, switches
    
    // === LED 1: Grain Size Visualization ===
    sizePattern = 0
    ledCount = (grainSize >> 9) + 1  // 1-8 LEDs based on grain size
    for (i = 0; i < ledCount && i < 8; i++) {
        sizePattern |= (1 << i)
    }
    displayLEDs[0] = sizePattern
    
    // === LED 2: Activity and Spray Indicator ===
    activityLevel = (abs(signal[0]) + abs(signal[1])) >> 6  // Audio activity
    sprayPattern = (grainSpray >> 3) & 0x1F  // Spray amount
    displayLEDs[1] = (activityLevel << 5) | sprayPattern
    
    // === LED 3: Pitch Shift Visualization ===
    pitchPattern = 0
    if (pitchShift < 256) {
        // Lower pitch - LEDs from center down
        pitchPattern = 0x0F >> ((256 - pitchShift) >> 6)
    } else {
        // Higher pitch - LEDs from center up  
        pitchPattern = 0xF0 >> ((pitchShift - 256) >> 6)
    }
    displayLEDs[2] = pitchPattern
    
    // === LED 4: Mix Level and Mode Indicators ===
    mixLevel = wetMix >> 3  // 0-31 for first 5 LEDs
    modeIndicators = 0
    
    // Add mode indicators to top 3 LEDs
    switches = params[SWITCHES_PARAM_INDEX]
    if (switches & 0x01) modeIndicators |= 0x20  // Freeze mode
    if (switches & 0x02) modeIndicators |= 0x40  // Reverse mode
    if (switches & 0x04) modeIndicators |= 0x80  // Chorus mode
    
    displayLEDs[3] = mixLevel | modeIndicators
}

// Main processing function
function process() {
    loop {
        processGranularEffect()
        updateCustomLEDs()
        yield()
    }
}

// Custom update function (ignores operator parameter changes)
function update() {
    // Only update when OUR parameters change, ignore operator-related changes
    // This would normally be called when operator/operand changes, but we ignore that
    
    // Could add parameter smoothing or other custom update behavior here
    // For example, smooth parameter changes to avoid audio artifacts:
    
    // static lastGrainSize = 512
    // targetGrainSize = (params[OPERAND_1_HIGH_PARAM_INDEX] * 15) + 128
    // lastGrainSize = (lastGrainSize * 7 + targetGrainSize) / 8  // Smooth transition
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
freezeMode = (switches & 0x01) != 0    // Switch 1: Freeze grain buffer
reverseMode = (switches & 0x02) != 0   // Switch 2: Reverse grain playback
chorusMode = (switches & 0x04) != 0    // Switch 3: Multi-grain chorus
glitchMode = (switches & 0x08) != 0    // Switch 4: Random bit corruption
```

**Custom Switch Behaviors**:
- **Freeze**: Stops writing new audio to grain buffer
- **Reverse**: Inverts grain audio signal
- **Chorus**: Plays multiple grains simultaneously
- **Glitch**: Random digital corruption effects

### **Custom LED Patterns**

```impala
displayLEDs[0] = // Grain size as progressive LED bar
displayLEDs[1] = // Audio activity + spray randomness
displayLEDs[2] = // Pitch shift direction and amount
displayLEDs[3] = // Mix level + active mode indicators
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
    "GRAIN |---- SIZE ---| |---- SPRAY ----|",  // Replace operator 1 display
    "",
    "",
    "",
    "GRAIN |--- PITCH ---| |---- MIX -----|"   // Replace operator 2 display
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