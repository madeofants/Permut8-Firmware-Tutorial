#!/bin/bash
# add-glossary-links.sh
# Adds clickable glossary links to copies of documentation files

echo "Adding glossary links to documentation files..."

# Function to add glossary links to a file
add_links() {
    local file="$1"
    
    echo "  Processing: $(basename "$file")"
    
    # Core language terms → link to glossary
    sed -i 's/\byield()\b/[yield()](\#yield)/g' "$file"
    sed -i 's/\bprocess()\b/[process()](\#process)/g' "$file"
    sed -i 's/\boperate1()\b/[operate1()](\#operate1)/g' "$file"
    sed -i 's/\boperate2()\b/[operate2()](\#operate2)/g' "$file"
    sed -i 's/\bImpala\b/[Impala](\#impala)/g' "$file"
    sed -i 's/\bDSP\b/[DSP](\#dsp)/g' "$file"
    sed -i 's/\bGAZL\b/[GAZL](\#gazl)/g' "$file"
    
    # Hardware interface terms
    sed -i 's/\bsignal\[0\]\b/[signal\[0\]](\#signal)/g' "$file"
    sed -i 's/\bsignal\[1\]\b/[signal\[1\]](\#signal)/g' "$file"
    sed -i 's/\bparams\[\b/[params\[](\#params)/g' "$file"
    sed -i 's/\bdisplayLEDs\[\b/[displayLEDs\[](\#displayleds)/g' "$file"
    sed -i 's/\bPRAWN_FIRMWARE_PATCH_FORMAT\b/[PRAWN_FIRMWARE_PATCH_FORMAT](\#prawn-firmware-patch-format)/g' "$file"
    
    # Audio processing terms
    sed -i 's/\breal-time\b/[real-time](\#real-time)/g' "$file"
    sed -i 's/\breal time\b/[real time](\#real-time)/g' "$file"
    sed -i 's/\bcircular buffer\b/[circular buffer](\#circular-buffer)/g' "$file"
    sed -i 's/\bdelay line\b/[delay line](\#delay-line)/g' "$file"
    sed -i 's/\bfeedback\b/[feedback](\#feedback)/g' "$file"
    sed -i 's/\bphase accumulator\b/[phase accumulator](\#phase-accumulator)/g' "$file"
    sed -i 's/\bphase increment\b/[phase increment](\#phase-increment)/g' "$file"
    
    # Distortion and effects terms
    sed -i 's/\bhard clipping\b/[hard clipping](\#hard-clipping)/g' "$file"
    sed -i 's/\bsoft clipping\b/[soft clipping](\#soft-clipping)/g' "$file"
    sed -i 's/\bwaveshaper\b/[waveshaper](\#waveshaper)/g' "$file"
    sed -i 's/\bgain staging\b/[gain staging](\#gain-staging)/g' "$file"
    sed -i 's/\bgain compensation\b/[gain compensation](\#gain-compensation)/g' "$file"
    sed -i 's/\bparameter smoothing\b/[parameter smoothing](\#parameter-smoothing)/g' "$file"
    
    # Development terms
    sed -i 's/\bFull patches\b/[Full patches](\#full-patches)/g' "$file"
    sed -i 's/\bMod patches\b/[Mod patches](\#mod-patches)/g' "$file"
    sed -i 's/\bPikaCmd\.exe\b/[PikaCmd.exe](\#pikacmd)/g' "$file"
    sed -i 's/\bcompilation\b/[compilation](\#compilation)/g' "$file"
    sed -i 's/\bfirmware\b/[firmware](\#firmware)/g' "$file"
    
    # Memory and performance terms
    sed -i 's/\bstatic memory\b/[static memory](\#static-memory)/g' "$file"
    sed -i 's/\bstatic allocation\b/[static allocation](\#static-allocation)/g' "$file"
    sed -i 's/\bcache optimization\b/[cache optimization](\#cache-optimization)/g' "$file"
    sed -i 's/\bfixed-point arithmetic\b/[fixed-point arithmetic](\#fixed-point-arithmetic)/g' "$file"
    sed -i 's/\blookup table\b/[lookup table](\#lookup-table)/g' "$file"
    
    # Audio engineering terms
    sed -i 's/\bsample rate\b/[sample rate](\#sample-rate)/g' "$file"
    sed -i 's/\bnyquist frequency\b/[nyquist frequency](\#nyquist-frequency)/g' "$file"
    sed -i 's/\baliasing\b/[aliasing](\#aliasing)/g' "$file"
    sed -i 's/\bfilter\b/[filter](\#filter)/g' "$file"
    sed -i 's/\boscillator\b/[oscillator](\#oscillator)/g' "$file"
    sed -i 's/\benvelope\b/[envelope](\#envelope)/g' "$file"
    
    # Integration terms
    sed -i 's/\bMIDI\b/[MIDI](\#midi)/g' "$file"
    sed -i 's/\bMIDI CC\b/[MIDI CC](\#midi-cc)/g' "$file"
    sed -i 's/\bpreset\b/[preset](\#preset)/g' "$file"
    sed -i 's/\bstate recall\b/[state recall](\#state-recall)/g' "$file"
    sed -i 's/\bautomation\b/[automation](\#automation)/g' "$file"
}

# IMPORTANT: Work on copies to preserve original files
echo "Creating temp directory for file copies..."
mkdir -p temp

# Copy files and add glossary links
while IFS= read -r file; do
    if [[ "$file" =~ ^[^#] && -f "$file" ]]; then
        # Copy original to temp directory
        cp "$file" "temp/$(basename "$file")"
        # Add glossary links to the copy
        add_links "temp/$(basename "$file")"
    fi
done < file-order.txt

echo ""
echo "✓ Glossary links added to copies in temp/ directory"
echo "✓ Original files preserved unchanged"
echo "✓ Processed $(find temp -name "*.md" | wc -l) documentation files"
echo ""
echo "Link examples added:"
echo "  yield() → [yield()](#yield)"
echo "  DSP → [DSP](#dsp)"
echo "  signal[0] → [signal[0]](#signal)"
echo "  real-time → [real-time](#real-time)"
echo "  circular buffer → [circular buffer](#circular-buffer)"