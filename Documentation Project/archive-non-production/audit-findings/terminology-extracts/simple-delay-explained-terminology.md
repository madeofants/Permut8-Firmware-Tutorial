# TERMINOLOGY EXTRACT: simple-delay-explained.md

**Source File**: `/content/user-guides/tutorials/simple-delay-explained.md`  
**Extraction Date**: January 10, 2025  
**Category**: Tutorial Foundation - Time-based effects  
**Terms Extracted**: 25+ technical terms

---

## 📚 CORE DELAY CONCEPTS

### **Circular buffer**
Fixed-size array with wraparound indexing for continuous data storage without memory allocation

### **Delay time**  
Duration between input and output of processed audio signal, measured in samples or seconds

### **Feedback**
Portion of delayed output fed back into input for multiple echoes and sustained effects

### **Dry signal**
Original, unprocessed audio input without any effect processing applied

### **Wet signal**
Processed audio output from delay effect, containing the delayed/echoed audio

### **Buffer position**
Current write index in circular buffer array, advanced each sample

---

## 🔧 TECHNICAL IMPLEMENTATION

### **Modulo arithmetic**
Mathematical operation (%) for circular buffer wraparound, ensuring array bounds safety

### **Parameter mapping**
Converting 0-255 knob values to musically useful ranges through mathematical scaling

### **Audio mixing**
Mathematical combination of multiple audio signals using addition and scaling

### **Clipping protection**
Limiting audio values to prevent overflow beyond ±2047 range using conditional statements

### **Sample**
Single audio data point representing amplitude at one moment in time

### **Read position**
Buffer index for retrieving delayed audio samples, calculated relative to write position

### **Write position**
Buffer index for storing new audio samples, advanced circularly each sample

### **Buffer wraparound**
Technique for circular array indexing without bounds checking using modulo operation

---

## 🎵 AUDIO PROCESSING PATTERNS

### **Feedback limiting**
Preventing runaway amplification in feedback systems through gain reduction and clipping

### **Mix control**
Parameter balancing original and processed audio signals using complementary scaling

### **Delay samples**
Number of samples between input and output, determining delay time duration

### **Activity threshold**
Audio level above which delay activity is considered significant for visual feedback

### **Safety feedback range**
Limited feedback values (typically 0-200/255) to prevent unstable oscillation

### **Buffer size**
Fixed array length determining maximum delay time and memory usage

---

## 🎛️ PARAMETER CONCEPTS

### **Delay time parameter**
Hardware knob input (0-255) controlling duration of delay effect

### **Feedback parameter**  
Hardware knob input (0-255) controlling amount of delayed signal fed back

### **Mix parameter**
Hardware knob input (0-255) controlling balance between dry and wet signals

### **Parameter scaling**
Mathematical conversion from hardware range (0-255) to effect-specific ranges

### **Linear mapping**
Direct proportional scaling of parameter values to effect ranges

---

## 💡 PERFORMANCE CONCEPTS

### **Memory efficiency**
Fixed buffer allocation using global arrays for predictable memory usage

### **Real-time processing**
Sample-by-sample processing with yield() calls for audio engine integration

### **Computational complexity**
Number of operations per sample, affecting CPU usage and efficiency

### **Buffer memory usage**
RAM consumption based on buffer size and data type (int = 4 bytes per sample)

---

**TOTAL TERMS EXTRACTED**: 25+ comprehensive delay and audio processing terms  
**USAGE CONTEXT**: Foundation for all time-based audio effects development  
**INTEGRATION**: Essential vocabulary for advanced audio processing tutorials