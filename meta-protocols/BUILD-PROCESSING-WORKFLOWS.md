# BUILD AND PROCESSING WORKFLOWS

**Purpose**: Reusable automation frameworks for project building, testing, and delivery  
**Usage**: Adapt for any project requiring systematic processing, validation, or output generation  
**Extracted From**: Documentation Project HTML/PDF generation and Processing codebase workflows

---

## 🔧 CORE AUTOMATION PRINCIPLES

### **1. PRESERVATION-FIRST STRATEGY**
- **Work on copies only** - Original files remain untouched
- **Backup before operations** - Safety mechanisms for all changes
- **Cleanup preserves originals** - Only temporary files removed
- **Explicit approval for modifications** - Never modify source without permission

### **2. MODULAR SCRIPT ARCHITECTURE**
```bash
# Standard automation script organization
project/
├── scripts/
│   ├── setup-environment.sh      # Environment preparation
│   ├── process-content.sh         # Core processing operations
│   ├── generate-output.sh         # Output generation
│   ├── validate-results.sh        # Quality assurance
│   └── build-master.sh           # One-command orchestration
```

### **3. ERROR HANDLING AND VALIDATION**
- **Dependency checking** before execution
- **Step-by-step validation** with clear error messages
- **Rollback capabilities** for failed operations
- **Progress reporting** throughout the process

---

## 📋 UNIVERSAL PROCESSING FRAMEWORK

### **Phase 1: Environment Setup**
```bash
# Standard environment validation
setup_environment() {
    echo "🔍 Setting up processing environment..."
    
    # Check required tools
    local required_tools=("git" "python" "node")  # Customize per project
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo "❌ Required tool missing: $tool"
            return 1
        fi
        echo "✅ Found: $tool"
    done
    
    # Create working directories
    mkdir -p {temp,output,backups}
    
    # Validate source files
    if [ ! -d "src" ] && [ ! -d "content" ] && [ ! -d "source" ]; then
        echo "❌ No source directory found"
        return 1
    fi
    
    echo "✅ Environment setup complete"
    return 0
}
```

### **Phase 2: Content Discovery and Preparation**
```bash
# Discover and organize source files
discover_content() {
    echo "📁 Discovering source content..."
    
    # Find source files based on project type
    local source_patterns=("*.md" "*.py" "*.js" "*.txt")  # Customize per project
    
    # Create file inventory
    > file-inventory.txt
    for pattern in "${source_patterns[@]}"; do
        find . -name "$pattern" -type f >> file-inventory.txt
    done
    
    local file_count=$(wc -l < file-inventory.txt)
    echo "📊 Found $file_count source files"
    
    # Validate file accessibility
    while read -r file; do
        if [ ! -r "$file" ]; then
            echo "❌ Cannot read file: $file"
            return 1
        fi
    done < file-inventory.txt
    
    echo "✅ Content discovery complete"
    return 0
}
```

### **Phase 3: Processing Pipeline**
```bash
# Core processing operations
process_content() {
    echo "⚙️ Processing content..."
    
    # Create safe working copy
    rm -rf temp/working
    mkdir -p temp/working
    
    # Process each file
    while read -r source_file; do
        local temp_file="temp/working/$(basename "$source_file")"
        
        echo "Processing: $source_file"
        
        # Copy to working directory
        cp "$source_file" "$temp_file"
        
        # Apply project-specific transformations
        if ! process_single_file "$temp_file"; then
            echo "❌ Processing failed for: $source_file"
            return 1
        fi
        
        echo "✅ Processed: $(basename "$source_file")"
    done < file-inventory.txt
    
    echo "✅ Content processing complete"
    return 0
}

# Template for single file processing
process_single_file() {
    local file="$1"
    
    # Example transformations (customize per project)
    # sed -i 's/old_pattern/new_pattern/g' "$file"
    # python preprocess.py "$file"
    # validate_file_syntax "$file"
    
    return 0
}
```

### **Phase 4: Output Generation**
```bash
# Generate final output
generate_output() {
    local output_format="${1:-default}"
    echo "📤 Generating output format: $output_format"
    
    case "$output_format" in
        "html")
            generate_html_output
            ;;
        "pdf")
            generate_pdf_output
            ;;
        "package")
            generate_package_output
            ;;
        *)
            echo "❌ Unknown output format: $output_format"
            return 1
            ;;
    esac
    
    return 0
}

# Example output generators (customize per project)
generate_html_output() {
    echo "Generating HTML output..."
    # Implementation depends on project type
    # pandoc temp/combined.md -o output/index.html
    # python generate_html.py temp/working output/
}

generate_pdf_output() {
    echo "Generating PDF output..."
    # Implementation depends on project type
    # pandoc temp/combined.md -o output/document.pdf
}
```

### **Phase 5: Quality Assurance**
```bash
# Validate generated output
validate_output() {
    echo "🔍 Validating output..."
    
    # Check output files exist
    if [ ! -d "output" ] || [ -z "$(ls -A output)" ]; then
        echo "❌ No output files generated"
        return 1
    fi
    
    # Validate each output file
    for output_file in output/*; do
        if [ -f "$output_file" ]; then
            echo "Validating: $(basename "$output_file")"
            
            # Check file size
            local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file")
            if [ "$file_size" -lt 100 ]; then
                echo "❌ Output file suspiciously small: $file_size bytes"
                return 1
            fi
            
            # Format-specific validation
            if ! validate_output_format "$output_file"; then
                echo "❌ Format validation failed for: $(basename "$output_file")"
                return 1
            fi
            
            echo "✅ Valid: $(basename "$output_file")"
        fi
    done
    
    echo "✅ Output validation complete"
    return 0
}

validate_output_format() {
    local file="$1"
    
    case "${file##*.}" in
        "html")
            # Basic HTML validation
            grep -q "<html>" "$file" || return 1
            ;;
        "pdf")
            # Basic PDF validation (if tools available)
            if command -v pdfinfo >/dev/null; then
                pdfinfo "$file" >/dev/null || return 1
            fi
            ;;
        "mp4"|"avi"|"mov")
            # Basic video validation (if tools available)
            if command -v ffprobe >/dev/null; then
                ffprobe -v quiet "$file" || return 1
            fi
            ;;
    esac
    
    return 0
}
```

---

## 🛠️ SPECIALIZED PROCESSING PATTERNS

### **Compilation-Based Workflows**
```bash
# For projects requiring compilation (code, documentation, media)
compilation_workflow() {
    echo "⚙️ Starting compilation workflow..."
    
    # Pre-compilation validation
    validate_source_files || return 1
    
    # Incremental compilation
    while read -r source_file; do
        local output_file="output/$(basename "$source_file" .ext).compiled"
        
        # Check if recompilation needed
        if [ "$source_file" -nt "$output_file" ]; then
            echo "Compiling: $source_file"
            if ! compile_single_file "$source_file" "$output_file"; then
                echo "❌ Compilation failed: $source_file"
                return 1
            fi
        else
            echo "✅ Up to date: $source_file"
        fi
    done < file-inventory.txt
    
    # Post-compilation validation
    validate_compiled_output || return 1
    
    echo "✅ Compilation workflow complete"
}

compile_single_file() {
    local source="$1"
    local output="$2"
    
    # Project-specific compilation logic
    # Examples:
    # gcc "$source" -o "$output"
    # python compile.py "$source" "$output"
    # pandoc "$source" -o "$output"
    
    return 0
}
```

### **Testing Integration Workflows**
```bash
# For projects requiring testing at each step
testing_workflow() {
    echo "🧪 Starting testing workflow..."
    
    # Run tests at each processing stage
    local test_stages=("setup" "processing" "output" "integration")
    
    for stage in "${test_stages[@]}"; do
        echo "Testing stage: $stage"
        if ! run_stage_tests "$stage"; then
            echo "❌ Tests failed at stage: $stage"
            return 1
        fi
        echo "✅ Tests passed: $stage"
    done
    
    echo "✅ All tests passed"
}

run_stage_tests() {
    local stage="$1"
    
    case "$stage" in
        "setup")
            test_environment_ready
            ;;
        "processing")
            test_processing_correctness
            ;;
        "output")
            test_output_quality
            ;;
        "integration")
            test_end_to_end_workflow
            ;;
    esac
}
```

### **Content Transformation Workflows**
```bash
# For projects requiring content transformation
transformation_workflow() {
    echo "🔄 Starting transformation workflow..."
    
    # Define transformation pipeline
    local transformations=("normalize" "enhance" "convert" "optimize")
    
    # Apply transformations in sequence
    for transform in "${transformations[@]}"; do
        echo "Applying transformation: $transform"
        if ! apply_transformation "$transform"; then
            echo "❌ Transformation failed: $transform"
            return 1
        fi
        
        # Validate after each transformation
        if ! validate_transformation_result "$transform"; then
            echo "❌ Validation failed after: $transform"
            return 1
        fi
        
        echo "✅ Transformation complete: $transform"
    done
    
    echo "✅ Transformation workflow complete"
}

apply_transformation() {
    local transform_type="$1"
    
    case "$transform_type" in
        "normalize")
            normalize_content
            ;;
        "enhance")
            enhance_content
            ;;
        "convert")
            convert_content_format
            ;;
        "optimize")
            optimize_content
            ;;
    esac
}
```

---

## 🚀 MASTER ORCHESTRATION SYSTEM

### **Universal Build Script Template**
```bash
#!/bin/bash
# universal-build.sh - Adaptable build orchestration

set -e  # Exit on any error

# Configuration (customize per project)
PROJECT_NAME="${PROJECT_NAME:-UniversalProject}"
SOURCE_DIR="${SOURCE_DIR:-src}"
OUTPUT_DIR="${OUTPUT_DIR:-output}"
TEMP_DIR="${TEMP_DIR:-temp}"
BUILD_TYPE="${1:-default}"

# Main orchestration function
main() {
    echo "=== Universal Build System ==="
    echo "Project: $PROJECT_NAME"
    echo "Build Type: $BUILD_TYPE"
    echo "Source: $SOURCE_DIR"
    echo "Output: $OUTPUT_DIR"
    echo ""
    
    # Execute build pipeline
    setup_environment || exit_with_error "Environment setup failed"
    discover_content || exit_with_error "Content discovery failed"
    process_content || exit_with_error "Content processing failed"
    generate_output "$BUILD_TYPE" || exit_with_error "Output generation failed"
    validate_output || exit_with_error "Output validation failed"
    cleanup_and_report || exit_with_error "Cleanup failed"
    
    echo "🎉 Build completed successfully!"
    show_results
}

# Error handling and cleanup
exit_with_error() {
    local error_msg="$1"
    echo "❌ BUILD FAILED: $error_msg"
    
    # Preserve debug information
    if [ -d "$TEMP_DIR" ]; then
        local debug_dir="debug-$(date +%Y%m%d-%H%M%S)"
        mv "$TEMP_DIR" "$debug_dir"
        echo "🔍 Debug information preserved in: $debug_dir"
    fi
    
    exit 1
}

cleanup_and_report() {
    echo "🧹 Cleaning up temporary files..."
    
    # Remove temp files but preserve output
    rm -rf "$TEMP_DIR"
    
    # Generate build report
    generate_build_report
    
    echo "✅ Cleanup complete"
}

show_results() {
    echo ""
    echo "📊 Build Results:"
    echo "=================="
    
    # Show output files
    if [ -d "$OUTPUT_DIR" ]; then
        echo "Generated files:"
        ls -lh "$OUTPUT_DIR"
    fi
    
    # Show build statistics
    echo ""
    echo "Build completed at: $(date)"
    echo "Total build time: $SECONDS seconds"
}

generate_build_report() {
    local report_file="$OUTPUT_DIR/build-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" <<EOF
Build Report
============
Project: $PROJECT_NAME
Build Type: $BUILD_TYPE
Date: $(date)
Duration: $SECONDS seconds

Source Directory: $SOURCE_DIR
Output Directory: $OUTPUT_DIR

Generated Files:
$(ls -la "$OUTPUT_DIR" 2>/dev/null || echo "No files generated")

Build Status: SUCCESS
EOF
    
    echo "📄 Build report: $report_file"
}

# Execute main function
main "$@"
```

---

## 🔧 WORKFLOW CUSTOMIZATION PATTERNS

### **For Development Projects**
```bash
# Emphasis on testing, compilation, and debugging
development_workflow() {
    setup_dev_environment
    run_linting_and_style_checks
    compile_or_build_project
    run_unit_tests
    run_integration_tests
    generate_documentation
    package_for_distribution
}
```

### **For Content Projects**
```bash
# Emphasis on content quality, formatting, and publishing
content_workflow() {
    validate_content_sources
    apply_content_transformations
    generate_multiple_output_formats
    validate_content_quality
    optimize_for_distribution
    create_content_packages
}
```

### **For Media Projects**
```bash
# Emphasis on media processing, encoding, and quality
media_workflow() {
    validate_media_sources
    apply_media_transformations
    encode_multiple_formats
    validate_media_quality
    optimize_file_sizes
    generate_preview_versions
}
```

---

## 📊 PERFORMANCE MONITORING AND OPTIMIZATION

### **Build Performance Tracking**
```bash
# Monitor build performance
monitor_performance() {
    local start_time=$(date +%s)
    local start_memory=$(free -m | awk 'NR==2{print $3}')
    
    # Execute monitored operation
    "$@"
    local exit_code=$?
    
    local end_time=$(date +%s)
    local end_memory=$(free -m | awk 'NR==2{print $3}')
    
    # Report performance
    local duration=$((end_time - start_time))
    local memory_used=$((end_memory - start_memory))
    
    echo "🔧 Performance: ${duration}s, ${memory_used}MB"
    
    return $exit_code
}

# Usage: monitor_performance some_expensive_operation
```

### **Parallel Processing Support**
```bash
# Process files in parallel for better performance
parallel_process() {
    local file_list="$1"
    local max_jobs="${2:-4}"
    
    # Function to process single file
    process_single() {
        local file="$1"
        echo "Processing: $file"
        process_single_file "$file"
        echo "✅ Completed: $file"
    }
    
    # Export function for parallel execution
    export -f process_single
    export -f process_single_file
    
    # Process files in parallel
    cat "$file_list" | xargs -n 1 -P "$max_jobs" -I {} bash -c 'process_single "$@"' _ {}
}
```

---

## 🔄 ADAPTATION GUIDELINES

### **Quick Adaptation Checklist**
1. **Customize file patterns** in `discover_content()`
2. **Modify processing logic** in `process_single_file()`
3. **Add output formats** in `generate_output()`
4. **Update validation rules** in `validate_output_format()`
5. **Configure environment requirements** in `setup_environment()`

### **Project-Specific Customizations**
- **Programming Projects**: Add compilation, testing, linting steps
- **Documentation Projects**: Add content validation, multiple format generation
- **Media Projects**: Add encoding, transcoding, quality optimization
- **Data Projects**: Add analysis, transformation, validation steps

---

**These build and processing workflows provide a systematic foundation for automating project operations while maintaining quality, safety, and repeatability across different project types and requirements.**