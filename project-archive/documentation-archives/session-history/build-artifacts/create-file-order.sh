#!/bin/bash
# create-file-order.sh
# Creates ordered list of files for logical reading in PDF

echo "Creating file order for PDF generation..."

cat > file-order.txt << 'EOF'
# Foundation Learning Path (90 minutes) - Pages 1-50
content/user-guides/QUICKSTART.md
content/user-guides/cookbook/fundamentals/how-dsp-affects-sound.md
content/user-guides/tutorials/getting-audio-in-and-out.md
content/user-guides/cookbook/fundamentals/simplest-distortion.md
content/fundamentals/audio-engineering-for-programmers.md

# Development Tutorials - Pages 51-100
content/user-guides/tutorials/mod-vs-full-architecture-guide.md
content/user-guides/tutorials/complete-development-workflow.md
content/user-guides/tutorials/debug-your-plugin.md

# Language Reference - Pages 101-150
content/language/core_language_reference.md
content/language/language-syntax-reference.md
content/language/standard-library-reference.md
content/language/types-and-operators.md
content/language/core-functions.md

# Architecture Reference - Pages 151-180
content/architecture/memory-layout.md
content/architecture/memory-model.md
content/architecture/processing-order.md
content/architecture/state-management.md
content/architecture/architecture_patterns.md

# Cookbook - Fundamentals - Pages 181-220
content/user-guides/cookbook/fundamentals/basic-oscillator.md
content/user-guides/cookbook/fundamentals/basic-filter.md
content/user-guides/cookbook/fundamentals/gain-and-volume.md
content/user-guides/cookbook/fundamentals/memory-basics.md
content/user-guides/cookbook/fundamentals/parameter-mapping.md
content/user-guides/cookbook/fundamentals/circular-buffer-guide.md
content/user-guides/cookbook/fundamentals/envelope-basics.md
content/user-guides/cookbook/fundamentals/stereo-processing.md
content/user-guides/cookbook/fundamentals/switches-and-modes.md
content/user-guides/cookbook/fundamentals/db-gain-control.md
content/user-guides/cookbook/fundamentals/level-metering.md
content/user-guides/cookbook/fundamentals/output-limiting.md

# Cookbook - Audio Effects - Pages 221-260
content/user-guides/cookbook/audio-effects/make-a-delay.md
content/user-guides/cookbook/audio-effects/waveshaper-distortion.md
content/user-guides/cookbook/audio-effects/chorus-effect.md
content/user-guides/cookbook/audio-effects/phaser-effect.md
content/user-guides/cookbook/audio-effects/compressor-basic.md
content/user-guides/cookbook/audio-effects/bitcrusher.md
content/user-guides/cookbook/audio-effects/granular-synthesis.md
content/user-guides/cookbook/audio-effects/pitch-shifter.md
content/user-guides/cookbook/audio-effects/multi-band-compressor.md
content/user-guides/cookbook/audio-effects/reverb-simple.md

# Performance Optimization - Pages 261-290
content/performance/optimization-basics.md
content/performance/memory-patterns.md
content/performance/lookup-tables.md
content/performance/fixed-point.md
content/performance/efficient-math.md
content/performance/batch-processing.md
content/performance/memory-access.md

# Integration Systems - Pages 291-320
content/integration/preset-system.md
content/integration/midi-learn-simplified.md
content/integration/midi-sync-simplified.md
content/integration/parameter-morphing.md
content/integration/state-recall-simplified.md
content/integration/preset-friendly.md
content/integration/midi-learn.md
content/integration/midi-sync.md
content/integration/state-recall.md

# Assembly Programming - Pages 321-340
content/assembly/gazl-assembly-introduction.md
content/assembly/gazl-debugging-profiling.md
content/assembly/gazl-optimization.md
content/assembly/gazl-integration-production.md

# Reference Documentation - Pages 341-360
content/reference/audio_processing_reference.md
content/reference/parameters_reference.md
content/reference/memory_management.md
content/reference/utilities_reference.md

# Navigation and Index (at end for reference) - Pages 361-380
content/index/navigation.md
content/index/cross-references.md
content/index/themes.md
content/index/language-foundation.md
content/index/master-index.md
content/index/glossary.md
EOF

echo "✓ File order created: file-order.txt"
echo "✓ Total files organized: $(grep -c '^content/' file-order.txt)"
echo "✓ Foundation path (first 5 files) prioritized"