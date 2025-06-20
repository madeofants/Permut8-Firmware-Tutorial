# Permut8 Firmware Development Glossary

*Complete terminology reference for embedded audio programming with Impala*

## Foundation Concepts

### DSP and Audio Fundamentals

**Digital Signal Processing (DSP)**  
Real-time manipulation of audio using mathematical algorithms. In Permut8, DSP means changing numbers that represent audio samples to create effects.

**Audio samples**  
Individual numbers representing speaker position at one moment in time. In Permut8: integers from -2047 to +2047 representing 12-bit audio precision.

**Real-time audio processing**  
Processing audio samples immediately as they arrive, 44,100 times per second, with predictable timing constraints requiring yield() calls.

**Code-to-sound relationship**  
Fundamental DSP concept: changing numbers in code immediately changes what listeners hear through speakers.

**Speaker cone movement**  
Physical representation of audio samples: positive numbers push speaker out, negative numbers pull in, zero = silence.

## Language Foundation

### Core Language Terms

**Impala**  
Real-time audio programming language for embedded systems, specifically designed for Permut8 hardware. Optimized for predictable execution with static memory allocation and cooperative multitasking.

**Real-time constraints**  
Timing requirements for audio processing requiring predictable execution with no dynamic memory allocation. Every operation must complete within one audio sample period.

**Static allocation**  
Memory management using fixed-size arrays with no dynamic allocation (no malloc/free). All memory is allocated at compile time for predictable behavior.

**yield()**  
Native function that returns control to the audio engine every sample, essential for real-time processing. Must be called once per processing cycle.
```impala
// Required parameter constants
const int OPERAND_1_HIGH_PARAM_INDEX
const int OPERAND_1_LOW_PARAM_INDEX
const int OPERAND_2_HIGH_PARAM_INDEX
const int OPERAND_2_LOW_PARAM_INDEX
const int OPERATOR_1_PARAM_INDEX
const int OPERATOR_2_PARAM_INDEX
const int SWITCHES_PARAM_INDEX
const int CLOCK_FREQ_PARAM_INDEX
const int PARAM_COUNT

yield(); // Return control to host

```

**extern native**  
Declaration keyword for system-provided functions available from Permut8 hardware.
```impala
extern native yield
```

### Data Types and Declarations

**const int**  
Compile-time constant declaration for immutable integer values.
```impala
const int SAMPLE_RATE = 44100
```

**global**  
Keyword for persistent variables that maintain state across processing cycles.
```impala
global array signal[2]
```

**locals clause**  
Function variable declaration section for temporary variables with function scope.
```impala
function process()
locals int tempValue, int result
```

**array declaration**  
Fixed-size array syntax with global or local scope for static memory allocation.
```impala
global array audioBuffer[1024]
```

## Hardware Interface

### Core Hardware Arrays

**signal[2]**  
Global audio I/O array for stereo processing (left/right channels). Audio samples range from -2047 to 2047.
```impala
global array signal[2]  // [left, right] audio samples
```

**params[PARAM_COUNT]**  
Global parameter array for hardware knob values (0-255 range).
```impala
global array params[PARAM_COUNT]  // Knob values (0-255)
```

**displayLEDs[4]**  
Global LED control array for visual feedback (8-bit brightness masks).
```impala
global array displayLEDs[4]  // LED control arrays
```

### Hardware Specifications

**PRAWN_FIRMWARE_PATCH_FORMAT**  
Required firmware version constant (value: 2) for compatibility identification.
```impala
const int PRAWN_FIRMWARE_PATCH_FORMAT = 2
```

**Audio samples**  
12-bit signed integers (-2047 to 2047) representing digital audio data. This range provides sufficient resolution for professional audio processing.

**Parameter range**  
Hardware control value range (0-255) from knobs and controls. Must be scaled to appropriate ranges for audio parameters.

## Audio Processing

### Audio Generation

**Digital oscillator**  
Software-based sound generator using mathematical waveforms. Creates audio by repeatedly outputting numbers at audio rate.

**Phase accumulator**  
Counter (0-65535) representing position in waveform cycle for oscillator state tracking.
```impala
global int phase = 0  // Current position in the waveform
```

**Phase increment**  
Amount added to phase each sample, controlling oscillator frequency/pitch.
```impala
phase = (phase + frequency) % 65536
```

### Waveform Types

**Triangle wave**  
Linear waveform creating smooth, warm sound character.
```impala
if (phase < 32768) {
    amplitude = phase - 16384;
} else {
    amplitude = 49152 - phase;
}
```

**Square wave**  
Binary waveform creating harsh, buzzy sound character.
```impala
if (phase < 32768) {
    amplitude = 16384;
} else {
    amplitude = -16384;
}
```

**Sawtooth wave**  
Linear ramp waveform creating bright, buzzy sound with rich harmonic content.
```impala
amplitude = (phase / 2) - 16384;  // Linear ramp
```

### Time-Based Effects

**Circular buffer**  
Fixed-size array with wraparound indexing for continuous data storage without memory allocation.

**Delay time**  
Duration between input and output of processed audio signal, measured in samples or seconds.

**Feedback**  
Portion of delayed output fed back into input for multiple echoes and sustained effects.

**Dry signal**  
Original, unprocessed audio input without any effect processing applied.

**Wet signal**  
Processed audio output from delay effect, containing the delayed/echoed audio.

### Distortion and Audio Effects

**Basic gain distortion**  
Simplest distortion created by multiplying audio samples by values larger than 1, causing clipping when samples exceed ±2047 range.

**Hard clipping**  
Immediate cutoff distortion where samples exceeding limits are truncated to maximum values, creating harsh digital sound.
```impala
if (signal > 2047) signal = 2047;  // Hard clipping
```

**Soft clipping**  
Gradual compression distortion using mathematical curves to smoothly limit audio, creating warm musical sound.
```impala
if (signal > threshold) signal = threshold + (excess / 4);  // Soft clipping
```

**Clipping threshold**  
The audio level where distortion begins, controlling the character and amount of harmonic saturation.

**Gain staging**  
Professional audio practice of controlling signal levels at each processing stage to optimize sound quality and prevent unwanted distortion.

**Musical vs digital distortion**  
Distinction between warm, pleasant-sounding soft clipping algorithms and harsh, unpleasant hard clipping artifacts.

**Progressive distortion**  
Educational approach building distortion complexity from basic multiplication through professional soft-clipping algorithms.

### Audio Engineering for Programmers

**Gain compensation**  
Automatic output level adjustment to maintain consistent volume when effects change signal amplitude, similar to auto-scaling algorithms.
```impala
int compensationGain = 256 / distortionAmount;  // Inverse scaling
```

**Parameter smoothing**  
Gradual transition between parameter values to prevent audio clicks, similar to interpolation techniques in programming.
```impala
smoothedValue = smoothedValue + ((targetValue - smoothedValue) / 8);
```

**Dynamic range management**  
Professional audio practice using available bit depth efficiently, similar to optimizing data type usage in programming.

**Headroom**  
Safety margin in audio processing preventing overflow, similar to buffer space in programming applications.

**Signal-to-noise ratio**  
Audio quality measure comparing useful signal to unwanted artifacts, analogous to clean code vs technical debt.

**Audio range validation**  
Safety practice ensuring audio samples remain within ±2047 bounds, similar to bounds checking in programming.

**Professional audio patterns**  
Standard practices including input validation, graceful degradation, and predictable behavior for audio applications.

### Digital Audio Effects

**Quantization**  
Bit depth reduction technique using right-shift operations to create digital stepping artifacts and lo-fi distortion.

**Sample-and-hold**  
Sample rate reduction technique holding audio samples for multiple cycles to create characteristic stepping and aliasing effects.

**Digital artifacts**  
Characteristic distortions from digital processing including quantization noise, aliasing, and stepping effects.

**Bit depth reduction**  
Quality degradation technique reducing effective resolution from 12-bit to lower bit depths for creative digital distortion.

**Harmonic content**  
Frequency spectrum characteristics of waveforms including fundamental frequency and overtones creating timbral character.

**Aliasing**  
Sampling rate artifacts creating false frequencies when sample rate is insufficient for signal content.

**Waveform generation**  
Basic audio synthesis creating mathematical waveforms including sine, triangle, square, and sawtooth patterns.

**Frequency control**  
Pitch management through phase increment adjustment controlling oscillator fundamental frequency.

**Amplitude control**  
Volume management through gain multiplication and scaling affecting signal loudness and dynamics.

## Parameter Control

### Parameter Processing

**Parameter scaling**  
Converting 0-255 knob values to usable parameter ranges through mathematical transformation.
```impala
int scaledValue = minValue + ((knobValue * (maxValue - minValue)) / 255);
```

**Parameter smoothing**  
Gradual transition between parameter values to prevent audio artifacts and clicking.
```impala
smoothedValue = smoothedValue + ((targetValue - smoothedValue) / 8);
```

**Zipper noise**  
Audio artifacts from sudden parameter changes causing clicking or zipper sounds. Prevented by parameter smoothing.

### Scaling Techniques

**Linear scaling**  
Direct proportional parameter mapping maintaining equal steps.
```impala
int frequency = 100 + ((knobValue * 1900) / 255);
```

**Exponential scaling**  
Non-linear parameter mapping providing musical feel with more control in lower ranges.
```impala
int scaledKnob = (knobValue * knobValue) / 255;
```

**Bipolar scaling**  
Parameter ranges spanning negative to positive values around center.
```impala
int bipolar = ((knobValue - 127) * 200) / 127;
```

## Development Workflow

### Firmware Types

**Full patches**  
Firmware replacing entire DSP engine with complete audio processing. Implements `process()` function for direct signal control.

**Mod patches**  
Firmware modifying built-in operators without replacing entire DSP chain. Implements `operate1()` and/or `operate2()` functions.

**Architecture decision**  
Critical choice between Full and Mod patch approaches based on project requirements, performance needs, and complexity trade-offs.

**Operator replacement**  
Mod patch capability to replace specific built-in Permut8 operators while maintaining framework integration and automatic features.

**Framework integration**  
Automatic Permut8 feature integration available in Mod patches including preset system, MIDI handling, and parameter management.

**Direct audio access**  
Full patch advantage providing immediate control over signal arrays for complete audio processing chain replacement.

**Memory-based I/O**  
Mod patch communication method using read/write operations to memory positions rather than direct signal array access.

**Migration strategy**  
Systematic approach for converting between Mod and Full patch architectures, including code restructuring and interface changes.

### Development Tools

**PikaCmd.exe**  
Impala compiler executable that converts .impala source files to .gazl assembly.
```bash
PikaCmd.exe -compile ringmod_code.impala
```

**Console**  
Plugin interface for loading firmware and debugging within Permut8 plugin.

**patch command**  
Command to load compiled firmware (.gazl files) into Permut8 via plugin interface.
```
Load bitcrush.gazl via plugin interface
```

### Development Process

**Compilation**  
Process converting .impala source code to .gazl executable assembly.

**Firmware loading**  
Process of installing compiled firmware into Permut8 hardware.

**Professional development phases**  
Systematic workflow stages including concept, planning, implementation, testing, optimization, documentation, and deployment.

**Incremental development**  
Building complexity gradually through successive feature additions, starting with minimal working implementations.

**Build automation**  
Scripted compilation processes using batch files or build systems for consistent, repeatable firmware generation.

**Version management**  
Systematic tracking of software changes, releases, and compatibility using version numbering and change documentation.

**Release preparation**  
Quality assurance processes including testing, validation, documentation updates, and deployment packaging.

### Audio I/O Fundamentals

**Audio passthrough**  
Default behavior where audio flows unchanged through plugin when no processing is applied to signal arrays.

**Signal validation**  
Process of ensuring audio samples remain within valid range (-2047 to +2047) to prevent distortion and hardware issues.

**I/O troubleshooting**  
Systematic approach to diagnosing audio connectivity issues including signal flow, channel routing, and parameter integration.

**Foundation workflow**  
Basic development process starting with working audio I/O before adding effects processing and advanced features.

## Memory Management

### Memory Architecture

**Static memory**  
Fixed allocation using global arrays with predictable memory usage for real-time constraints.
```impala
global array buffer[1024];  // Static allocation
```

**Circular buffer**  
Fixed-size array with wraparound indexing for continuous data storage.
```impala
buffer[pos % BUFFER_SIZE] = sample;
```

**Memory regions**  
Distinct areas of memory with different access characteristics and purposes.

### Performance Optimization

**Cache optimization**  
Memory layout and access patterns designed for optimal cache performance.

**Fixed-point arithmetic**  
Integer math techniques for fractional calculations avoiding floating-point overhead.

### Development Testing and Quality Assurance

**Unit testing**  
Component-level validation testing individual functions and algorithms in isolation to verify correctness.

**Integration testing**  
System-level validation testing complete signal chain and component interactions under realistic conditions.

**Performance profiling**  
Systematic measurement of CPU usage, memory consumption, and execution time to identify optimization opportunities.

**Compilation error**  
Build-time failures including syntax errors, type mismatches, undefined variables, and linking problems.

**Runtime error**  
Execution-time problems including array bounds violations, arithmetic overflow, and infinite loops.

**Debug by elimination**  
Systematic troubleshooting approach isolating problems by progressively removing code sections to identify root causes.

**Safety patterns**  
Defensive programming practices including bounds checking, parameter validation, and graceful error handling.

**LED debugging**  
Visual troubleshooting technique using displayLEDs arrays to provide real-time feedback on plugin state and parameter values.

**Systematic debugging methodology**  
Professional debugging approach including problem reproduction, hypothesis formation, testing, and validation procedures.

## Integration Systems

### MIDI Integration

**MIDI Learn**  
Dynamic MIDI CC assignment system for real-time controller mapping.

**MIDI Sync**  
MIDI clock synchronization for tempo-locked effects and processing.

**MIDI CC**  
MIDI Continuous Controller messages for parameter automation.

### Audio Processing Safety

**Audio range management**  
Preventing overflow beyond ±2047 limits to avoid distortion.

**Clipping**  
Limiting audio values to prevent distortion and hardware damage.
```impala
if (result > 2047) result = 2047;
if (result < -2047) result = -2047;
```

**Real-time processing**  
Sample-by-sample audio processing at audio rate with yield() calls.

## Assembly Integration

### GAZL Assembly

**GAZL**  
Assembly language output from Impala compilation targeting Permut8 virtual machine.

**Virtual registers**  
GAZL virtual machine registers (%0, %1, %2) for temporary computation storage.

**Memory operations**  
GAZL instructions (PEEK/POKE) for loading and storing data in memory.

---

## Cross-Reference Index

### By Complexity Level
- **Beginner**: Basic language terms, hardware interface, simple audio processing
- **Intermediate**: Parameter control, memory management, basic effects
- **Advanced**: Assembly integration, complex effects, optimization techniques
- **Expert**: MIDI integration, advanced memory patterns, performance optimization

### By Usage Context
- **Core Development**: Language terms, compilation, basic hardware interface
- **Audio Programming**: Synthesis terms, effects processing, audio safety
- **System Integration**: MIDI terms, parameter systems, advanced features
- **Performance Optimization**: Memory management, assembly, real-time constraints

---

*This glossary covers 160+ essential terms for Permut8 firmware development, providing clear definitions, practical examples, and cross-references for all levels of embedded audio programming with Impala. Includes comprehensive coverage of DSP fundamentals, progressive distortion techniques, audio engineering concepts for programmers, architecture decisions, professional development workflow, systematic debugging, and digital audio effects terminology.*