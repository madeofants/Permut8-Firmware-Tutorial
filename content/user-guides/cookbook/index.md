# Permut8 Cookbook

*Complete collection of ready-to-use audio effects and techniques*

## About the Cookbook

This cookbook provides **36 complete, tested recipes** for building audio effects and understanding DSP concepts on the Permut8. Each recipe includes working code, parameter explanations, and practical modifications.

**Difficulty Levels:**
- 🟢 **Beginner** (1-2 hours) - Basic concepts with simple implementations
- 🟡 **Intermediate** (2-4 hours) - More complex effects requiring DSP understanding  
- 🔴 **Advanced** (4+ hours) - Sophisticated techniques for experienced developers

## Learning Pathway

**Start Here:** Begin with [Fundamentals](#fundamentals) to build essential DSP skills, then explore [Audio Effects](#audio-effects) for practical applications.

**Prerequisites:** Complete [QUICKSTART](../QUICKSTART.md) and [Make Your First Sound](../tutorials/make-your-first-sound.md) before starting cookbook recipes.

---

## Fundamentals 🟢
*Essential building blocks for all audio processing*

| Recipe | Time | Concepts |
|--------|------|----------|
| [Basic Oscillator](fundamentals/basic-oscillator.md) | 1h | Phase accumulation, waveform generation |
| [Basic Filter](fundamentals/basic-filter.md) | 1h | State variable filters, frequency response |
| [Envelope Basics](fundamentals/envelope-basics.md) | 1h | ADSR envelopes, exponential curves |
| [Gain and Volume](fundamentals/gain-and-volume.md) | 30m | Amplitude control, dB conversion |
| [Memory Basics](fundamentals/memory-basics.md) | 45m | Buffer management, circular buffers |
| [Parameter Mapping](fundamentals/parameter-mapping.md) | 45m | Control scaling, exponential mapping |
| [Stereo Processing](fundamentals/stereo-processing.md) | 1h | Left/right channels, stereo effects |
| [Switches and Modes](fundamentals/switches-and-modes.md) | 30m | Mode selection, parameter switching |
| [Circular Buffer Guide](fundamentals/circular-buffer-guide.md) | 1.5h | Ring buffers, delay lines |
| [dB Gain Control](fundamentals/db-gain-control.md) | 1h | Logarithmic volume, dB calculations |
| [How DSP Affects Sound](fundamentals/how-dsp-affects-sound.md) | 45m | Audio theory, digital signal processing |
| [Level Metering](fundamentals/level-metering.md) | 1h | RMS, peak detection, VU meters |
| [Output Limiting](fundamentals/output-limiting.md) | 1h | Clipping prevention, soft limiting |
| [Simplest Distortion](fundamentals/simplest-distortion.md) | 30m | Waveshaping, saturation |

---

## Audio Effects 🟡
*Complete effect implementations ready for performance*

### Dynamics
| Recipe | Time | Concepts |
|--------|------|----------|
| [Compressor Basic](audio-effects/compressor-basic.md) | 2h | Envelope following, gain reduction |
| [Multi-band Compressor](audio-effects/multi-band-compressor.md) | 4h | Frequency splitting, independent compression |

### Time-Based Effects  
| Recipe | Time | Concepts |
|--------|------|----------|
| [Make a Delay](audio-effects/make-a-delay.md) | 2h | Delay lines, feedback, modulation |
| [Chorus Effect](audio-effects/chorus-effect.md) | 3h | Modulated delay, voice doubling |
| [Phaser Effect](audio-effects/phaser-effect.md) | 3h | All-pass filters, LFO modulation |
| [Reverb Simple](audio-effects/reverb-simple.md) | 2.5h | Comb filters, early reflections |

### Distortion & Saturation
| Recipe | Time | Concepts |
|--------|------|----------|
| [Bitcrusher](audio-effects/bitcrusher.md) | 1.5h | Bit reduction, sample rate reduction |
| [Waveshaper Distortion](audio-effects/waveshaper-distortion.md) | 2h | Transfer functions, harmonic saturation |

### Pitch & Synthesis
| Recipe | Time | Concepts |
|--------|------|----------|
| [Pitch Shifter](audio-effects/pitch-shifter.md) | 4h | Granular synthesis, time stretching |
| [Granular Synthesis](audio-effects/granular-synthesis.md) | 4h | Grain clouds, texture synthesis |

---

## Spectral Processing 🔴
*Frequency domain analysis and manipulation*

| Recipe | Time | Concepts |
|--------|------|----------|
| [FFT Basics](spectral-processing/fft-basics.md) | 3h | Discrete Fourier Transform, frequency analysis |
| [Frequency Analysis](spectral-processing/frequency-analysis.md) | 3h | Spectral analysis, magnitude/phase |
| [Phase Vocoder](spectral-processing/phase-vocoder.md) | 5h | Time-stretching, pitch shifting |
| [Spectral Filtering](spectral-processing/spectral-filtering.md) | 4h | Frequency domain filtering |

---

## Timing & Sync 🟡
*Tempo-based and rhythmic effects*

| Recipe | Time | Concepts |
|--------|------|----------|
| [Clock Dividers](timing/clock-dividers.md) | 2h | Rhythmic subdivision, tempo tracking |
| [Swing Timing](timing/swing-timing.md) | 2.5h | Groove quantization, timing offset |
| [Sync to Tempo](timing/sync-to-tempo.md) | 2h | BPM synchronization, musical timing |

---

## Utilities 🟢
*Helper functions and system integration*

| Recipe | Time | Concepts |
|--------|------|----------|
| [Crossfade](utilities/crossfade.md) | 1h | Signal blending, smooth transitions |
| [Input Monitoring](utilities/input-monitoring.md) | 1h | Signal routing, level monitoring |
| [Mix Multiple Signals](utilities/mix-multiple-signals.md) | 1.5h | Signal summing, mixer design |

---

## Visual Feedback 🟡
*LED control and visual display*

| Recipe | Time | Concepts |
|--------|------|----------|
| [Parameter Display](visual-feedback/parameter-display.md) | 2h | LED mapping, parameter visualization |

---

## Advanced Patterns 🔴
*Complex techniques for expert developers*

| Recipe | Time | Concepts |
|--------|------|----------|
| [Firmware Patterns](advanced/firmware-patterns.md) | 6h | System architecture, optimization |

---

## Quick Reference

### By Difficulty
- **🟢 Beginner (14 recipes)**: Start here for basic DSP concepts
- **🟡 Intermediate (11 recipes)**: Practical effects and techniques  
- **🔴 Advanced (11 recipes)**: Complex processing and optimization

### By Time Commitment
- **Quick (< 1 hour)**: 4 recipes for immediate results
- **Short (1-2 hours)**: 16 recipes for focused learning
- **Medium (2-4 hours)**: 12 recipes for complete effects
- **Long (4+ hours)**: 4 recipes for advanced techniques

### By Audio Category
- **Synthesis**: Oscillators, envelopes, parameter mapping
- **Dynamics**: Compressors, limiters, level control
- **Time Effects**: Delays, reverb, chorus, phaser
- **Distortion**: Bitcrushing, waveshaping, saturation
- **Spectral**: FFT, frequency analysis, spectral filters
- **Utilities**: Mixing, crossfading, monitoring

---

## Getting Help

**Stuck on a recipe?** Check the [Debug Your Plugin](../tutorials/debug-your-plugin.md) tutorial for troubleshooting techniques.

**Want more theory?** See [Audio Engineering for Programmers](../../fundamentals/audio-engineering-for-programmers.md) for deeper DSP understanding.

**Ready for production?** Follow [Complete Development Workflow](../tutorials/complete-development-workflow.md) for professional development practices.

---

## Next Steps

1. **Complete a fundamentals recipe** to build essential skills
2. **Try an audio effect** that interests you  
3. **Modify parameters** and experiment with variations
4. **Combine techniques** from multiple recipes
5. **Build your own effects** using cookbook patterns

*The cookbook is designed for hands-on learning. Don't just read - build, experiment, and create!*

---

*Part of the [Permut8 Documentation](../../index.md) • [Getting Started](../QUICKSTART.md) • [Tutorials](../tutorials/) • [Reference](../../reference/)*