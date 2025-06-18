# How to Use This Documentation

*Your complete guide to mastering Permut8 firmware development*

## What This Documentation Contains

This documentation is your comprehensive resource for developing custom firmware for the Permut8 device. It contains over 100 guides, tutorials, and reference materials organized to take you from complete beginner to advanced developer. Whether you want to create simple effects or complex audio processors, everything you need is here.

The documentation is designed for **offline use** - once you have it, you can develop anywhere without internet access.

## Section Guide

### 🎯 Start Here
**Purpose:** Essential first steps and orientation  
**When to use:** Always read this first - contains the 30-minute QUICKSTART and this navigation guide  
**What you'll learn:** Basic workflow, essential concepts, and how to navigate the rest of the documentation  

### 📖 Language Reference
**Purpose:** Complete Impala language documentation  
**When to use:** When you need to understand syntax, functions, or language rules  
**What you'll learn:** Core language syntax, data types, operators, built-in functions, and standard library  
**Prerequisites:** None, but QUICKSTART recommended first  

### 🎓 Tutorials  
**Purpose:** Step-by-step guided learning experiences  
**When to use:** When you want structured learning with clear outcomes  
**What you'll learn:** How to build specific projects from start to finish  
**Prerequisites:** QUICKSTART and basic language understanding  

### 🍳 Cookbook - Fundamentals
**Purpose:** Essential building blocks for all firmware development  
**When to use:** When learning core concepts or implementing basic functionality  
**What you'll learn:** Oscillators, filters, envelopes, parameter control, basic math operations  
**Prerequisites:** Language basics and first tutorial completion  

### 🎵 Cookbook - Audio Effects
**Purpose:** Popular audio processing recipes  
**When to use:** When you want to implement specific effects like delay, distortion, chorus  
**What you'll learn:** Complete implementations of classic audio effects  
**Prerequisites:** Fundamentals knowledge and parameter control understanding  

### ⏱️ Cookbook - Timing & Utilities
**Purpose:** Timing controls, utility functions, and visual feedback  
**When to use:** When building rhythmic effects or need helper functions  
**What you'll learn:** Tempo sync, clock division, signal mixing, LED control  
**Prerequisites:** Basic effects experience  

### 🌊 Cookbook - Advanced
**Purpose:** Complex techniques and experimental approaches  
**When to use:** When you're comfortable with basics and want to push boundaries  
**What you'll learn:** Spectral processing, granular synthesis, advanced patterns  
**Prerequisites:** Solid foundation in fundamentals and several completed effects  

### 📚 Reference Docs
**Purpose:** Complete API and parameter documentation  
**When to use:** When you need exact function signatures or parameter ranges  
**What you'll learn:** Every available function, parameter, and system capability  
**Prerequisites:** Basic language knowledge for context  

### 🏗️ Architecture
**Purpose:** System design and memory management  
**When to use:** When building complex firmware or optimizing performance  
**What you'll learn:** Memory models, processing order, state management, system architecture  
**Prerequisites:** Several completed projects and performance awareness  

### ⚡ Performance
**Purpose:** Optimization techniques and best practices  
**When to use:** When your firmware is too slow or uses too much memory  
**What you'll learn:** Efficient algorithms, memory optimization, mathematical techniques  
**Prerequisites:** Working firmware that needs optimization  

### 🔗 Integration
**Purpose:** Host integration and MIDI functionality  
**When to use:** When building production-ready firmware for real-world use  
**What you'll learn:** Preset systems, MIDI learning, host automation, state recall  
**Prerequisites:** Completed effects and understanding of plugin hosts  

### ⚙️ Assembly
**Purpose:** Low-level GAZL programming  
**When to use:** When you need maximum performance or system-level control  
**What you'll learn:** Assembly language programming, debugging, optimization  
**Prerequisites:** Strong Impala foundation and performance knowledge  

### 🔬 Advanced Topics
**Purpose:** Specialized and experimental techniques  
**When to use:** When standard approaches don't meet your needs  
**What you'll learn:** Custom build tools, metaprogramming, advanced debugging  
**Prerequisites:** Solid experience across multiple areas  

---

## Learning Paths

### Path 1: Complete Beginner → Basic Understanding
*From zero knowledge to your first working effect*  
**Total Time Investment: 3-4 hours**

#### Stage 1: Foundation (60 minutes)
1. **Read QUICKSTART** (30 minutes)
   - Location: 🎯 Start Here → QUICKSTART
   - Outcome: Understanding of basic workflow and first successful compilation
   - Checkpoint: You can compile and load the example delay effect

2. **Core Language Basics** (30 minutes)
   - Location: 📖 Language Reference → Core Language Reference
   - Focus: Variables, functions, basic syntax, the `process()` function
   - Outcome: Understanding how Impala code is structured
   - Checkpoint: You can read and understand basic code examples

#### Stage 2: First Real Project (90 minutes)
3. **Build Your First Filter** (45 minutes)
   - Location: 🎓 Tutorials → Build Your First Filter  
   - Outcome: Complete working filter from scratch
   - Checkpoint: You have a functioning low-pass filter

4. **Understanding Parameters** (30 minutes)
   - Location: 🍳 Fundamentals → Parameter Mapping
   - Outcome: Know how to connect knobs to your code
   - Checkpoint: Your filter responds to Control 1

5. **Basic Audio Processing** (15 minutes)
   - Location: 🍳 Fundamentals → Gain and Volume
   - Outcome: Understand audio signal flow
   - Checkpoint: You can control output volume

#### Stage 3: Practical Skills (60 minutes)
6. **Simple Effect Creation** (30 minutes)
   - Location: 🍳 Fundamentals → Simplest Distortion
   - Outcome: Build a basic distortion effect
   - Checkpoint: Working distortion with parameter control

7. **Testing and Debugging** (30 minutes)
   - Location: 🎓 Tutorials → Test Your Plugin
   - Outcome: Know how to verify your effects work correctly
   - Checkpoint: Confidence in testing your own code

**Path 1 Completion Goal:** You can create simple audio effects, control them with knobs, and test that they work properly.

---

### Path 2: Basic Understanding → Practical Hobbyist
*From simple effects to creating the sounds you imagine*  
**Total Time Investment: 8-12 hours**

#### Stage 4: Effect Building Skills (3-4 hours)
8. **Essential Effects Toolkit** (2-3 hours)
   - **Delay Effect** (45 minutes)
     - Location: 🎵 Audio Effects → Make a Delay
     - Outcome: Understanding of memory and feedback
   - **Bitcrusher** (30 minutes)  
     - Location: 🎵 Audio Effects → Bitcrusher
     - Outcome: Digital distortion techniques
   - **Chorus Effect** (45 minutes)
     - Location: 🎵 Audio Effects → Chorus Effect  
     - Outcome: Modulation and multiple delay lines
   - **Basic Filter Types** (30 minutes)
     - Location: 🍳 Fundamentals → Basic Filter
     - Outcome: High-pass, band-pass, and resonance control
   - Checkpoint: You have 4-5 working effects you built yourself

9. **Advanced Parameter Control** (60 minutes)
   - **Envelope Basics** (30 minutes)
     - Location: 🍳 Fundamentals → Envelope Basics
     - Outcome: Attack, decay, sustain, release control
   - **Parameter Smoothing** (30 minutes)
     - Location: 📚 Reference → Parameters → Parameter Smoothing
     - Outcome: Smooth parameter changes, no clicks
   - Checkpoint: Your effects have professional-feeling controls

#### Stage 5: Sound Design Capabilities (2-3 hours)
10. **Oscillator and Synthesis** (90 minutes)
    - **Basic Oscillator** (45 minutes)
      - Location: 🍳 Fundamentals → Basic Oscillator
      - Outcome: Generate waveforms from scratch
    - **Waveshaper Distortion** (45 minutes)
      - Location: 🎵 Audio Effects → Waveshaper Distortion  
      - Outcome: Complex distortion algorithms
    - Checkpoint: You can generate and shape audio signals

11. **Stereo and Spatial Effects** (60 minutes)
    - **Stereo Processing** (30 minutes)
      - Location: 🍳 Fundamentals → Stereo Processing
      - Outcome: Left/right channel manipulation
    - **Phaser Effect** (30 minutes)
      - Location: 🎵 Audio Effects → Phaser Effect
      - Outcome: Spatial movement and stereo imaging
    - Checkpoint: Your effects work convincingly in stereo

#### Stage 6: Production Skills (3-4 hours)
12. **Complex Effects** (2 hours)
    - **Reverb Implementation** (60 minutes)
      - Location: 🎵 Audio Effects → Reverb Simple
      - Outcome: Space and ambience creation
    - **Compressor Design** (60 minutes)
      - Location: 🎵 Audio Effects → Compressor Basic
      - Outcome: Dynamic range control
    - Checkpoint: You can build studio-quality effects

13. **Timing and Rhythm** (90 minutes)
    - **Tempo Sync** (45 minutes)
      - Location: ⏱️ Timing & Utilities → Sync to Tempo
      - Outcome: Effects that lock to host tempo
    - **Clock Dividers** (45 minutes)
      - Location: ⏱️ Timing & Utilities → Clock Dividers
      - Outcome: Rhythmic subdivision effects
    - Checkpoint: Your effects integrate musically with DAW projects

14. **User Interface Polish** (60 minutes)
    - **LED Control** (30 minutes)
      - Location: 🎓 Tutorials → Light Up LEDs
      - Outcome: Visual feedback for your effects
    - **Parameter Display** (30 minutes)
      - Location: ⏱️ Timing & Utilities → Parameter Display
      - Outcome: Clear indication of current settings
    - Checkpoint: Your effects feel professional and polished

**Path 2 Completion Goal:** You can create any common audio effect you can imagine, with professional controls and timing integration. You understand both the technical and musical aspects of audio processing.

---

## Quick Reference Guide

### I need to...
- **Find a specific function:** → 📚 Reference Docs → Audio Processing Reference
- **Build a specific effect:** → 🎵 Cookbook - Audio Effects → [Effect Name]
- **Fix compilation errors:** → 🎓 Tutorials → Compiler Troubleshooting Guide  
- **Make my effect faster:** → ⚡ Performance → Optimization Basics
- **Connect to DAW features:** → 🔗 Integration → Preset System
- **Understand memory issues:** → 🏗️ Architecture → Memory Model
- **Learn advanced techniques:** → 🌊 Cookbook - Advanced

### Time Estimates for Common Tasks
- **Learn basic concept:** 15-30 minutes
- **Build simple effect:** 30-60 minutes  
- **Build complex effect:** 1-3 hours
- **Debug compilation problem:** 15-45 minutes
- **Add professional polish:** 30-60 minutes per feature

### Getting Unstuck
1. **Check QUICKSTART** - Covers 80% of common issues
2. **Search for error message** - Usually in Compiler Troubleshooting
3. **Look at similar working example** - Find closest cookbook recipe
4. **Check parameter ranges** - Reference docs have exact specifications
5. **Verify basic syntax** - Language reference has all rules

Remember: Every expert was once a beginner. Take your time with each stage, and don't hesitate to revisit earlier sections when needed.