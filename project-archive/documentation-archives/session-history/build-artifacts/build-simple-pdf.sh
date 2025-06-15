#!/bin/bash
# build-simple-pdf.sh
# Master script to build PDF with glossary links

echo "=== Permut8 Documentation - Simple PDF Builder ==="
echo ""

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null && ! command -v "$1.exe" &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        case "$1" in
            "pandoc")
                echo "   Windows: choco install pandoc"
                echo "   macOS: brew install pandoc"
                echo "   Linux: sudo apt install pandoc"
                ;;
        esac
        return 1
    else
        echo "✅ $1 found"
        return 0
    fi
}

# Check required tools
echo "Checking required tools..."
if ! check_command "pandoc"; then
    echo ""
    echo "Please install the required tools and run this script again."
    exit 1
fi

echo ""
echo "📋 Building PDF with the following features:"
echo "   ✅ All 67 files combined in logical reading order"
echo "   ✅ Clickable glossary terms throughout text"
echo "   ✅ Table of contents with page numbers"
echo "   ✅ Foundation learning path (90 minutes) prioritized"
echo "   ✅ Original documentation files preserved"
echo ""

# Step 1: Create file order
echo "Step 1: Creating file order list..."
if [ ! -f "create-file-order.sh" ]; then
    echo "❌ create-file-order.sh not found!"
    exit 1
fi
chmod +x create-file-order.sh
./create-file-order.sh

if [ ! -f "file-order.txt" ]; then
    echo "❌ Failed to create file-order.txt"
    exit 1
fi

echo "✅ File order created ($(grep -c '^content/' file-order.txt) files)"
echo ""

# Step 2: Add glossary links to copies
echo "Step 2: Adding glossary links to file copies..."
if [ ! -f "add-glossary-links.sh" ]; then
    echo "❌ add-glossary-links.sh not found!"
    exit 1
fi
chmod +x add-glossary-links.sh
./add-glossary-links.sh

if [ ! -d "temp" ] || [ -z "$(ls -A temp 2>/dev/null)" ]; then
    echo "❌ Failed to create copies with glossary links"
    exit 1
fi

echo "✅ Glossary links added to $(find temp -name "*.md" | wc -l) files"
echo ""

# Step 3: Generate PDF
echo "Step 3: Generating PDF with Pandoc..."
if [ ! -f "generate-simple-pdf.sh" ]; then
    echo "❌ generate-simple-pdf.sh not found!"
    exit 1
fi
chmod +x generate-simple-pdf.sh
./generate-simple-pdf.sh

# Check if PDF was created
if [ -f "Permut8-Documentation-With-Links.pdf" ]; then
    echo ""
    echo "🎉 SUCCESS! PDF build complete!"
    echo ""
    echo "📄 Generated: Permut8-Documentation-With-Links.pdf"
    echo "📊 File size: $(ls -lh Permut8-Documentation-With-Links.pdf | awk '{print $5}')"
    echo ""
    echo "🎯 What you got:"
    echo "   📚 All 67 A+ quality documentation files"
    echo "   🔗 Clickable glossary terms (yield, DSP, signal[], etc.)"
    echo "   📖 Table of contents with page navigation"
    echo "   🔍 Full-text search capability (Ctrl+F)"
    echo "   📱 Works on any device offline"
    echo "   💾 Original docs completely preserved"
    echo ""
    echo "🚀 Foundation Learning Path (90 minutes):"
    echo "   1. QUICKSTART - Firmware concepts (30 min)"
    echo "   2. How DSP Affects Sound - Core understanding (20 min)"
    echo "   3. Getting Audio In/Out - I/O basics (10 min)"
    echo "   4. Simplest Distortion - First effect (15 min)"
    echo "   5. Audio Engineering for Programmers - Professional bridge (25 min)"
    echo ""
    echo "💡 Usage tips:"
    echo "   • Click any blue highlighted term to jump to glossary"
    echo "   • Use Ctrl+F to search across entire document"
    echo "   • Follow sections 1-5 for complete foundation learning"
    echo "   • Bookmark frequently used sections"
    echo ""
    echo "✅ Build completed successfully!"
else
    echo ""
    echo "❌ BUILD FAILED - PDF was not created"
    echo "Check the error messages above for details."
    exit 1
fi