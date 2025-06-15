#!/bin/bash
# build-pdf-docs.sh - Master script to build PDF documentation

echo "=== Permut8 Documentation PDF Builder ==="
echo ""

# Function to check if a tool is available
check_tool() {
    if command -v "$1" &> /dev/null; then
        echo "✅ $1 found"
        return 0
    else
        echo "❌ $1 not found"
        return 1
    fi
}

# Function to install tools if possible
try_install() {
    echo ""
    echo "Attempting to install required tools..."
    
    # Detect package manager and try installation
    if command -v apt &> /dev/null; then
        echo "Detected apt package manager (Ubuntu/Debian)"
        echo "To install required tools, run:"
        echo "  sudo apt update && sudo apt install pandoc wkhtmltopdf"
        echo ""
        echo "You can also try without sudo (may not work):"
        read -p "Try installation without sudo? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            apt update && apt install pandoc wkhtmltopdf
        fi
    elif command -v yum &> /dev/null; then
        echo "Detected yum package manager (RHEL/CentOS)"
        echo "To install required tools, run:"
        echo "  sudo yum install pandoc wkhtmltopdf"
    elif command -v brew &> /dev/null; then
        echo "Detected Homebrew (macOS)"
        echo "Installing tools with Homebrew..."
        brew install pandoc
        brew install --cask wkhtmltopdf
    else
        echo "Package manager not detected. Please install manually:"
        echo "- Pandoc: https://pandoc.org/installing.html"
        echo "- wkhtmltopdf: https://wkhtmltopdf.org/downloads.html"
    fi
}

echo "Checking required tools..."
pandoc_available=false
wkhtmltopdf_available=false

if check_tool pandoc; then
    pandoc_available=true
fi

if check_tool wkhtmltopdf; then
    wkhtmltopdf_available=true
fi

# If tools are missing, try to install or provide guidance
if [ "$pandoc_available" = false ]; then
    echo ""
    echo "⚠️  Pandoc is required for PDF generation."
    try_install
    
    # Check again after installation attempt
    if check_tool pandoc; then
        pandoc_available=true
        echo "✅ Pandoc installation successful"
    else
        echo "❌ Pandoc installation failed or skipped"
        echo ""
        echo "📋 Manual installation options:"
        echo "   Ubuntu/WSL: sudo apt update && sudo apt install pandoc"
        echo "   macOS: brew install pandoc"
        echo "   Windows: Download from https://pandoc.org/installing.html"
        echo ""
        echo "🔄 You can also continue with HTML-only generation..."
        read -p "Continue without PDF capability? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Exiting. Please install pandoc and run again."
            exit 1
        fi
    fi
fi

echo ""
echo "Step 1: Creating file order list..."
chmod +x create-file-order.sh
./create-file-order.sh

if [ $? -ne 0 ]; then
    echo "❌ Failed to create file order list"
    exit 1
fi

echo ""
echo "Step 2: Adding glossary links to copies..."
chmod +x add-glossary-links.sh
./add-glossary-links.sh

if [ $? -ne 0 ]; then
    echo "❌ Failed to add glossary links"
    exit 1
fi

echo ""
echo "Step 3: Generating documentation..."
chmod +x generate-pdf.sh
./generate-pdf.sh

echo ""
if [ -f "Permut8-Firmware-Documentation.pdf" ] || [ -f "Permut8-Firmware-Documentation.html" ]; then
    echo "🎉 Documentation generation complete!"
    echo ""
    echo "📁 Generated files:"
    if [ -f "Permut8-Firmware-Documentation.pdf" ]; then
        file_size=$(ls -lh Permut8-Firmware-Documentation.pdf | awk '{print $5}')
        echo "   📄 Permut8-Firmware-Documentation.pdf ($file_size)"
    fi
    if [ -f "Permut8-Firmware-Documentation.html" ]; then
        file_size=$(ls -lh Permut8-Firmware-Documentation.html | awk '{print $5}')
        echo "   🌐 Permut8-Firmware-Documentation.html ($file_size)"
    fi
    echo ""
    echo "✨ Features included:"
    echo "   ✅ All 67 A+ quality files in logical reading order"
    echo "   ✅ Complete 90-minute foundation learning path"
    echo "   ✅ Clickable table of contents and navigation"
    echo "   ✅ Linked glossary terms throughout text"
    echo "   ✅ Syntax-highlighted code examples"
    echo "   ✅ Professional formatting and layout"
    echo "   ✅ Full-text search capability"
    echo ""
    echo "📖 Usage tips:"
    echo "   • Use Ctrl+F to search across all content"
    echo "   • Click glossary links to jump to definitions"
    echo "   • Use bookmarks panel for quick navigation"
    echo "   • Follow the 90-minute foundation path for beginners"
    echo ""
    echo "🔄 To regenerate after updating source files:"
    echo "   ./build-pdf-docs.sh"
else
    echo "❌ Documentation generation failed"
    echo "Check error messages above for troubleshooting"
    exit 1
fi

# Cleanup temp directory
if [ -d "temp-pdf-processing" ]; then
    echo ""
    echo "🧹 Cleaning up temporary files..."
    rm -rf temp-pdf-processing
    echo "✅ Cleanup complete"
fi

echo ""
echo "🚀 PDF companion documentation ready for use!"