# Light Up LEDs - Instant Visual Feedback

## What This Tutorial Does
Master Permut8's LED displays to create visual feedback for your plugins. In 10 minutes, you'll understand how to control all LED patterns and create informative, beautiful visual displays that help users understand what your plugin is doing.

## What You'll Learn
- How Permut8's LED system works
- Control individual LEDs and create patterns
- Display parameter values visually
- Create animated displays and activity indicators
- Design intuitive visual feedback for any plugin

**Prerequisites**: [Getting Audio In and Out](getting-audio-in-and-out.md)  
**Time Required**: 10 minutes  
**Difficulty**: Beginner

---

## Step 1: Understanding the LED System

### 1.1 Hardware Layout
**Permut8 has 4 LED displays**, each with **8 individual LEDs**:
```impala
global array displayLEDs[4]





```

### 1.2 How LED Values Work
**Each display is controlled by a single number (0-PARAM_MAX)**:
```impala
displayLEDs[0] = 0x00
displayLEDs[0] = 0x01
displayLEDs[0] = 0xFF
displayLEDs[0] = 0x0F
```

### 1.3 Binary Pattern Basics
**Each bit controls one LED:**
```
LED Position:  8  7  6  5  4  3  2  1
Binary:        0  0  0  0  0  0  0  1  = 0x01 (decimal 1)
Binary:        1  1  1  1  0  0  0  0  = 0xF0 (decimal 240)
Binary:        1  0  1  0  1  0  1  0  = 0xAA (decimal 170)
```

---

## Step 2: Your First LED Control

### 2.1 Basic LED Test
Create `led_test.impala`:

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2




const int PARAM_MAX = 255
const int PARAM_MIN = 0
const int PARAM_MID = 128
const int PARAM_SWITCH_THRESHOLD = 127


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int AUDIO_ZERO = 0


const int SAMPLE_RATE_44K1 = 44100
const int SAMPLE_RATE_HALF = 22050
const int SAMPLE_RATE_QUARTER = 11025


const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_DOUBLE = 0x03
const int LED_QUAD = 0x0F


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300

function process()
{
    loop {

        displayLEDs[0] = LED_SINGLE
        displayLEDs[1] = LED_DOUBLE
        displayLEDs[2] = LED_QUAD
        displayLEDs[3] = LED_ALL_ON
        

        yield()
    }
}
```

### 2.2 Test Static Patterns
1. **Compile**: `PikaCmd.exe -compile led_test.impala`
2. **Load**: `patch led_test.gazl`
3. **Expected result**: You should see different LED patterns on each display
4. **Success indicator**: LEDs show different patterns as programmed

**🎉 You're controlling the lights!** Each display shows a different pattern.

---

## Step 3: Common LED Patterns

### 3.1 Useful LED Pattern Values
**Memorize these common patterns:**

```impala

displayLEDs[0] = LED_OFF
displayLEDs[0] = LED_SINGLE
displayLEDs[0] = 0x80
displayLEDs[0] = LED_ALL_ON


displayLEDs[0] = 0x01
displayLEDs[0] = 0x03
displayLEDs[0] = 0x07
displayLEDs[0] = 0x0F
displayLEDs[0] = 0x1F
displayLEDs[0] = 0x3F
displayLEDs[0] = 0x7F
displayLEDs[0] = 0xFF


displayLEDs[0] = 0xAA
displayLEDs[0] = 0x55
displayLEDs[0] = 0x18
displayLEDs[0] = 0x81
```

### 3.2 Pattern Test Plugin
Test all the common patterns:

```impala
function process()
{
    loop {

        static int counter = 0
        counter = (counter + 1) % SAMPLE_RATE_44K1
        
        int pattern = counter / (SAMPLE_RATE_44K1 / 8)
        
        if (pattern == 0) displayLEDs[0] = 0x01
        else if (pattern == 1) displayLEDs[0] = 0x03
        else if (pattern == 2) displayLEDs[0] = 0x07
        else if (pattern == 3) displayLEDs[0] = 0x0F
        else if (pattern == 4) displayLEDs[0] = 0x1F
        else if (pattern == 5) displayLEDs[0] = 0x3F
        else if (pattern == 6) displayLEDs[0] = 0x7F
        else displayLEDs[0] = 0xFF
        
        yield()
    }
}
```

**This creates an animated bar graph** that grows and shrinks automatically.

---

## Step 4: Parameter Visualization

### 4.1 Show Knob Values with LEDs
**Convert knob values (0-255) to LED bar graphs:**

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2




const int PARAM_MAX = 255
const int PARAM_MIN = 0
const int PARAM_MID = 128
const int PARAM_SWITCH_THRESHOLD = 127


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int AUDIO_ZERO = 0


const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_DOUBLE = 0x03
const int LED_QUAD = 0x0F


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300

function process()
{
    loop {

        int knob1 = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        int knob2 = (int)global params[OPERAND_2_LOW_PARAM_INDEX]
        

        int leds1 = 0
        if (knob1 > (PARAM_MAX * 7 / 8)) leds1 = 0xFF
        else if (knob1 > (PARAM_MAX * 6 / 8)) leds1 = 0x7F
        else if (knob1 > (PARAM_MAX * 5 / 8)) leds1 = 0x3F
        else if (knob1 > PARAM_MID) leds1 = 0x1F
        else if (knob1 > (PARAM_MAX * 3 / 8)) leds1 = LED_QUAD
        else if (knob1 > (PARAM_MAX / 4)) leds1 = 0x07
        else if (knob1 > (PARAM_MAX / 8)) leds1 = LED_DOUBLE
        else if (knob1 > PARAM_MIN) leds1 = LED_SINGLE
        else leds1 = LED_OFF
        

        int leds2 = 0
        if (knob2 > (PARAM_MAX * 7 / 8)) leds2 = 0xFF
        else if (knob2 > (PARAM_MAX * 6 / 8)) leds2 = 0x7F
        else if (knob2 > (PARAM_MAX * 5 / 8)) leds2 = 0x3F
        else if (knob2 > PARAM_MID) leds2 = 0x1F
        else if (knob2 > (PARAM_MAX * 3 / 8)) leds2 = LED_QUAD
        else if (knob2 > (PARAM_MAX / 4)) leds2 = 0x07
        else if (knob2 > (PARAM_MAX / 8)) leds2 = LED_DOUBLE
        else if (knob2 > PARAM_MIN) leds2 = LED_SINGLE
        else leds2 = LED_OFF
        

        displayLEDs[0] = leds1
        displayLEDs[1] = leds2
        
        yield()
    }
}
```

### 4.2 Test Parameter Display
1. **Compile and load**
2. **Turn knobs 1 and 2**
3. **Expected result**: LED displays show knob positions as bar graphs
4. **Success indicator**: LEDs respond immediately to knob movements

**Now you have visual parameter feedback!**

---

## Step 5: Audio Level Meters

### 5.1 Create Audio Activity Display
**Show audio signal levels on LEDs:**

```impala
function process()
{
    loop {

        int leftLevel = signal[0]
        if (leftLevel < 0) leftLevel = -leftLevel
        
        int rightLevel = signal[1]
        if (rightLevel < 0) rightLevel = -rightLevel
        

        int leftLEDs = 0
        if (leftLevel > (AUDIO_MAX * 7 / 8)) leftLEDs = LED_ALL_ON
        else if (leftLevel > (AUDIO_MAX * 6 / 8)) leftLEDs = 0x7F
        else if (leftLevel > (AUDIO_MAX * 5 / 8)) leftLEDs = 0x3F
        else if (leftLevel > (AUDIO_MAX * 4 / 8)) leftLEDs = 0x1F
        else if (leftLevel > (AUDIO_MAX * 3 / 8)) leftLEDs = LED_QUAD
        else if (leftLevel > (AUDIO_MAX * 2 / 8)) leftLEDs = 0x07
        else if (leftLevel > (AUDIO_MAX / 8)) leftLEDs = LED_DOUBLE
        else if (leftLevel > (AUDIO_MAX / 20)) leftLEDs = LED_SINGLE
        else leftLEDs = LED_OFF
        

        int rightLEDs = 0
        if (rightLevel > (AUDIO_MAX * 7 / 8)) rightLEDs = LED_ALL_ON
        else if (rightLevel > (AUDIO_MAX * 6 / 8)) rightLEDs = 0x7F
        else if (rightLevel > (AUDIO_MAX * 5 / 8)) rightLEDs = 0x3F
        else if (rightLevel > (AUDIO_MAX * 4 / 8)) rightLEDs = 0x1F
        else if (rightLevel > (AUDIO_MAX * 3 / 8)) rightLEDs = LED_QUAD
        else if (rightLevel > (AUDIO_MAX * 2 / 8)) rightLEDs = 0x07
        else if (rightLevel > (AUDIO_MAX / 8)) rightLEDs = LED_DOUBLE
        else if (rightLevel > (AUDIO_MAX / 20)) rightLEDs = LED_SINGLE
        else rightLEDs = LED_OFF
        

        displayLEDs[0] = leftLEDs
        displayLEDs[1] = rightLEDs
        
        yield()
    }
}
```

### 5.2 Test Audio Metering
1. **Play audio** through the plugin
2. **Expected result**: LEDs show audio activity levels
3. **Loud audio**: More LEDs light up
4. **Quiet audio**: Fewer LEDs light up
5. **No audio**: All LEDs off

**You've created professional audio meters!**

---

## Step 6: Moving and Animated Patterns

### 6.1 Create Moving Dot Pattern
**Animate a single LED moving across the display:**

```impala
function process()
{
    loop {

        static int position = 0
        static int counter = 0
        
        counter = (counter + 1) % (SAMPLE_RATE_44K1 / 20)
        if (counter == 0) {
            position = (position + 1) % 8
        }
        

        int movingDot = 1 << position
        displayLEDs[0] = movingDot
        

        int reversePosition = 7 - position
        int reverseDot = 1 << reversePosition
        displayLEDs[1] = reverseDot
        
        yield()
    }
}
```

### 6.2 Knight Rider Pattern
**Create the classic scanning pattern:**

```impala
function process()
{
    loop {
        static int position = 0
        static int direction = 1
        static int counter = 0
        
        counter = (counter + 1) % (SAMPLE_RATE_44K1 / 40)
        if (counter == 0) {
            position = position + direction
            

            if (position >= 7) {
                position = 7
                direction = -1
            } else if (position <= 0) {
                position = 0
                direction = 1
            }
        }
        

        int pattern = (1 << position)
        if (position > 0) pattern |= (1 << (position - 1)) / 2
        if (position < 7) pattern |= (1 << (position + 1)) / 2
        
        displayLEDs[0] = pattern
        
        yield()
    }
}
```

---

## Step 7: Advanced LED Techniques

### 7.1 LED Helper Functions
**Create reusable functions for common patterns:**

```impala

function valueToBarGraph(int value)
returns int ledPattern
{
    if (value > (PARAM_MAX * 7 / 8)) ledPattern = LED_ALL_ON
    else if (value > (PARAM_MAX * 6 / 8)) ledPattern = 0x7F
    else if (value > (PARAM_MAX * 5 / 8)) ledPattern = 0x3F
    else if (value > PARAM_MID) ledPattern = 0x1F
    else if (value > (PARAM_MAX * 3 / 8)) ledPattern = LED_QUAD
    else if (value > (PARAM_MAX / 4)) ledPattern = 0x07
    else if (value > (PARAM_MAX / 8)) ledPattern = LED_DOUBLE
    else if (value > PARAM_MIN) ledPattern = LED_SINGLE
    else ledPattern = LED_OFF
}


function positionToLED(int position)
returns int ledPattern
{
    if (position >= 8) position = 7
    if (position < 0) position = 0
    ledPattern = 1 << position
}


function blinkingPattern(int basePattern, int speed)
returns int ledPattern
{
    static int blinkCounter = 0
    blinkCounter = (blinkCounter + 1) % speed
    
    if (blinkCounter < (speed / 2)) {
        ledPattern = basePattern
    } else {
        ledPattern = 0x00
    }
}
```

### 7.2 Complete LED Showcase
**Comprehensive LED control example:**

```impala

const int PRAWN_FIRMWARE_PATCH_FORMAT = 2




const int PARAM_MAX = 255
const int PARAM_MIN = 0
const int PARAM_MID = 128
const int PARAM_SWITCH_THRESHOLD = 127


const int AUDIO_MAX = 2047
const int AUDIO_MIN = -2047
const int AUDIO_ZERO = 0


const int SAMPLE_RATE_44K1 = 44100
const int SAMPLE_RATE_HALF = 22050
const int SAMPLE_RATE_QUARTER = 11025


const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_DOUBLE = 0x03
const int LED_QUAD = 0x0F


const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT


global int clock = 0
global array signal[2]
global array params[PARAM_COUNT]
global array displayLEDs[4]
global int clockFreqLimit = 132300

function process()
{
    loop {

        int knob1Value = (int)global params[OPERAND_2_HIGH_PARAM_INDEX]
        displayLEDs[0] = valueToBarGraph(knob1Value)
        

        int leftLevel = signal[0]
        if (leftLevel < 0) leftLevel = -leftLevel
        int scaledLevel = (leftLevel * PARAM_MAX) / AUDIO_MAX
        displayLEDs[1] = valueToBarGraph(scaledLevel)
        

        static int dotPosition = 0
        static int dotCounter = 0
        int speed = 100 + (((int)global params[OPERAND_2_LOW_PARAM_INDEX] * 2000) / PARAM_MAX)
        
        dotCounter = (dotCounter + 1) % speed
        if (dotCounter == 0) {
            dotPosition = (dotPosition + 1) % 8
        }
        displayLEDs[2] = positionToLED(dotPosition)
        

        int activity = (scaledLevel > 10) ? LED_ALL_ON : LED_SINGLE
        displayLEDs[3] = blinkingPattern(activity, (SAMPLE_RATE_44K1 / 20))
        
        yield()
    }
}
```

---

## Step 8: LED Design Guidelines

### 8.1 User Experience Principles
**Good LED feedback should be:**

✅ **Immediate**: Responds instantly to changes  
✅ **Intuitive**: Pattern meaning is obvious  
✅ **Informative**: Shows useful information  
✅ **Not distracting**: Doesn't interfere with music-making  
✅ **Consistent**: Same patterns mean same things across displays  

### 8.2 Common LED Usage Patterns

| LED Purpose | Pattern Type | Example |
|-------------|--------------|---------|
| **Parameter Value** | Bar graph | `valueToBarGraph(knobValue)` |
| **Audio Level** | Bar meter | More LEDs = louder audio |
| **Selection/Mode** | Position indicator | Different LED for each mode |
| **Activity Status** | Blink/flash | Flash when processing audio |
| **Range/Zone** | Multiple LEDs | Group of LEDs for frequency bands |

### 8.3 LED Pattern Library
**Save these patterns for future use:**

```impala

const int LED_OFF = 0x00
const int LED_ALL_ON = 0xFF
const int LED_SINGLE = 0x01
const int LED_LAST = 0x80
const int LED_ENDS = 0x81
const int LED_CENTER = 0x18
const int LED_ALTERNATE1 = 0xAA
const int LED_ALTERNATE2 = 0x55
const int LED_BAR_1 = 0x01
const int LED_BAR_2 = 0x03
const int LED_BAR_3 = 0x07
const int LED_BAR_4 = 0x0F
const int LED_BAR_5 = 0x1F
const int LED_BAR_6 = 0x3F
const int LED_BAR_7 = 0x7F
const int LED_BAR_8 = 0xFF
```

---

## Step 9: What You've Mastered

### 9.1 LED Control Skills
✅ **LED bit pattern control** with binary values  
✅ **Parameter visualization** with bar graphs  
✅ **Audio level metering** with real-time display  
✅ **Animated patterns** with moving and blinking effects  
✅ **Professional LED design** with user experience principles  

### 9.2 Visual Feedback Concepts
**Essential Patterns:**
- Converting numerical values to visual patterns
- Real-time audio visualization techniques
- Animation timing and smooth movement
- Multi-display coordination and design
- User interface feedback principles

**Professional Applications:**
- Parameter monitoring and feedback
- Audio signal analysis and display
- Plugin status and mode indication
- Interactive visual performance elements

---

## Step 10: Advanced LED Projects

### 10.1 Spectrum Analyzer Display
**Show frequency content across multiple displays:**

```impala



```

### 10.2 Pattern Sequencer Visualization
**Show step sequencer patterns:**

```impala



```

### 10.3 Ready for Advanced Visualization
**Build on your LED skills:**
- 📖 [Control Something with Knobs](control-something-with-knobs.md) - Combine knob control with LED feedback
- 📖 [Simple Delay Explained](simple-delay-explained.md) - Add LED visualization to time-based effects
- 📖 [Level Meters](../cookbook/visual-feedback/level-meters.md) - Professional audio metering
- 📖 [Parameter Display](../cookbook/visual-feedback/parameter-display.md) - Advanced parameter visualization

### 10.4 Creative LED Applications
**Your LED foundation enables:**
- Real-time audio spectrum analysis
- Multi-parameter macro control visualization
- Step sequencer and rhythm pattern display
- Performance-oriented visual feedback
- Complex multi-dimensional parameter spaces

**🎉 You're now a visual feedback designer!** Your plugins can communicate clearly with users through beautiful, informative LED displays. This visual connection makes your plugins more intuitive and engaging to use.