# TERMINOLOGY EXTRACT: make-your-first-sound.md

**Source File**: `/content/user-guides/tutorials/make-your-first-sound.md`  
**Extraction Date**: January 10, 2025  
**Terms Identified**: 20+ core terms  
**Category**: Tutorial Foundation - Audio Generation

---

## 📚 EXTRACTED TERMINOLOGY

### **AUDIO GENERATION CONCEPTS** (6 terms)

#### **Digital oscillator**
- **Definition**: Software-based sound generator using mathematical waveforms
- **Context**: Core concept for creating audio from scratch
- **Usage Example**: "Repeatedly output numbers that, when played fast enough, create sound waves"
- **Related Terms**: waveform generation, synthesis, phase accumulator

#### **Phase accumulator**
- **Definition**: Counter (0-65535) representing position in waveform cycle
- **Context**: Fundamental mechanism for tracking oscillator state
- **Usage Example**: "global int phase = 0 // Current position in the waveform"
- **Related Terms**: frequency, phase increment, waveform cycle

#### **Sound generation**
- **Definition**: Creating audio from scratch vs processing existing audio
- **Context**: Distinguishes synthesis from effects processing
- **Usage Example**: "signal[0] = myGeneratedSound // Create audio from scratch"
- **Related Terms**: audio processing, synthesis, digital oscillator

#### **Waveform generation**
- **Definition**: Mathematical process of creating repeating audio patterns
- **Context**: Core synthesis technique for creating different timbres
- **Usage Example**: "Generate triangle wave oscillator"
- **Related Terms**: triangle wave, square wave, sine wave, amplitude

#### **Phase increment**
- **Definition**: Amount added to phase each sample (controls frequency)
- **Context**: Mechanism for controlling oscillator pitch
- **Usage Example**: "phase = (phase + frequency) % 65536"
- **Related Terms**: frequency control, phase accumulator, pitch

#### **Real-time synthesis**
- **Definition**: Continuous audio generation using yield() pattern
- **Context**: Live audio generation in processing loop
- **Usage Example**: "Generate waveform in loop with yield()"
- **Related Terms**: yield(), real-time processing, audio generation

### **WAVEFORM TYPES** (4 terms)

#### **Triangle wave**
- **Definition**: Linear waveform creating smooth, warm sound character
- **Context**: Example waveform type with simple mathematical generation
- **Usage Example**: "if (phase < 32768) amplitude = phase - 16384"
- **Related Terms**: waveform, amplitude, harmonic content

#### **Square wave**
- **Definition**: Binary waveform creating harsh, buzzy sound character
- **Context**: Alternative waveform with different timbral characteristics
- **Usage Example**: "High for first half, low for second half"
- **Related Terms**: waveform, harmonic content, digital synthesis

#### **Sawtooth wave**
- **Definition**: Linear ramp waveform creating bright, buzzy sound
- **Context**: Common synthesis waveform with rich harmonic content
- **Usage Example**: "amplitude = (phase / 2) - 16384 // Linear ramp"
- **Related Terms**: waveform, harmonic content, brightness

#### **Sine wave**
- **Definition**: Smooth curved waveform creating pure, flute-like tone
- **Context**: Mathematical waveform with only fundamental frequency
- **Usage Example**: "Pure tone (like a flute)"
- **Related Terms**: waveform, harmonic content, pure tone

### **MUSICAL CONCEPTS** (5 terms)

#### **Musical frequencies**
- **Definition**: Specific frequency values corresponding to musical notes
- **Context**: Translation between mathematical frequencies and musical pitches
- **Usage Example**: "if (note == 9) frequency = 165 // A (reference pitch)"
- **Related Terms**: chromatic scale, pitch, frequency

#### **Chromatic scale**
- **Definition**: 12-note musical system (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
- **Context**: Complete set of musical notes within an octave
- **Usage Example**: "Try values 0-11 for different notes"
- **Related Terms**: musical notes, octave, pitch

#### **Octave**
- **Definition**: Frequency doubling relationship in musical intervals
- **Context**: Musical interval representing frequency multiplication by 2
- **Usage Example**: "int frequency2 = frequency * 2 // Octave higher"
- **Related Terms**: musical intervals, frequency relationships

#### **Frequency**
- **Definition**: Rate of phase increment determining musical pitch
- **Context**: Mathematical control parameter for oscillator pitch
- **Usage Example**: "frequency = 200 // Medium-low pitch"
- **Related Terms**: pitch, phase increment, musical frequencies

#### **Amplitude**
- **Definition**: Wave height/volume level in digital representation
- **Context**: Mathematical representation of audio loudness
- **Usage Example**: "int amplitude = phase - 16384"
- **Related Terms**: volume, waveform, audio level

### **PROGRAMMING PATTERNS** (5 terms)

#### **Modulo operation**
- **Definition**: Mathematical wrapping to keep phase within 0-65535 range
- **Context**: Essential technique for phase accumulator overflow handling
- **Usage Example**: "phase = (phase + frequency) % 65536"
- **Related Terms**: phase accumulator, overflow handling, wraparound

#### **State variables**
- **Definition**: Global variables maintaining oscillator state between calls
- **Context**: Persistent data storage for continuous audio generation
- **Usage Example**: "global int phase = 0 // Oscillator state"
- **Related Terms**: global variables, persistence, oscillator state

#### **Volume scaling**
- **Definition**: Mathematical amplitude control for safe audio levels
- **Context**: Technique for controlling output level and preventing damage
- **Usage Example**: "int output = (amplitude * volume) / 8000"
- **Related Terms**: amplitude, audio safety, level control

#### **LED visualization**
- **Definition**: Visual feedback showing oscillator state and parameters
- **Context**: User interface technique for displaying audio parameters
- **Usage Example**: "displayLEDs[2] = (phase / 8192) // Show phase"
- **Related Terms**: displayLEDs, visual feedback, user interface

#### **Frequency control**
- **Definition**: Parameter adjustment mechanism for changing oscillator pitch
- **Context**: User control over musical pitch and frequency relationships
- **Usage Example**: "frequency = 200 // Try different values"
- **Related Terms**: pitch control, musical frequencies, parameter control

---

## 🔍 TERMINOLOGY ANALYSIS

### **FREQUENCY ANALYSIS**
- **High Frequency**: frequency (25x), phase (18x), amplitude (15x)
- **Medium Frequency**: wave (12x), oscillator (10x), sound (8x)
- **Technical Depth**: Balanced synthesis theory with practical application

### **CONCEPT RELATIONSHIPS**
```
Audio Generation Foundation
├── Core Concepts
│   ├── Digital oscillator (sound generation engine)
│   ├── Phase accumulator (position tracking)
│   ├── Frequency control (pitch determination)
│   └── Amplitude control (volume management)
├── Waveform Types
│   ├── Triangle wave (smooth, warm)
│   ├── Square wave (harsh, buzzy)
│   ├── Sawtooth wave (bright, rich)
│   └── Sine wave (pure, smooth)
├── Musical Application
│   ├── Musical frequencies (note-to-frequency mapping)
│   ├── Chromatic scale (12-note system)
│   ├── Octave relationships (frequency doubling)
│   └── Pitch control (musical expression)
└── Implementation Patterns
    ├── Phase increment (frequency control)
    ├── Modulo operation (overflow handling)
    ├── Volume scaling (safe audio levels)
    └── State persistence (continuous generation)
```

### **LEARNING PROGRESSION**
- **Foundation**: Sound generation vs processing concepts
- **Mathematics**: Phase accumulation and waveform generation
- **Application**: Musical frequencies and note generation
- **Control**: Volume and frequency parameter management
- **Extension**: Multiple waveforms and advanced synthesis

---

## 📊 GLOSSARY CONTRIBUTION

**Total Terms for Master Glossary**: 20+  
**Audio Generation Terms**: 6  
**Waveform Types**: 4  
**Musical Concepts**: 5  
**Programming Patterns**: 5  

**Quality Assessment**: **Excellent** - Clear synthesis foundation with practical musical application

**Educational Value**: **High** - Essential terminology for all subsequent synthesis learning

**Practical Application**: **Maximum** - All terms directly applicable to sound generation projects

---

## 🎯 SYNTHESIS TERMINOLOGY SIGNIFICANCE

### **Foundation for Advanced Topics**:
- **FM Synthesis**: Phase accumulator and frequency control concepts
- **Subtractive Synthesis**: Waveform generation and filtering foundation
- **Additive Synthesis**: Amplitude and harmonic content understanding
- **Modular Synthesis**: State variables and parameter control patterns

### **Musical Integration**:
- **Chromatic scale**: Complete musical note system
- **Frequency relationships**: Mathematical basis for musical intervals
- **Amplitude control**: Dynamic expression and musical phrasing
- **Real-time control**: Live performance and interaction concepts

---

**EXTRACTION COMPLETED**: January 10, 2025  
**NEXT FILE**: build-your-first-filter.md  
**GLOSSARY STATUS**: Audio generation foundation established