# BUILD AND PROCESSING WORKFLOWS

**Purpose**: Reusable frameworks for automated documentation processing and delivery  
**Extracted From**: Build scripts, session logs, and implementation plans  
**Application**: Any documentation project requiring automated processing, format conversion, or batch operations

---

## 🔧 CORE BUILD AUTOMATION PRINCIPLES

### **1. DOCUMENT PRESERVATION STRATEGY**
- **Work on copies only** - All modifications happen in temporary directories
- **Original files untouched** - Source documentation remains pristine
- **Cleanup preserves originals** - Only temp files removed after processing
- **Backup before major operations** - Safety mechanisms for destructive changes

### **2. MODULAR SCRIPT ARCHITECTURE**
```bash
# Standard build script organization
project/
├── create-file-order.sh      # Define processing sequence
├── process-content.sh        # Content transformation operations
├── generate-output.sh        # Format conversion and compilation
├── build-master.sh           # One-command orchestration script
└── validate-output.sh        # Quality assurance checks
```

### **3. ERROR HANDLING AND VALIDATION**
- **Dependency checking** before execution
- **Step-by-step validation** with clear error messages
- **Rollback capabilities** for failed operations
- **Progress reporting** throughout the process

---

## 📋 UNIVERSAL FILE PROCESSING FRAMEWORK

### **Phase 1: Preparation and Discovery**
```bash
# File discovery and organization
echo "Phase 1: Preparing file inventory..."

# Create working directory
mkdir -p temp/processed
mkdir -p output

# Generate file list in logical order
find content/ -name "*.md" | sort > file-inventory.txt

# Validate file existence and accessibility
while read file; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done < file-inventory.txt

echo "✅ File inventory complete ($(wc -l < file-inventory.txt) files)"
```

### **Phase 2: Content Processing Pipeline**
```bash
# Content transformation operations
echo "Phase 2: Processing content..."

process_file() {
    local source_file="$1"
    local temp_file="temp/processed/$(basename "$source_file")"
    
    # Copy to temp directory
    cp "$source_file" "$temp_file"
    
    # Apply transformations (example operations)
    sed -i 's/old_pattern/new_pattern/g' "$temp_file"
    
    # Validate transformations
    if ! validate_syntax "$temp_file"; then
        echo "❌ Syntax validation failed: $temp_file"
        return 1
    fi
    
    echo "✅ Processed: $(basename "$source_file")"
    return 0
}

# Process all files
while read file; do
    if ! process_file "$file"; then
        echo "❌ Processing failed for: $file"
        exit 1
    fi
done < file-inventory.txt
```

### **Phase 3: Output Generation**
```bash
# Format conversion and compilation
echo "Phase 3: Generating output..."

# Combine processed files
cat temp/processed/*.md > temp/combined-content.md

# Apply format-specific processing
case "$OUTPUT_FORMAT" in
    "pdf")
        generate_pdf "temp/combined-content.md" "output/document.pdf"
        ;;
    "html")
        generate_html "temp/combined-content.md" "output/index.html"
        ;;
    *)
        echo "❌ Unknown output format: $OUTPUT_FORMAT"
        exit 1
        ;;
esac
```

### **Phase 4: Quality Assurance**
```bash
# Validation and verification
echo "Phase 4: Quality assurance..."

validate_output() {
    local output_file="$1"
    
    if [ ! -f "$output_file" ]; then
        echo "❌ Output file not generated: $output_file"
        return 1
    fi
    
    # Size validation
    local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file")
    if [ "$file_size" -lt 1000 ]; then
        echo "❌ Output file suspiciously small: $file_size bytes"
        return 1
    fi
    
    # Format-specific validation
    case "$output_file" in
        *.pdf)
            # Validate PDF structure if tools available
            if command -v pdfinfo >/dev/null; then
                pdfinfo "$output_file" >/dev/null || return 1
            fi
            ;;
        *.html)
            # Basic HTML validation
            if ! grep -q "<html>" "$output_file"; then
                echo "❌ Invalid HTML structure"
                return 1
            fi
            ;;
    esac
    
    echo "✅ Output validation passed: $output_file"
    return 0
}
```

---

## 🛠️ SPECIALIZED PROCESSING PATTERNS

### **Link Enhancement System**
```bash
# Add hyperlinks to content copies
add_glossary_links() {
    local file="$1"
    local glossary_file="$2"
    
    # Read glossary terms
    while IFS='|' read -r term definition; do
        # Skip empty lines and comments
        [[ "$term" =~ ^[[:space:]]*$ ]] && continue
        [[ "$term" =~ ^# ]] && continue
        
        # Create markdown link
        local link="[$term](#$(echo "$term" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g'))"
        
        # Replace term with link (careful to avoid double-linking)
        sed -i "s/\\b$term\\b/$link/g" "$file"
        
    done < "$glossary_file"
}

# Apply to all processed files
for file in temp/processed/*.md; do
    add_glossary_links "$file" "glossary-terms.txt"
done
```

### **Content Consolidation Pipeline**
```bash
# Combine multiple files with proper structure
consolidate_content() {
    local output_file="$1"
    local file_order="$2"
    
    # Initialize output file
    echo "# Combined Documentation" > "$output_file"
    echo "" >> "$output_file"
    
    # Add table of contents
    echo "## Table of Contents" >> "$output_file"
    echo "" >> "$output_file"
    
    # Process files in specified order
    while read file_path; do
        # Extract title from file
        local title=$(head -n 1 "$file_path" | sed 's/^# //')
        local anchor=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')
        
        # Add to table of contents
        echo "- [$title](#$anchor)" >> "$output_file"
        
    done < "$file_order"
    
    echo "" >> "$output_file"
    
    # Combine actual content
    while read file_path; do
        echo "" >> "$output_file"
        echo "---" >> "$output_file"
        echo "" >> "$output_file"
        cat "$file_path" >> "$output_file"
        echo "" >> "$output_file"
    done < "$file_order"
}
```

### **Format-Specific Generation**

#### **PDF Generation Pipeline**
```bash
generate_pdf() {
    local source_md="$1"
    local output_pdf="$2"
    
    # Check dependencies
    if ! command -v pandoc >/dev/null; then
        echo "❌ Pandoc not found. Install with:"
        echo "   Windows: choco install pandoc"
        echo "   macOS: brew install pandoc"
        echo "   Linux: sudo apt install pandoc"
        return 1
    fi
    
    # Generate PDF with options
    pandoc "$source_md" \
        -o "$output_pdf" \
        --pdf-engine=wkhtmltopdf \
        --toc \
        --toc-depth=3 \
        --number-sections \
        --metadata title="Documentation" \
        --css styles.css \
        --self-contained
    
    if [ $? -eq 0 ]; then
        echo "✅ PDF generated: $output_pdf"
        echo "📊 File size: $(ls -lh "$output_pdf" | awk '{print $5}')"
    else
        echo "❌ PDF generation failed"
        return 1
    fi
}
```

#### **Static Site Generation**
```bash
generate_static_site() {
    local content_dir="$1"
    local output_dir="$2"
    local site_generator="$3"
    
    case "$site_generator" in
        "mkdocs")
            # Generate MkDocs configuration
            cat > mkdocs.yml <<EOF
site_name: Documentation
nav:
  - Home: index.md
  $(find "$content_dir" -name "*.md" | sed 's|.*content/||' | sort | sed 's|^|  - |; s|\.md$||; s|/| > |g; s|-| |g')
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.highlight
EOF
            mkdocs build --site-dir "$output_dir"
            ;;
            
        "docusaurus")
            # Initialize Docusaurus site
            npx create-docusaurus@latest "$output_dir" classic
            # Copy processed content to docs directory
            cp -r "$content_dir"/* "$output_dir/docs/"
            cd "$output_dir" && npm run build
            ;;
            
        *)
            echo "❌ Unknown site generator: $site_generator"
            return 1
            ;;
    esac
}
```

---

## 📊 BATCH PROCESSING STRATEGIES

### **Parallel Processing Framework**
```bash
# Process multiple files concurrently
process_batch() {
    local file_list="$1"
    local max_jobs="${2:-4}"
    
    # Function to process single file
    process_single() {
        local file="$1"
        echo "Processing: $file"
        
        # Actual processing logic here
        apply_transformations "$file"
        validate_result "$file"
        
        echo "✅ Completed: $file"
    }
    
    # Export function for parallel execution
    export -f process_single
    
    # Process files in parallel
    cat "$file_list" | xargs -n 1 -P "$max_jobs" -I {} bash -c 'process_single "$@"' _ {}
}
```

### **Incremental Processing**
```bash
# Only process files that have changed
incremental_build() {
    local source_dir="$1"
    local output_dir="$2"
    local manifest_file="checksums.txt"
    
    # Generate current checksums
    find "$source_dir" -name "*.md" -exec md5sum {} \; > temp_checksums.txt
    
    # Compare with previous checksums
    if [ -f "$manifest_file" ]; then
        # Find changed files
        comm -13 <(sort "$manifest_file") <(sort temp_checksums.txt) | cut -d' ' -f2- > changed_files.txt
        
        echo "Processing $(wc -l < changed_files.txt) changed files..."
        
        # Process only changed files
        while read file; do
            process_file "$file"
        done < changed_files.txt
        
    else
        echo "No previous manifest found. Processing all files..."
        # Process all files
        find "$source_dir" -name "*.md" | while read file; do
            process_file "$file"
        done
    fi
    
    # Update manifest
    mv temp_checksums.txt "$manifest_file"
}
```

---

## 🔍 VALIDATION AND TESTING FRAMEWORKS

### **Content Validation Pipeline**
```bash
validate_content() {
    local file="$1"
    local errors=0
    
    # Syntax validation
    if ! validate_markdown_syntax "$file"; then
        echo "❌ Markdown syntax error in: $file"
        ((errors++))
    fi
    
    # Link validation
    if ! validate_internal_links "$file"; then
        echo "❌ Broken internal links in: $file"
        ((errors++))
    fi
    
    # Content structure validation
    if ! validate_content_structure "$file"; then
        echo "❌ Invalid content structure in: $file"
        ((errors++))
    fi
    
    return $errors
}

# Validate all processed content
validate_all_content() {
    local total_errors=0
    
    for file in temp/processed/*.md; do
        if ! validate_content "$file"; then
            ((total_errors++))
        fi
    done
    
    if [ $total_errors -eq 0 ]; then
        echo "✅ All content validation passed"
        return 0
    else
        echo "❌ Content validation failed with $total_errors errors"
        return 1
    fi
}
```

### **Output Testing Framework**
```bash
test_output() {
    local output_file="$1"
    local expected_features="$2"
    
    echo "Testing output: $output_file"
    
    # Test file existence and size
    if [ ! -f "$output_file" ] || [ ! -s "$output_file" ]; then
        echo "❌ Output file missing or empty"
        return 1
    fi
    
    # Test specific features
    while read feature; do
        case "$feature" in
            "toc")
                if ! grep -q "Table of Contents\|TOC" "$output_file"; then
                    echo "❌ Missing table of contents"
                    return 1
                fi
                ;;
            "links")
                if ! grep -q "\[.*\](#.*)" "$output_file"; then
                    echo "❌ Missing internal links"
                    return 1
                fi
                ;;
            "search")
                # Implementation depends on output format
                ;;
        esac
    done < "$expected_features"
    
    echo "✅ Output testing passed"
    return 0
}
```

---

## 🚀 MASTER BUILD ORCHESTRATION

### **One-Command Build System**
```bash
#!/bin/bash
# master-build.sh - Orchestrates entire build process

set -e  # Exit on any error

# Configuration
SOURCE_DIR="content"
OUTPUT_FORMAT="${1:-pdf}"
OUTPUT_DIR="output"
TEMP_DIR="temp"

# Main orchestration function
main() {
    echo "=== Documentation Build System ==="
    echo "Output format: $OUTPUT_FORMAT"
    echo ""
    
    # Phase 1: Setup and validation
    setup_environment
    
    # Phase 2: Content discovery and preparation
    discover_content
    
    # Phase 3: Content processing
    process_content
    
    # Phase 4: Output generation
    generate_output "$OUTPUT_FORMAT"
    
    # Phase 5: Quality assurance
    validate_output
    
    # Phase 6: Cleanup and reporting
    cleanup_and_report
    
    echo "🎉 Build completed successfully!"
}

# Execute main function
main "$@"
```

### **Error Recovery and Debugging**
```bash
# Error handling and recovery mechanisms
error_handler() {
    local exit_code=$?
    local line_number=$1
    
    echo "❌ BUILD FAILED at line $line_number with exit code $exit_code"
    echo ""
    echo "Debug information:"
    echo "- Current phase: $CURRENT_PHASE"
    echo "- Last successful step: $LAST_STEP"
    echo "- Temp directory contents:"
    ls -la "$TEMP_DIR" 2>/dev/null || echo "  (Temp directory not created)"
    
    # Preserve temp files for debugging
    if [ -d "$TEMP_DIR" ]; then
        mv "$TEMP_DIR" "debug-$(date +%Y%m%d-%H%M%S)"
        echo "- Temp files preserved in debug directory"
    fi
    
    exit $exit_code
}

# Set error trap
trap 'error_handler $LINENO' ERR
```

---

## 🔄 ADAPTATION PATTERNS

### **Configuration-Driven Processing**
```bash
# Load configuration from file
load_config() {
    local config_file="${1:-build-config.yaml}"
    
    if [ -f "$config_file" ]; then
        # Parse YAML configuration (requires yq or custom parser)
        export BUILD_FORMAT=$(yq e '.output.format' "$config_file")
        export BUILD_OPTIONS=$(yq e '.output.options[]' "$config_file" | tr '\n' ' ')
        export CONTENT_DIRS=$(yq e '.source.directories[]' "$config_file" | tr '\n' ' ')
    else
        # Use defaults
        export BUILD_FORMAT="pdf"
        export BUILD_OPTIONS="--toc --number-sections"
        export CONTENT_DIRS="content"
    fi
}
```

### **Plugin Architecture**
```bash
# Support for custom processing plugins
load_plugins() {
    local plugin_dir="plugins"
    
    if [ -d "$plugin_dir" ]; then
        for plugin in "$plugin_dir"/*.sh; do
            if [ -f "$plugin" ]; then
                echo "Loading plugin: $(basename "$plugin")"
                source "$plugin"
            fi
        done
    fi
}

# Plugin interface example
# plugins/custom-processor.sh
custom_process_file() {
    local file="$1"
    # Custom processing logic
    echo "Custom processing: $file"
}

# Register plugin hook
PROCESS_HOOKS+=("custom_process_file")
```

---

**Implementation Note**: This framework provides a comprehensive foundation for automated documentation processing that can be adapted for various output formats, content types, and quality requirements. The modular design enables easy customization and extension for specific project needs.