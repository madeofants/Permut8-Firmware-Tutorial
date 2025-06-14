# TERMINOLOGY EXTRACT: build-your-first-filter.md

**Source File**: `/content/user-guides/tutorials/build-your-first-filter.md`  
**Extraction Date**: January 10, 2025  
**Terms Identified**: 18+ core terms  
**Category**: Tutorial Foundation - Audio Processing

---

## 📚 EXTRACTED TERMINOLOGY

### **FILTER CONCEPTS** (6 terms)

#### **Low-pass filter**
- **Definition**: Frequency filter removing high frequencies above cutoff point
- **Context**: Primary audio processing effect for frequency shaping
- **Usage Example**: "A simple low-pass filter works like this: output = (input * mix) + (lastOutput * (1 - mix))"
- **Related Terms**: cutoff frequency, frequency response, filtering

#### **Cutoff frequency**
- **Definition**: Frequency threshold where filter operation begins
- **Context**: Primary parameter controlling filter behavior
- **Usage Example**: "Get cutoff frequency from first knob (0-255)"
- **Related Terms**: low-pass filter, frequency response, filter parameter

#### **Resonance**
- **Definition**: Feedback mechanism creating peak at cutoff frequency
- **Context**: Secondary filter parameter adding harmonic emphasis
- **Usage Example**: "Resonance adds a peak at the cutoff frequency by feeding some output back to the input"
- **Related Terms**: feedback loop, filter peak, self-oscillation

#### **Filter coefficient**
- **Definition**: Mathematical parameter controlling filter behavior
- **Context**: Internal calculation converting user parameters to filter math
- **Usage Example**: "int filterMix = (cutoffParam * 200) / 255"
- **Related Terms**: parameter scaling, filter math, DSP coefficients

#### **IIR filter**
- **Definition**: Infinite Impulse Response filter using feedback from output
- **Context**: Filter type that uses previous output in current calculation
- **Usage Example**: "output = (input * mix) + (lastOutput * (1-mix))"
- **Related Terms**: filter state, feedback, recursive filter

#### **Frequency response**
- **Definition**: Filter behavior across different frequency ranges
- **Context**: Characteristic curve showing filter effect on audio spectrum
- **Usage Example**: "Lower knob values keep more of the previous output, which smooths out fast changes (high frequencies)"
- **Related Terms**: low-pass filter, cutoff frequency, audio spectrum

### **DSP MATHEMATICS** (5 terms)

#### **Filter mix**
- **Definition**: Ratio parameter controlling input vs feedback blend
- **Context**: Core mathematical parameter in filter equation
- **Usage Example**: "int filterMix = (cutoffParam * 200) / 255"
- **Related Terms**: filter coefficient, blend ratio, DSP math

#### **Feedback loop**
- **Definition**: Circuit pattern feeding output back to input for processing
- **Context**: Fundamental DSP technique for creating resonance effects
- **Usage Example**: "int input = signal[0] + ((lastOutput * resonance) / 255)"
- **Related Terms**: resonance, IIR filter, recursive processing

#### **Clipping protection**
- **Definition**: Overflow prevention limiting audio values to ±2047 range
- **Context**: Essential safety technique preventing audio distortion
- **Usage Example**: "if (input > 2047) input = 2047"
- **Related Terms**: audio range, overflow prevention, audio safety

#### **Filter state**
- **Definition**: Memory variables maintaining filter history between samples
- **Context**: Persistent data storage for recursive filter calculations
- **Usage Example**: "global int lastOutput = 0 // Remember last output sample"
- **Related Terms**: IIR filter, filter memory, state variables

#### **Parameter scaling**
- **Definition**: Converting 0-255 knob values to usable filter ranges
- **Context**: Interface between hardware controls and DSP mathematics
- **Usage Example**: "int filterMix = (cutoffParam * 200) / 255"
- **Related Terms**: knob control, range conversion, hardware interface

### **IMPLEMENTATION PATTERNS** (4 terms)

#### **Stereo processing**
- **Definition**: Independent left/right channel handling for true stereo effects
- **Context**: Professional audio technique maintaining channel separation
- **Usage Example**: "global int lastOutput = 0 // Left channel filter memory; global int lastOutputR = 0 // Right channel filter memory"
- **Related Terms**: channel separation, stereo audio, professional processing

#### **LED patterns**
- **Definition**: Bit manipulation for visual feedback display
- **Context**: User interface technique showing filter state visually
- **Usage Example**: "if (filterAmount > 200) ledPattern = 0xFF // All 8 LEDs"
- **Related Terms**: visual feedback, bit patterns, user interface

#### **Audio stability**
- **Definition**: Techniques preventing runaway feedback and oscillation
- **Context**: Essential practices for stable real-time audio processing
- **Usage Example**: "int resonance = (resonanceParam * 150) / 255 // Limit for stability"
- **Related Terms**: clipping protection, feedback control, stable processing

#### **Real-time processing**
- **Definition**: Sample-by-sample audio processing with yield() pattern
- **Context**: Fundamental approach for live audio effect processing
- **Usage Example**: "loop { // Process one sample; yield(); }"
- **Related Terms**: yield(), sample processing, real-time audio

### **AUDIO ENGINEERING CONCEPTS** (3 terms)

#### **Self-oscillation**
- **Definition**: Filter behavior where high resonance creates audible tone
- **Context**: Advanced filter technique where filter generates its own sound
- **Usage Example**: "Extreme resonance = self-oscillation (makes its own tone!)"
- **Related Terms**: resonance, feedback loop, oscillation

#### **Filter sweep**
- **Definition**: Dynamic change of cutoff frequency over time
- **Context**: Musical technique for expressive filter effects
- **Usage Example**: "Turn the knob - you should hear the high frequencies being filtered!"
- **Related Terms**: cutoff frequency, dynamic filtering, musical expression

#### **Harmonic content**
- **Definition**: Frequency components that make up complex audio signals
- **Context**: What filters modify to change sound character
- **Usage Example**: "Low-pass filter removes high frequencies (harmonics)"
- **Related Terms**: frequency spectrum, audio timbre, frequency response

---

## 🔍 TERMINOLOGY ANALYSIS

### **FREQUENCY ANALYSIS**
- **High Frequency**: filter (35x), frequency (12x), output (25x)
- **Medium Frequency**: resonance (8x), input (15x), cutoff (10x)
- **Technical Depth**: Comprehensive DSP coverage with practical application

### **CONCEPT RELATIONSHIPS**
```
Audio Filter Foundation
├── Core Filter Concepts
│   ├── Low-pass filter (frequency removal)
│   ├── Cutoff frequency (threshold parameter)
│   ├── Resonance (feedback peak)
│   └── Frequency response (filter characteristic)
├── DSP Mathematics
│   ├── Filter coefficient (mix parameter)
│   ├── Feedback loop (output-to-input)
│   ├── Filter state (memory variables)
│   └── Parameter scaling (control mapping)
├── Implementation Techniques
│   ├── Clipping protection (audio safety)
│   ├── Stereo processing (channel separation)
│   ├── Real-time processing (sample-by-sample)
│   └── Visual feedback (LED patterns)
└── Musical Application
    ├── Filter sweep (dynamic cutoff)
    ├── Self-oscillation (resonance effects)
    └── Harmonic shaping (timbre control)
```

### **LEARNING PROGRESSION**
- **Foundation**: Basic filter theory and mathematics
- **Implementation**: Step-by-step filter building
- **Enhancement**: Resonance and advanced features
- **Professional**: Stereo processing and stability
- **Musical**: Creative application and expression

---

## 📊 GLOSSARY CONTRIBUTION

**Total Terms for Master Glossary**: 18+  
**Filter Concepts**: 6  
**DSP Mathematics**: 5  
**Implementation Patterns**: 4  
**Audio Engineering**: 3  

**Quality Assessment**: **Excellent** - Comprehensive filter foundation with practical DSP application

**Educational Value**: **High** - Essential terminology for all audio processing development

**Professional Relevance**: **Maximum** - Industry-standard filter concepts and techniques

---

## 🎯 DSP TERMINOLOGY SIGNIFICANCE

### **Foundation for Advanced Audio Processing**:
- **Multi-band Filters**: Multiple filter concepts combined
- **Modulation Effects**: Filter sweeps and dynamic control
- **Synthesis**: Filter integration with oscillators
- **Complex Effects**: Filter chains and parallel processing

### **Professional Audio Development**:
- **Stereo Processing**: Industry-standard channel handling
- **Stability Techniques**: Professional audio safety practices
- **Parameter Control**: User interface design principles
- **Real-time Constraints**: Performance optimization concepts

---

**EXTRACTION COMPLETED**: January 10, 2025  
**NEXT FILE**: getting-audio-in-and-out.md  
**GLOSSARY STATUS**: Audio processing foundation established