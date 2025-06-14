# MIDI Synchronization Techniques

## Overview
Implement precise MIDI clock synchronization for tempo-locked effects, ensuring sample-accurate timing with external sequencers, DAWs, and hardware devices.

> **Note**: This file contains a comprehensive advanced implementation. For a practical working version, see [midi-sync-simplified.md](midi-sync-simplified.md) which provides the same core functionality using proper Impala syntax.

## MIDI Clock Fundamentals

### Clock Reception and Processing
```impala
// MIDI clock state management
struct MIDIClockState {
    bool isRunning;
    int clockCounter;
    int ticksPerBeat;    // 24 MIDI clocks per quarter note
    float currentTempo;
    int samplesPerClock;
    int sampleCounter;
    bool clockReceived;
};

MIDIClockState midiClock = {false, 0, 24, 120.0, 0, 0, false};

// Initialize MIDI clock system
void initMIDIClock() {
    midiClock.ticksPerBeat = 24;  // MIDI standard
    midiClock.currentTempo = 120.0;
    midiClock.samplesPerClock = calculateSamplesPerClock(120.0);
    midiClock.isRunning = false;
    midiClock.clockCounter = 0;
}

// Calculate samples per MIDI clock tick
int calculateSamplesPerClock(float tempo) {
    // MIDI sends 24 clocks per quarter note
    float clocksPerSecond = (tempo / 60.0) * 24.0;
    return (int)(sampleRate / clocksPerSecond);
}
```

### MIDI Message Processing
```impala
// Process incoming MIDI clock messages
void processMIDIClockMessage(unsigned char midiStatus, unsigned char data1) {
    switch (midiStatus) {
        case 0xF8:  // MIDI Clock (24 per quarter note)
            handleMIDIClock();
            break;
            
        case 0xFA:  // MIDI Start
            handleMIDIStart();
            break;
            
        case 0xFB:  // MIDI Continue
            handleMIDIContinue();
            break;
            
        case 0xFC:  // MIDI Stop
            handleMIDIStop();
            break;
            
        case 0xF2:  // Song Position Pointer
            handleSongPosition(data1);
            break;
    }
}

void handleMIDIClock() {
    midiClock.clockReceived = true;
    midiClock.clockCounter++;
    
    // Reset sample counter for precise timing
    midiClock.sampleCounter = 0;
    
    // Update tempo estimation
    updateTempoEstimation();
}

void handleMIDIStart() {
    midiClock.isRunning = true;
    midiClock.clockCounter = 0;
    midiClock.sampleCounter = 0;
    resetSyncedEffects();
}

void handleMIDIStop() {
    midiClock.isRunning = false;
    stopSyncedEffects();
}
```

## Tempo Estimation and Stability

### Real-Time Tempo Detection
```impala
// Tempo estimation with stability filtering
struct TempoEstimator {
    float clockTimestamps[8];  // Recent clock timestamps
    int timestampIndex;
    float estimatedTempo;
    float tempoStability;
    bool tempoLocked;
};

TempoEstimator tempoEst = {0};

void updateTempoEstimation() {
    static int lastClockTime = 0;
    int currentTime = getCurrentSampleTime();
    
    // Store timestamp
    tempoEst.clockTimestamps[tempoEst.timestampIndex] = currentTime;
    tempoEst.timestampIndex = (tempoEst.timestampIndex + 1) % 8;
    
    // Calculate tempo from recent clock intervals
    if (tempoEst.timestampIndex == 0) {  // Buffer full
        float avgClockInterval = calculateAverageInterval();
        float newTempo = calculateTempoFromInterval(avgClockInterval);
        
        // Smooth tempo changes
        tempoEst.estimatedTempo += (newTempo - tempoEst.estimatedTempo) * 0.1;
        
        // Update stability metric
        updateTempoStability(newTempo);
    }
    
    lastClockTime = currentTime;
}

float calculateAverageInterval() {
    float totalInterval = 0.0;
    int validIntervals = 0;
    
    for (int i = 1; i < 8; i++) {
        float interval = tempoEst.clockTimestamps[i] - tempoEst.clockTimestamps[i-1];
        if (interval > 0 && interval < sampleRate) {  // Sanity check
            totalInterval += interval;
            validIntervals++;
        }
    }
    
    return validIntervals > 0 ? totalInterval / validIntervals : 0.0;
}

void updateTempoStability(float newTempo) {
    float tempoChange = abs(newTempo - tempoEst.estimatedTempo);
    float changeRatio = tempoChange / tempoEst.estimatedTempo;
    
    // Stability decreases with tempo changes
    if (changeRatio < 0.01) {  // Less than 1% change
        tempoEst.tempoStability = min(tempoEst.tempoStability + 0.01, 1.0);
    } else {
        tempoEst.tempoStability = max(tempoEst.tempoStability - 0.1, 0.0);
    }
    
    // Lock tempo when stable
    tempoEst.tempoLocked = tempoEst.tempoStability > 0.8;
}
```

### Clock Prediction and Interpolation
```impala
// Predict next MIDI clock for smooth operation
struct ClockPredictor {
    int predictedNextClock;
    float clockPhase;       // 0.0 to 1.0 between clocks
    bool predictionValid;
};

ClockPredictor clockPred = {0, 0.0, false};

void updateClockPrediction() {
    if (!midiClock.isRunning || !tempoEst.tempoLocked) {
        clockPred.predictionValid = false;
        return;
    }
    
    // Update sample counter
    midiClock.sampleCounter++;
    
    // Calculate phase between MIDI clocks
    if (midiClock.samplesPerClock > 0) {
        clockPred.clockPhase = (float)midiClock.sampleCounter / midiClock.samplesPerClock;
    }
    
    // Predict next clock time
    clockPred.predictedNextClock = midiClock.samplesPerClock - midiClock.sampleCounter;
    clockPred.predictionValid = true;
    
    // Reset if we've passed expected clock time
    if (midiClock.sampleCounter >= midiClock.samplesPerClock) {
        if (!midiClock.clockReceived) {
            // Clock is late - adjust timing
            handleLateClockCompensation();
        }
        midiClock.sampleCounter = 0;
        midiClock.clockReceived = false;
    }
}

void handleLateClockCompensation() {
    // Gradually adjust sample rate to compensate for timing drift
    float driftCompensation = 0.001;  // Small adjustment
    midiClock.samplesPerClock = (int)(midiClock.samplesPerClock * (1.0 + driftCompensation));
}
```

## Synchronized Effect Implementation

### Beat-Locked Delay
```impala
// Delay synchronized to MIDI clock divisions
void syncedDelay() {
    // Division settings: 1/4, 1/8, 1/16, 1/32
    int division = (int)params[DELAY_DIVISION];  // 0-3
    int clocksPerNote[] = {24, 12, 6, 3};        // MIDI clocks per note value
    
    // Calculate delay time in samples
    int clocksForDelay = clocksPerNote[division];
    int samplesPerNote = midiClock.samplesPerClock * clocksForDelay;
    
    // Smooth delay time changes to avoid clicks
    static float smoothDelayTime = 0.0;
    smoothDelayTime += (samplesPerNote - smoothDelayTime) * 0.01;
    
    // Apply synchronized delay
    int delayTime = (int)smoothDelayTime;
    processDelayWithFeedback(signal[2], delayTime, params[DELAY_FEEDBACK]);
    
    // Visual feedback - flash LED on beat
    if ((midiClock.clockCounter % clocksForDelay) == 0) {
        displayLEDs[BEAT_LED] = 255;
    } else {
        displayLEDs[BEAT_LED] = max(displayLEDs[BEAT_LED] - 10, 0);
    }
}
```

### Tempo-Locked LFO
```impala
// LFO synchronized to MIDI clock with multiple rate options
struct SyncedLFO {
    float phase;
    float rate;          // In Hz when free-running
    int syncDivision;    // MIDI clock division when synced
    bool syncEnabled;
    float lastValue;
};

SyncedLFO syncLFO = {0.0, 1.0, 24, true, 0.0};

float generateSyncedLFO() {
    if (syncLFO.syncEnabled && midiClock.isRunning && tempoEst.tempoLocked) {
        // Sync to MIDI clock
        int clocksPerCycle = syncLFO.syncDivision;
        float cyclePhase = (float)(midiClock.clockCounter % clocksPerCycle) / clocksPerCycle;
        
        // Add inter-clock interpolation for smooth LFO
        if (clockPred.predictionValid) {
            float interClockPhase = clockPred.clockPhase / clocksPerCycle;
            cyclePhase += interClockPhase;
        }
        
        syncLFO.phase = cyclePhase;
    } else {
        // Free-running mode
        float phaseIncrement = syncLFO.rate / sampleRate;
        syncLFO.phase += phaseIncrement;
        if (syncLFO.phase >= 1.0) syncLFO.phase -= 1.0;
    }
    
    // Generate waveform
    syncLFO.lastValue = sin(syncLFO.phase * 2.0 * M_PI);
    return syncLFO.lastValue;
}

// LFO rate selection for musical divisions
void setSyncedLFORate(int division) {
    // Common musical divisions
    int divisions[] = {96, 48, 24, 12, 6, 3};  // 1 bar to 1/32 note
    syncLFO.syncDivision = divisions[division];
}
```

### Rhythmic Gate Sequencer
```impala
// Simple gate sequencer synced to MIDI clock
struct SyncedGate {
    bool pattern[16];     // 16-step pattern
    int currentStep;
    int clocksPerStep;    // MIDI clocks per sequencer step
    int stepClock;
    bool gateOpen;
};

SyncedGate gateSeq = {{1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0}, 0, 6, 0, false};

void updateSyncedGate() {
    if (!midiClock.isRunning) {
        gateSeq.gateOpen = false;
        return;
    }
    
    // Update step position based on MIDI clock
    gateSeq.stepClock++;
    if (gateSeq.stepClock >= gateSeq.clocksPerStep) {
        gateSeq.stepClock = 0;
        gateSeq.currentStep = (gateSeq.currentStep + 1) % 16;
    }
    
    // Set gate state based on pattern
    gateSeq.gateOpen = gateSeq.pattern[gateSeq.currentStep];
    
    // Apply gate to audio
    if (gateSeq.gateOpen) {
        // Gate open - pass audio through
        float gateLevel = 1.0;
        signal[2] *= gateLevel;
    } else {
        // Gate closed - mute or reduce audio
        float gateLevel = params[GATE_CLOSED_LEVEL];  // 0.0 to 0.1
        signal[2] *= gateLevel;
    }
    
    // Visual feedback
    displayLEDs[STEP_LED] = gateSeq.gateOpen ? 255 : 32;
}
```

## Advanced Synchronization Features

### Song Position Synchronization
```impala
// Handle MIDI Song Position Pointer for precise positioning
void handleSongPosition(unsigned char positionLSB, unsigned char positionMSB) {
    // Song position is in 16th notes (MIDI beats)
    int songPosition = (positionMSB << 7) | positionLSB;
    
    // Convert to MIDI clock ticks (6 clocks per 16th note)
    int totalClocks = songPosition * 6;
    
    // Update clock counter to match song position
    midiClock.clockCounter = totalClocks;
    
    // Reset synchronized effects to match position
    resetEffectsToPosition(songPosition);
}

void resetEffectsToPosition(int position) {
    // Reset LFO phase to match song position
    int lfoSteps = position / (syncLFO.syncDivision / 6);  // Convert to LFO cycles
    syncLFO.phase = (float)(lfoSteps % 1);
    
    // Reset gate sequencer position
    gateSeq.currentStep = (position / (gateSeq.clocksPerStep / 6)) % 16;
    
    // Reset delay buffers if needed for clean start
    if (position == 0) {
        clearDelayBuffers();
    }
}
```

### Multiple Clock Sources
```impala
// Handle multiple timing sources with priority
enum ClockSource {
    INTERNAL_CLOCK,
    MIDI_CLOCK,
    AUDIO_CLICK,
    TAP_TEMPO
};

struct MultiClock {
    ClockSource activeSource;
    ClockSource preferredSource;
    float internalTempo;
    bool autoSwitch;
};

MultiClock multiClock = {INTERNAL_CLOCK, MIDI_CLOCK, 120.0, true};

void updateClockSource() {
    ClockSource newSource = multiClock.activeSource;
    
    if (multiClock.autoSwitch) {
        // Priority: MIDI > Audio Click > Tap > Internal
        if (midiClock.isRunning && tempoEst.tempoLocked) {
            newSource = MIDI_CLOCK;
        } else if (audioClickDetected()) {
            newSource = AUDIO_CLICK;
        } else if (tapTempoActive()) {
            newSource = TAP_TEMPO;
        } else {
            newSource = INTERNAL_CLOCK;
        }
    }
    
    // Switch clock source if changed
    if (newSource != multiClock.activeSource) {
        switchClockSource(newSource);
        multiClock.activeSource = newSource;
    }
}

void switchClockSource(ClockSource newSource) {
    // Smooth transition between clock sources
    switch (newSource) {
        case MIDI_CLOCK:
            // Sync internal timing to MIDI
            multiClock.internalTempo = tempoEst.estimatedTempo;
            break;
            
        case INTERNAL_CLOCK:
            // Maintain last known tempo
            break;
            
        case TAP_TEMPO:
            // Use tap tempo measurement
            multiClock.internalTempo = getTapTempo();
            break;
    }
    
    // Update display to show active source
    updateClockSourceDisplay(newSource);
}
```

## Performance and Stability

### Jitter Compensation
```impala
// Compensate for MIDI timing jitter
struct JitterFilter {
    float clockTimes[4];
    int index;
    float averageInterval;
    bool stable;
};

JitterFilter jitterFilter = {0};

void filterMIDIJitter() {
    static int lastClockSample = 0;
    int currentSample = getCurrentSampleTime();
    
    // Store clock interval
    float interval = currentSample - lastClockSample;
    jitterFilter.clockTimes[jitterFilter.index] = interval;
    jitterFilter.index = (jitterFilter.index + 1) % 4;
    
    // Calculate average interval
    float total = 0.0;
    for (int i = 0; i < 4; i++) {
        total += jitterFilter.clockTimes[i];
    }
    jitterFilter.averageInterval = total / 4.0;
    
    // Update samples per clock with filtered value
    if (jitterFilter.averageInterval > 0) {
        midiClock.samplesPerClock = (int)jitterFilter.averageInterval;
    }
    
    lastClockSample = currentSample;
}
```

### Sync Status Display
```impala
// Visual feedback for synchronization status
void updateSyncDisplay() {
    // Clock source indicator
    switch (multiClock.activeSource) {
        case MIDI_CLOCK:
            displayLEDs[SOURCE_LED] = tempoEst.tempoLocked ? 255 : 128;
            break;
        case INTERNAL_CLOCK:
            displayLEDs[SOURCE_LED] = 64;
            break;
        case TAP_TEMPO:
            displayLEDs[SOURCE_LED] = 192;
            break;
    }
    
    // Tempo stability indicator
    int stabilityLED = (int)(tempoEst.tempoStability * 255);
    displayLEDs[STABILITY_LED] = stabilityLED;
    
    // Beat indicator
    if (midiClock.clockCounter % 24 == 0) {  // Quarter note
        displayLEDs[BEAT_LED] = 255;
    } else {
        displayLEDs[BEAT_LED] = max(displayLEDs[BEAT_LED] - 5, 0);
    }
}
```

## Integration Examples

### Complete Synchronized Effect
```impala
// Multi-synchronized modulation effect
void synchronizedModulation() {
    // Update all timing systems
    updateClockPrediction();
    filterMIDIJitter();
    updateClockSource();
    
    // Generate synchronized modulation
    float syncedLFO = generateSyncedLFO();
    
    // Apply tempo-locked modulation
    float modulationRate = syncedLFO * params[MOD_DEPTH];
    signal[2] = applyModulation(signal[2], modulationRate);
    
    // Update synchronized gate
    updateSyncedGate();
    
    // Apply synchronized delay
    syncedDelay();
    
    // Update displays
    updateSyncDisplay();
}
```

## Key Benefits

**Sample-Accurate Timing**: Precise synchronization with external sequencers and DAWs through MIDI clock interpolation.

**Tempo Stability**: Advanced filtering eliminates MIDI jitter while maintaining musical timing accuracy.

**Musical Divisions**: Support for standard musical note divisions (whole notes to 32nd notes) with visual feedback.

**Multiple Sources**: Automatic switching between MIDI, audio click, tap tempo, and internal clock sources.

**Performance Ready**: Robust handling of tempo changes, start/stop commands, and song position updates.

Use these techniques to create effects that lock perfectly to external timing sources, enabling professional studio integration and live performance reliability.
