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
global array displayLEDs[4]  // 4 separate LED displays

// displayLEDs[0] = First LED display (8 LEDs)
// displayLEDs[1] = Second LED display (8 LEDs)  
// displayLEDs[2] = Third LED display (8 LEDs)
// displayLEDs[3] = Fourth LED display (8 LEDs)
```

### 1.2 How LED Values Work
**Each display is controlled by a single number (0-255)**:
```impala
displayLEDs[0] = 0x00  // All LEDs off (binary: 00000000)
displayLEDs[0] = 0x01  // Only first LED on (binary: 00000001)
displayLEDs[0] = 0xFF  // All LEDs on (binary: 11111111)
displayLEDs[0] = 0x0F  // First 4 LEDs on (binary: 00001111)
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
// LED Test - Light Up Different Patterns
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {
        // Test different LED patterns
        displayLEDs[0] = 0x01  // First LED only
        displayLEDs[1] = 0x03  // First 2 LEDs
        displayLEDs[2] = 0x0F  // First 4 LEDs  
        displayLEDs[3] = 0xFF  // All 8 LEDs
        
        // Pass audio through unchanged
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
// Basic patterns
displayLEDs[0] = 0x00  // All off
displayLEDs[0] = 0x01  // Single LED (position 1)
displayLEDs[0] = 0x80  // Single LED (position 8)
displayLEDs[0] = 0xFF  // All on

// Bar graphs (show levels)
displayLEDs[0] = 0x01  // 1 LED  (12.5% level)
displayLEDs[0] = 0x03  // 2 LEDs (25% level)
displayLEDs[0] = 0x07  // 3 LEDs (37.5% level)
displayLEDs[0] = 0x0F  // 4 LEDs (50% level)
displayLEDs[0] = 0x1F  // 5 LEDs (62.5% level)
displayLEDs[0] = 0x3F  // 6 LEDs (75% level)
displayLEDs[0] = 0x7F  // 7 LEDs (87.5% level)
displayLEDs[0] = 0xFF  // 8 LEDs (100% level)

// Special patterns
displayLEDs[0] = 0xAA  // Alternating (10101010)
displayLEDs[0] = 0x55  // Alternating (01010101)
displayLEDs[0] = 0x18  // Center 2 LEDs (00011000)
displayLEDs[0] = 0x81  // Ends only (10000001)
```

### 3.2 Pattern Test Plugin
Test all the common patterns:

```impala
function process()
{
    loop {
        // Cycle through different patterns every few seconds
        static int counter = 0
        counter = (counter + 1) % 44100  // Change every second at 44.1kHz
        
        int pattern = counter / 5512  // 8 different patterns (44100/8 ≈ 5512)
        
        if (pattern == 0) displayLEDs[0] = 0x01      // Single LED
        else if (pattern == 1) displayLEDs[0] = 0x03 // 2 LEDs
        else if (pattern == 2) displayLEDs[0] = 0x07 // 3 LEDs
        else if (pattern == 3) displayLEDs[0] = 0x0F // 4 LEDs
        else if (pattern == 4) displayLEDs[0] = 0x1F // 5 LEDs
        else if (pattern == 5) displayLEDs[0] = 0x3F // 6 LEDs
        else if (pattern == 6) displayLEDs[0] = 0x7F // 7 LEDs
        else displayLEDs[0] = 0xFF                   // All LEDs
        
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
// Parameter LED Display
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {
        // Read knob values
        int knob1 = params[3]  // 0-255
        int knob2 = params[4]  // 0-255
        
        // Convert to LED bar graphs
        int leds1 = 0
        if (knob1 > 224) leds1 = 0xFF      // 8 LEDs (87.5%+)
        else if (knob1 > 192) leds1 = 0x7F // 7 LEDs (75%+)
        else if (knob1 > 160) leds1 = 0x3F // 6 LEDs (62.5%+)
        else if (knob1 > 128) leds1 = 0x1F // 5 LEDs (50%+)
        else if (knob1 > 96) leds1 = 0x0F  // 4 LEDs (37.5%+)
        else if (knob1 > 64) leds1 = 0x07  // 3 LEDs (25%+)
        else if (knob1 > 32) leds1 = 0x03  // 2 LEDs (12.5%+)
        else if (knob1 > 0) leds1 = 0x01   // 1 LED (0%+)
        else leds1 = 0x00                  // No LEDs
        
        // Same for knob 2
        int leds2 = 0
        if (knob2 > 224) leds2 = 0xFF
        else if (knob2 > 192) leds2 = 0x7F
        else if (knob2 > 160) leds2 = 0x3F
        else if (knob2 > 128) leds2 = 0x1F
        else if (knob2 > 96) leds2 = 0x0F
        else if (knob2 > 64) leds2 = 0x07
        else if (knob2 > 32) leds2 = 0x03
        else if (knob2 > 0) leds2 = 0x01
        else leds2 = 0x00
        
        // Display on LEDs
        displayLEDs[0] = leds1  // Knob 1 level
        displayLEDs[1] = leds2  // Knob 2 level
        
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
        // Get audio levels (absolute values)
        int leftLevel = signal[0]
        if (leftLevel < 0) leftLevel = -leftLevel    // Make positive
        
        int rightLevel = signal[1]
        if (rightLevel < 0) rightLevel = -rightLevel // Make positive
        
        // Convert audio levels to LED patterns
        int leftLEDs = 0
        if (leftLevel > 1800) leftLEDs = 0xFF        // Very loud
        else if (leftLevel > 1500) leftLEDs = 0x7F  // Loud
        else if (leftLevel > 1200) leftLEDs = 0x3F  // Medium-loud
        else if (leftLevel > 900) leftLEDs = 0x1F   // Medium
        else if (leftLevel > 600) leftLEDs = 0x0F   // Medium-quiet
        else if (leftLevel > 300) leftLEDs = 0x07   // Quiet
        else if (leftLevel > 100) leftLEDs = 0x03   // Very quiet
        else if (leftLevel > 10) leftLEDs = 0x01    // Barely audible
        else leftLEDs = 0x00                        // Silent
        
        // Same calculation for right channel
        int rightLEDs = 0
        if (rightLevel > 1800) rightLEDs = 0xFF
        else if (rightLevel > 1500) rightLEDs = 0x7F
        else if (rightLevel > 1200) rightLEDs = 0x3F
        else if (rightLevel > 900) rightLEDs = 0x1F
        else if (rightLevel > 600) rightLEDs = 0x0F
        else if (rightLevel > 300) rightLEDs = 0x07
        else if (rightLevel > 100) rightLEDs = 0x03
        else if (rightLevel > 10) rightLEDs = 0x01
        else rightLEDs = 0x00
        
        // Display audio levels
        displayLEDs[0] = leftLEDs   // Left channel meter
        displayLEDs[1] = rightLEDs  // Right channel meter
        
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
        // Create moving dot
        static int position = 0
        static int counter = 0
        
        counter = (counter + 1) % 2205  // Update every 1/20 second
        if (counter == 0) {
            position = (position + 1) % 8  // Move to next LED position
        }
        
        // Convert position to LED pattern
        int movingDot = 1 << position  // Bit shift to create single LED
        displayLEDs[0] = movingDot
        
        // Create reverse direction on second display
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
        static int direction = 1  // 1 = right, -1 = left
        static int counter = 0
        
        counter = (counter + 1) % 1102  // Update every 1/40 second
        if (counter == 0) {
            position = position + direction
            
            // Bounce at ends
            if (position >= 7) {
                position = 7
                direction = -1
            } else if (position <= 0) {
                position = 0
                direction = 1
            }
        }
        
        // Create scanning pattern with trail
        int pattern = (1 << position)           // Main dot
        if (position > 0) pattern |= (1 << (position - 1)) / 2  // Dim trail
        if (position < 7) pattern |= (1 << (position + 1)) / 2  // Dim trail
        
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
// Convert 0-255 value to bar graph LED pattern
function valueToBarGraph(int value)
returns int ledPattern
{
    if (value > 224) ledPattern = 0xFF
    else if (value > 192) ledPattern = 0x7F
    else if (value > 160) ledPattern = 0x3F
    else if (value > 128) ledPattern = 0x1F
    else if (value > 96) ledPattern = 0x0F
    else if (value > 64) ledPattern = 0x07
    else if (value > 32) ledPattern = 0x03
    else if (value > 0) ledPattern = 0x01
    else ledPattern = 0x00
}

// Convert 0-7 position to single LED
function positionToLED(int position)
returns int ledPattern
{
    if (position >= 8) position = 7  // Clamp to valid range
    if (position < 0) position = 0
    ledPattern = 1 << position
}

// Create blinking pattern
function blinkingPattern(int basePattern, int speed)
returns int ledPattern
{
    static int blinkCounter = 0
    blinkCounter = (blinkCounter + 1) % speed
    
    if (blinkCounter < (speed / 2)) {
        ledPattern = basePattern      // On phase
    } else {
        ledPattern = 0x00            // Off phase
    }
}
```

### 7.2 Complete LED Showcase
**Comprehensive LED control example:**

```impala
// Complete LED Showcase - All Techniques
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2

global array signal[2]
global array params[8]
global array displayLEDs[4]

function process()
{
    loop {
        // Display 1: Knob 1 value as bar graph
        int knob1Value = params[3]
        displayLEDs[0] = valueToBarGraph(knob1Value)
        
        // Display 2: Audio level meter for left channel
        int leftLevel = signal[0]
        if (leftLevel < 0) leftLevel = -leftLevel
        int scaledLevel = (leftLevel * 255) / 2047  // Scale to 0-255
        displayLEDs[1] = valueToBarGraph(scaledLevel)
        
        // Display 3: Moving dot based on knob 2 speed
        static int dotPosition = 0
        static int dotCounter = 0
        int speed = 100 + ((params[4] * 2000) / 255)  // Speed control from knob 2
        
        dotCounter = (dotCounter + 1) % speed
        if (dotCounter == 0) {
            dotPosition = (dotPosition + 1) % 8
        }
        displayLEDs[2] = positionToLED(dotPosition)
        
        // Display 4: Activity indicator (blinking when audio present)
        int activity = (scaledLevel > 10) ? 0xFF : 0x01
        displayLEDs[3] = blinkingPattern(activity, 2205)  // Blink every 1/20 second
        
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
// Pattern library - copy these into your plugins
const int LED_OFF = 0x00
const int LED_ALL = 0xFF
const int LED_FIRST = 0x01
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
// Frequency band monitoring across 4 LED displays
// Display different frequency ranges on each LED bank
// Requires frequency analysis (advanced topic)
```

### 10.2 Pattern Sequencer Visualization
**Show step sequencer patterns:**

```impala
// Light up LEDs to show which step is currently playing
// Show pattern editing with blinking LEDs
// Display multiple sequence layers
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