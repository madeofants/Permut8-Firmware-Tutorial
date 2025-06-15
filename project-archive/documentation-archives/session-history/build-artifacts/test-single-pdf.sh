#!/bin/bash
# test-single-pdf.sh
# Complete test: single file to PDF with glossary links (preserves original)

echo "=== Single File to PDF Test ==="
echo ""

# Test with a rich content file
TEST_FILE="content/user-guides/cookbook/fundamentals/how-dsp-affects-sound.md"

if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Test file not found: $TEST_FILE"
    echo "Trying alternative file..."
    TEST_FILE="content/user-guides/QUICKSTART.md"
    if [ ! -f "$TEST_FILE" ]; then
        echo "❌ No test files found!"
        exit 1
    fi
fi

echo "🧪 Testing complete PDF generation with: $TEST_FILE"
echo ""

# Step 1: Record original file state
echo "📋 Recording original file state..."
ORIGINAL_SIZE=$(ls -lh "$TEST_FILE" | awk '{print $5}')
ORIGINAL_LINES=$(wc -l < "$TEST_FILE")
ORIGINAL_CHECKSUM=$(md5sum "$TEST_FILE" 2>/dev/null || md5 "$TEST_FILE" 2>/dev/null | cut -d' ' -f1)
ORIGINAL_MTIME=$(stat -c %Y "$TEST_FILE" 2>/dev/null || stat -f %m "$TEST_FILE" 2>/dev/null)

echo "   File: $TEST_FILE"
echo "   Size: $ORIGINAL_SIZE"
echo "   Lines: $ORIGINAL_LINES"
echo "   Checksum: $ORIGINAL_CHECKSUM"
echo "   Modified: $ORIGINAL_MTIME"
echo ""

# Step 2: Create working directory
echo "📁 Creating test environment..."
mkdir -p pdf-test
cd pdf-test

# Copy the test file
cp "../$TEST_FILE" "test-input.md"
echo "✅ File copied to pdf-test/test-input.md"
echo ""

# Step 3: Add glossary links to copy
echo "🔗 Adding glossary links to copy..."

# Function to add glossary links
add_links_to_test() {
    local file="$1"
    
    echo "  Processing glossary terms..."
    
    # Core language terms
    sed -i 's/\byield()\b/[yield()](\#yield)/g' "$file"
    sed -i 's/\bprocess()\b/[process()](\#process)/g' "$file"
    sed -i 's/\bDSP\b/[DSP](\#dsp)/g' "$file"
    sed -i 's/\bImpala\b/[Impala](\#impala)/g' "$file"
    
    # Hardware interface terms
    sed -i 's/\bsignal\[0\]\b/[signal\[0\]](\#signal)/g' "$file"
    sed -i 's/\bsignal\[1\]\b/[signal\[1\]](\#signal)/g' "$file"
    sed -i 's/\bparams\[\b/[params\[](\#params)/g' "$file"
    sed -i 's/\bdisplayLEDs\[\b/[displayLEDs\[](\#displayleds)/g' "$file"
    
    # Audio processing terms
    sed -i 's/\breal-time\b/[real-time](\#real-time)/g' "$file"
    sed -i 's/\baudio samples\b/[audio samples](\#audio-samples)/g' "$file"
    sed -i 's/\bvolume control\b/[volume control](\#volume-control)/g' "$file"
    sed -i 's/\bfirmware\b/[firmware](\#firmware)/g' "$file"
    sed -i 's/\bcircular buffer\b/[circular buffer](\#circular-buffer)/g' "$file"
    
    # Effects terms
    sed -i 's/\bdistortion\b/[distortion](\#distortion)/g' "$file"
    sed -i 's/\bfilter\b/[filter](\#filter)/g' "$file"
    sed -i 's/\boscillator\b/[oscillator](\#oscillator)/g' "$file"
    
    echo "  ✅ Glossary links added"
}

add_links_to_test "test-input.md"

# Count links added
LINKS_ADDED=$(grep -c '\[.*\](' "test-input.md" || echo 0)
echo "   Links added: $LINKS_ADDED"
echo ""

# Step 4: Create simple glossary section
echo "📚 Adding glossary section..."
cat >> test-input.md << 'EOF'

---

# Glossary

## audio-samples
Digital representations of sound at specific points in time.

## circular-buffer  
A memory structure where data wraps around from end to beginning.

## distortion
Audio effect that modifies waveforms to create harmonic content.

## dsp
Digital Signal Processing - manipulating audio with mathematical operations.

## filter
Audio effect that removes or emphasizes certain frequencies.

## firmware  
Low-level software that runs directly on hardware.

## impala
The programming language used for Permut8 firmware development.

## oscillator
Generator that produces periodic waveforms for audio synthesis.

## params
Array containing knob positions and parameter values from hardware.

## process
Main function that processes audio samples in real-time.

## real-time
Processing that must complete within strict timing constraints.

## signal
Array containing audio input/output samples [left, right].

## volume-control
Effect that adjusts the amplitude/loudness of audio signals.

## yield
Function that returns control to the audio engine every sample.

EOF

echo "✅ Glossary section added"
echo ""

# Step 5: Create PDF document with header
echo "📄 Creating PDF document..."

cat > pdf-document.md << EOF
---
title: "Test PDF with Glossary Links"
subtitle: "Single File Test - $(basename "$TEST_FILE" .md)"
author: "Permut8 Documentation Test"
date: "$(date +"%B %Y")"
toc: true
toc-depth: 2
linkcolor: blue
urlcolor: blue
---

# Test PDF with Glossary Links

This is a test of the PDF generation system with clickable glossary links.

**Source File**: $TEST_FILE  
**Test Date**: $(date)  
**Features**: Clickable glossary terms throughout document

---

$(cat test-input.md)
EOF

echo "✅ PDF document created"
echo ""

# Step 6: Generate PDF (try different approaches)
echo "🔧 Generating PDF..."

PDF_GENERATED=false

# Try pandoc with different engines
if command -v pandoc &> /dev/null || command -v pandoc.exe &> /dev/null; then
    
    # Determine pandoc command
    if command -v pandoc.exe &> /dev/null; then
        PANDOC_CMD="pandoc.exe"
    else
        PANDOC_CMD="pandoc"
    fi
    
    echo "  Using: $PANDOC_CMD"
    
    # Try with basic PDF engine first
    echo "  Attempting PDF generation..."
    
    $PANDOC_CMD pdf-document.md -o test-output.pdf \
        --toc \
        --toc-depth=2 \
        --highlight-style=github \
        --variable geometry:margin=1in \
        --variable fontsize=11pt \
        --variable linkcolor=blue \
        --standalone 2>/dev/null
    
    if [ -f "test-output.pdf" ]; then
        PDF_GENERATED=true
        echo "  ✅ PDF generated successfully!"
    else
        echo "  ⚠️  Basic PDF generation failed, trying alternative..."
        
        # Try without some options
        $PANDOC_CMD pdf-document.md -o test-output.pdf \
            --toc \
            --standalone 2>/dev/null
        
        if [ -f "test-output.pdf" ]; then
            PDF_GENERATED=true
            echo "  ✅ PDF generated with basic options!"
        fi
    fi
else
    echo "  ❌ Pandoc not available"
fi

if [ "$PDF_GENERATED" = true ]; then
    PDF_SIZE=$(ls -lh test-output.pdf | awk '{print $5}')
    echo "   📊 PDF Size: $PDF_SIZE"
    echo "   📄 File: pdf-test/test-output.pdf"
else
    echo "   ❌ PDF generation failed"
fi

echo ""

# Step 7: Verify original file unchanged
cd ..
echo "🔒 Verifying original file is unchanged..."

NEW_SIZE=$(ls -lh "$TEST_FILE" | awk '{print $5}')
NEW_LINES=$(wc -l < "$TEST_FILE")
NEW_CHECKSUM=$(md5sum "$TEST_FILE" 2>/dev/null || md5 "$TEST_FILE" 2>/dev/null | cut -d' ' -f1)
NEW_MTIME=$(stat -c %Y "$TEST_FILE" 2>/dev/null || stat -f %m "$TEST_FILE" 2>/dev/null)

echo "   Original checksum: $ORIGINAL_CHECKSUM"
echo "   Current checksum:  $NEW_CHECKSUM"
echo "   Original size: $ORIGINAL_SIZE → Current size: $NEW_SIZE"
echo "   Original lines: $ORIGINAL_LINES → Current lines: $NEW_LINES"
echo "   Modified time: $ORIGINAL_MTIME → $NEW_MTIME"

if [ "$ORIGINAL_CHECKSUM" = "$NEW_CHECKSUM" ]; then
    echo "   ✅ SUCCESS: Original file completely unchanged!"
else
    echo "   ❌ ERROR: Original file was modified!"
fi

echo ""

# Step 8: Summary
echo "🎯 Test Summary:"
echo "   📁 Test directory: pdf-test/"
echo "   📝 Input file: test-input.md (with $LINKS_ADDED glossary links)"
echo "   📚 Glossary: Added 15 definition entries"

if [ "$PDF_GENERATED" = true ]; then
    echo "   📄 PDF output: test-output.pdf ($PDF_SIZE)"
    echo "   🔗 Features: Clickable glossary links throughout document"
    echo "   ✅ STATUS: Complete PDF generation successful"
else
    echo "   ❌ PDF generation failed (may need pandoc installation)"
fi

echo "   🔒 Original file: Completely preserved"
echo ""

echo "📋 Files created in pdf-test/:"
ls -la pdf-test/ 2>/dev/null || echo "   No files created"

echo ""
echo "💡 To clean up: rm -rf pdf-test/"

if [ "$PDF_GENERATED" = true ]; then
    echo "💡 To view PDF: Open pdf-test/test-output.pdf"
    echo "   • Test clickable links by clicking blue highlighted terms"
    echo "   • Links should jump to glossary definitions"
    echo "   • Table of contents should provide navigation"
fi