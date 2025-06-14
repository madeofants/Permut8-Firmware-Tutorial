# Timing Reference

## Clock System Overview

The Permut8 clock system provides tempo-synchronized timing for effects and modulation. The clock operates at 96 pulses per quarter note (24 PPQN × 4) for high-resolution timing.

### Clock Structure
```impala
// Global clock counter (wraps at 6144)
int32 clock;  // 0-6143, representing 16 bars at 96 PPQ

// Clock phase within current beat
float clockPhase;  // 0.0-1.0, current position in beat

// Tempo in BPM
float bpm;  // 20.0-999.0 BPM range
```

## BPM Calculations

### Converting BPM to Sample Intervals
```impala
// Calculate samples per beat
float samplesPerBeat = 60.0 * SAMPLE_RATE / bpm;
// SAMPLE_RATE = 44100 for Permut8

// Calculate samples per clock tick (96 PPQ)
float samplesPerTick = samplesPerBeat / 96.0;

// Example: 120 BPM
// samplesPerBeat = 60.0 * 44100 / 120 = 22050 samples
// samplesPerTick = 22050 / 96 = 229.7 samples
```

### Common Time Divisions
```impala
// Calculate samples for musical divisions
float whole = samplesPerBeat * 4.0;      // Whole note
float half = samplesPerBeat * 2.0;       // Half note
float quarter = samplesPerBeat;          // Quarter note
float eighth = samplesPerBeat * 0.5;     // Eighth note
float sixteenth = samplesPerBeat * 0.25; // Sixteenth note
float triplet = samplesPerBeat / 3.0;    // Triplet

// Dotted notes (1.5x duration)
float dottedQuarter = samplesPerBeat * 1.5;
float dottedEighth = samplesPerBeat * 0.75;
```

## Phase Tracking

### Basic Phase Accumulator
```impala
// Phase accumulator for LFO or delay time
float phase = 0.0;
float phaseInc = 1.0 / samplesPerBeat;

process() {
    // Update phase
    phase += phaseInc;
    if (phase >= 1.0) {
        phase -= 1.0;
        // Trigger on beat
    }
    
    // Use phase for modulation
    float lfo = sin(phase * TWO_PI);
}
```

### Clock-Synced Phase
```impala
// Sync to global clock
process() {
    // Get current beat position
    float beatPos = (clock % 96) / 96.0;
    
    // Quantize to specific divisions
    float quarterPos = beatPos;                    // Quarter notes
    float eighthPos = (beatPos * 2.0) % 1.0;      // Eighth notes
    float sixteenthPos = (beatPos * 4.0) % 1.0;   // Sixteenth notes
}
```

## Clock Division Patterns

### Musical Clock Dividers
```impala
// Clock divider with selectable ratios
int32 dividerCount = 0;
int32 dividerRatio = 24;  // 96/4 = quarter notes

process() {
    // Track clock changes
    static int32 lastClock = 0;
    if (clock != lastClock) {
        dividerCount++;
        if (dividerCount >= dividerRatio) {
            dividerCount = 0;
            // Trigger divided clock event
        }
        lastClock = clock;
    }
}

// Common division ratios
const int32 DIV_WHOLE = 384;      // 96 * 4
const int32 DIV_HALF = 192;       // 96 * 2
const int32 DIV_QUARTER = 96;     // 96 * 1
const int32 DIV_EIGHTH = 48;      // 96 / 2
const int32 DIV_SIXTEENTH = 24;   // 96 / 4
const int32 DIV_TRIPLET = 32;     // 96 / 3
```

### Polyrhythmic Patterns
```impala
// Multiple simultaneous divisions
int32 div3Count = 0;
int32 div4Count = 0;
int32 div5Count = 0;

process() {
    if (clockChanged()) {
        // 3 against 4 polyrhythm
        if (++div3Count >= 32) {  // 96/3
            div3Count = 0;
            trigger3();
        }
        if (++div4Count >= 24) {  // 96/4
            div4Count = 0;
            trigger4();
        }
    }
}
```

## Swing and Shuffle

### Basic Swing
```impala
// Swing amount (0.0 = straight, 1.0 = full swing)
float swingAmount = 0.2;

// Calculate swung eighth note positions
float getSwungPosition(float position) {
    float eighth = position * 2.0;
    int32 eighthIndex = int32(eighth);
    float eighthFrac = eighth - eighthIndex;
    
    if (eighthIndex & 1) {
        // Odd eighths (off-beats) are delayed
        eighthFrac = eighthFrac * (1.0 - swingAmount) + swingAmount;
    }
    
    return (eighthIndex + eighthFrac) * 0.5;
}
```

### Shuffle Patterns
```impala
// 16th note shuffle
float shuffleAmount = 0.3;
int32 shufflePattern = 0b1010110110101101;  // 16-bit pattern

float getShuffledTiming(int32 step) {
    float baseTime = step / 16.0;
    
    // Check if this step should be shuffled
    if (shufflePattern & (1 << (step & 15))) {
        baseTime += shuffleAmount / 16.0;
    }
    
    return baseTime;
}
```

## Tempo Detection

### Simple Beat Tracking
```impala
// Tap tempo implementation
int32 tapTimes[8];
int32 tapIndex = 0;
int32 lastTapTime = 0;

void processTap() {
    int32 currentTime = getSampleTime();
    int32 interval = currentTime - lastTapTime;
    
    if (interval < SAMPLE_RATE * 2) {  // Within 2 seconds
        tapTimes[tapIndex] = interval;
        tapIndex = (tapIndex + 1) & 7;
        
        // Calculate average interval
        int32 sum = 0;
        for (int i = 0; i < 8; i++) {
            sum += tapTimes[i];
        }
        float avgInterval = sum / 8.0;
        
        // Convert to BPM
        bpm = 60.0 * SAMPLE_RATE / avgInterval;
    }
    
    lastTapTime = currentTime;
}
```

## Example: Multi-Tap Delay with Clock Sync

```impala
// Clock-synced multi-tap delay
const int32 MAX_DELAY = 88200;  // 2 seconds at 44.1kHz
float delayBuffer[MAX_DELAY];
int32 writePos = 0;

// Tap positions in musical time
float tapTimes[4] = {
    0.25,   // Sixteenth
    0.5,    // Eighth
    0.75,   // Dotted eighth
    1.0     // Quarter
};

float tapLevels[4] = {0.3, 0.5, 0.4, 0.6};
float feedback = 0.4;

process() {
    float input = signal[0];
    float output = input;
    
    // Calculate samples per beat from BPM
    float samplesPerBeat = 60.0 * 44100.0 / bpm;
    
    // Write to delay buffer
    delayBuffer[writePos] = input;
    
    // Read taps
    for (int32 tap = 0; tap < 4; tap++) {
        // Calculate delay time in samples
        int32 delaySamples = int32(tapTimes[tap] * samplesPerBeat);
        
        // Ensure within buffer bounds
        delaySamples = min(delaySamples, MAX_DELAY - 1);
        
        // Calculate read position
        int32 readPos = writePos - delaySamples;
        if (readPos < 0) readPos += MAX_DELAY;
        
        // Add tap to output
        float tapSignal = delayBuffer[readPos];
        output += tapSignal * tapLevels[tap];
        
        // Add feedback to buffer
        delayBuffer[writePos] += tapSignal * feedback * 0.25;
    }
    
    // Increment write position
    writePos = (writePos + 1) % MAX_DELAY;
    
    // Output
    signal[0] = output;
    signal[1] = output;
}
```

## Clock Utilities

### Phase Reset and Sync
```impala
// Reset phase on beat boundaries
bool shouldReset(int32 division) {
    return (clock % division) == 0;
}

// Smooth phase reset to avoid clicks
float smoothPhase = 0.0;
float phaseSlew = 0.01;

process() {
    if (shouldReset(96)) {  // Reset on quarter notes
        phase = 0.0;
    }
    
    // Smooth phase transitions
    smoothPhase += (phase - smoothPhase) * phaseSlew;
}
```

### Clock Multiplication
```impala
// Generate higher resolution clocks
float multiplier = 3.0;  // 3x clock speed
float multPhase = 0.0;

process() {
    // Calculate phase increment
    float phaseInc = multiplier / samplesPerBeat;
    multPhase += phaseInc;
    
    // Generate triggers
    if (multPhase >= 1.0) {
        multPhase -= 1.0;
        triggerMultipliedClock();
    }
}
```

## Best Practices

1. **Always validate BPM range**: Clamp between 20-999 BPM
2. **Handle clock wraparound**: Clock wraps at 6144 (16 bars)
3. **Use interpolation**: For smooth tempo changes
4. **Prevent buffer overruns**: Check delay times against buffer size
5. **Consider latency**: Account for processing delay in tight sync

## Common Pitfalls

1. **Integer overflow**: Use int32 for sample calculations
2. **Phase accumulation errors**: Reset phase periodically
3. **Tempo change artifacts**: Smooth BPM changes over time
4. **Clock jitter**: Filter clock input for stability

---
*See also: [Audio Processing Reference](audio_processing_reference.md) for DSP techniques*