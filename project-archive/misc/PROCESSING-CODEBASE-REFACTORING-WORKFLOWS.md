# PROCESSING CODEBASE REFACTORING WORKFLOWS

**Purpose**: Comprehensive protocols for ingesting, analyzing, and refactoring Processing codebases with compilation requirements  
**Extracted From**: Permut8 Documentation Project session management, audit protocols, and build workflows  
**Application**: Any code refactoring project requiring iterative compilation, testing, and validation

---

## 🎯 PROJECT OVERVIEW

### **Unique Processing Project Characteristics**
- **Processing Language**: Java-based creative coding environment
- **Visual/Interactive Output**: Real-time graphics and interaction
- **Compilation Required**: Each edit needs compilation testing (unless AI can validate)
- **Reference Documentation Integration**: Existing docs must be preserved and integrated
- **Iterative Workflow**: Edit → Compile → Test → Validate cycle

### **Key Challenges**
- **Compilation Dependencies**: Processing IDE and library requirements
- **Visual Validation**: Output needs visual/interactive testing
- **Reference Doc Preservation**: Existing documentation must remain intact
- **Change Impact Assessment**: Understanding ripple effects across codebase

---

## 🔄 CORE SESSION MANAGEMENT PROTOCOLS

### **1. SESSION RECOVERY COMMAND (Processing Projects)**
```
Processing project session recovery: TodoRead + Read PROCESSING-PROJECT-STATUS.md + Read CODEBASE-ANALYSIS-TRACKER.md + Read [LATEST_SESSION_LOG] + Task "find most recent compilation results"
```

### **2. SESSION STARTUP CHECKLIST**
```markdown
## Processing Project Session Startup

### Context Recovery
- [ ] Read project status tracker for current phase
- [ ] Check compilation environment status
- [ ] Review last successful compilation results
- [ ] Identify current refactoring target
- [ ] Verify backup integrity

### Environment Validation
- [ ] Processing IDE available and functional
- [ ] Required libraries accessible
- [ ] Reference documentation location confirmed
- [ ] Backup systems operational
- [ ] Working copy isolated from originals

### Task Continuity
- [ ] Current todo status reviewed
- [ ] Next compilation target identified
- [ ] Change impact assessment updated
- [ ] Risk assessment for current changes reviewed
```

### **3. PROCESSING-SPECIFIC SESSION LOG TEMPLATE**
```markdown
# Session [Date]: Processing Refactoring - [Component]

## Compilation Environment
- **Processing Version**: [Version]
- **Libraries**: [Required libraries]
- **Last Successful Build**: [Timestamp]
- **Current Target**: [File/component being refactored]

## Work Completed
### [Timestamp] - [Refactoring Task]
- **Files Modified**: [List]
- **Compilation Status**: [SUCCESS/FAILED/UNTESTED]
- **Visual Output**: [Description of behavior changes]
- **Performance Impact**: [Notes on performance]

## Current Status
- **Compilation State**: [Working/Broken/Unknown]
- **Next Target**: [Specific next file/function]
- **Blocking Issues**: [Any compilation or logic problems]

## Handoff Notes
**For next session**: [Specific instructions]
**Compilation Notes**: [Build environment specifics]
**Visual Validation Required**: [What needs testing]
```

---

## 📋 CODEBASE INGESTION FRAMEWORK

### **Phase 1: Initial Codebase Analysis (Session 1)**

#### **Step 1: Environment Assessment**
```bash
# Processing environment validation
check_processing_environment() {
    echo "🔍 Validating Processing environment..."
    
    # Check Processing IDE
    if command -v processing-java >/dev/null; then
        echo "✅ Processing command line available"
        processing-java --version
    else
        echo "⚠️ Processing command line not found"
        echo "   Manual compilation required"
    fi
    
    # Check for sketch files
    local sketch_count=$(find . -name "*.pde" | wc -l)
    echo "📊 Found $sketch_count Processing sketch files"
    
    # Check for reference docs
    if [ -d "docs" ] || [ -d "documentation" ] || [ -f "README.md" ]; then
        echo "✅ Reference documentation found"
    else
        echo "⚠️ No obvious reference documentation"
    fi
}
```

#### **Step 2: Codebase Structure Discovery**
```bash
# Analyze Processing project structure
analyze_processing_structure() {
    echo "📁 Analyzing Processing project structure..."
    
    # Create structure inventory
    cat > codebase-structure.md <<EOF
# Processing Codebase Structure Analysis

**Analysis Date**: $(date)

## File Inventory
EOF
    
    # Main sketch files
    echo "### Main Sketch Files (.pde)" >> codebase-structure.md
    find . -name "*.pde" | sort | sed 's/^/- /' >> codebase-structure.md
    
    # Java source files
    echo "" >> codebase-structure.md
    echo "### Java Source Files (.java)" >> codebase-structure.md
    find . -name "*.java" | sort | sed 's/^/- /' >> codebase-structure.md
    
    # Data files
    echo "" >> codebase-structure.md
    echo "### Data Files" >> codebase-structure.md
    find . -path "*/data/*" | sort | sed 's/^/- /' >> codebase-structure.md
    
    # Documentation
    echo "" >> codebase-structure.md
    echo "### Documentation" >> codebase-structure.md
    find . -name "*.md" -o -name "*.txt" -o -name "*.pdf" | sort | sed 's/^/- /' >> codebase-structure.md
    
    echo "✅ Structure analysis saved to codebase-structure.md"
}
```

#### **Step 3: Dependency Mapping**
```bash
# Map Processing library dependencies
map_processing_dependencies() {
    echo "🔗 Mapping Processing dependencies..."
    
    # Look for import statements
    echo "# Processing Dependencies Analysis" > dependencies.md
    echo "" >> dependencies.md
    echo "**Analysis Date**: $(date)" >> dependencies.md
    echo "" >> dependencies.md
    
    # Core Processing imports
    echo "## Core Processing Libraries" >> dependencies.md
    grep -r "import.*processing\." . --include="*.pde" --include="*.java" | \
        sort | uniq | sed 's/^/- /' >> dependencies.md
    
    # External libraries
    echo "" >> dependencies.md
    echo "## External Libraries" >> dependencies.md
    grep -r "^import" . --include="*.pde" --include="*.java" | \
        grep -v "processing\." | sort | uniq | sed 's/^/- /' >> dependencies.md
    
    echo "✅ Dependencies mapped to dependencies.md"
}
```

### **Phase 2: Safety Infrastructure Setup**

#### **Step 1: Create Protected Working Environment**
```bash
# Set up safe Processing refactoring environment
setup_processing_safety() {
    echo "🛡️ Setting up Processing refactoring safety infrastructure..."
    
    # Create working copy
    if [ ! -d "refactoring-workspace" ]; then
        echo "Creating protected working copy..."
        cp -r . refactoring-workspace/
        
        # Mark as working copy
        cat > refactoring-workspace/WORKING-COPY-INFO.md <<EOF
# Processing Refactoring Working Copy

**Created**: $(date)
**Purpose**: Safe refactoring environment for Processing codebase
**Safety Level**: COPY-MODIFY (originals protected)

## Important Notes
- Original Processing sketches preserved in parent directory
- All refactoring happens in this workspace only
- Compilation testing safe - no risk to originals
- Reference documentation preserved unchanged

## Compilation Testing
Processing sketches can be safely compiled and tested in this workspace.
Original functionality preserved until changes are explicitly approved.
EOF
    fi
    
    # Create backup of reference docs
    if [ -d "docs" ] || [ -d "documentation" ]; then
        echo "Backing up reference documentation..."
        mkdir -p backups/reference-docs-$(date +%Y%m%d)
        cp -r docs documentation README.md backups/reference-docs-$(date +%Y%m%d)/ 2>/dev/null || true
    fi
    
    echo "✅ Safe refactoring environment ready"
    echo "📁 Work in: refactoring-workspace/"
    echo "🛡️ Originals protected in parent directory"
}
```

#### **Step 2: Compilation Baseline**
```bash
# Establish compilation baseline
create_compilation_baseline() {
    echo "⚙️ Creating compilation baseline..."
    
    local workspace_dir="refactoring-workspace"
    local baseline_log="compilation-baseline-$(date +%Y%m%d-%H%M%S).log"
    
    cd "$workspace_dir"
    
    # Attempt to compile each sketch
    echo "# Processing Compilation Baseline" > "../$baseline_log"
    echo "**Created**: $(date)" >> "../$baseline_log"
    echo "" >> "../$baseline_log"
    
    find . -name "*.pde" | while read sketch; do
        local sketch_dir=$(dirname "$sketch")
        local sketch_name=$(basename "$sketch" .pde)
        
        echo "Testing compilation: $sketch" | tee -a "../$baseline_log"
        
        # Try compilation (method depends on Processing setup)
        if command -v processing-java >/dev/null; then
            if processing-java --sketch="$sketch_dir" --output="temp-build" --run 2>&1 | tee -a "../$baseline_log"; then
                echo "✅ COMPILE SUCCESS: $sketch" | tee -a "../$baseline_log"
            else
                echo "❌ COMPILE FAILED: $sketch" | tee -a "../$baseline_log"
            fi
        else
            echo "⚠️ Manual compilation required for: $sketch" | tee -a "../$baseline_log"
        fi
        
        echo "---" >> "../$baseline_log"
        rm -rf temp-build 2>/dev/null || true
    done
    
    cd ..
    echo "✅ Compilation baseline created: $baseline_log"
}
```

---

## 🔧 REFACTORING WORKFLOW PROTOCOLS

### **Iterative Refactoring Pattern**

#### **Single File Refactoring Cycle**
```bash
# Safe single-file refactoring with compilation validation
refactor_processing_file() {
    local target_file="$1"
    local refactor_description="$2"
    local workspace="refactoring-workspace"
    
    echo "🔧 Starting refactoring: $target_file"
    echo "📝 Goal: $refactor_description"
    
    # Pre-refactoring backup
    cp "$workspace/$target_file" "$workspace/$target_file.backup-$(date +%H%M%S)"
    
    # Document change
    cat >> refactoring-log.md <<EOF
## $(date): Refactoring $target_file
**Goal**: $refactor_description
**Pre-change backup**: $target_file.backup-$(date +%H%M%S)
EOF
    
    echo "✅ Ready for refactoring"
    echo "📂 Target file: $workspace/$target_file"
    echo "🛡️ Backup created"
    echo ""
    echo "Next steps:"
    echo "1. Edit $workspace/$target_file"
    echo "2. Test compilation with: test_compilation \"$target_file\""
    echo "3. Document results with: document_refactoring_result"
}

# Test compilation after refactoring
test_compilation() {
    local target_file="$1"
    local workspace="refactoring-workspace"
    local test_log="compilation-test-$(date +%H%M%S).log"
    
    echo "⚙️ Testing compilation after refactoring..."
    
    cd "$workspace"
    local sketch_dir=$(dirname "$target_file")
    local sketch_name=$(basename "$target_file" .pde)
    
    # Attempt compilation
    if command -v processing-java >/dev/null; then
        if processing-java --sketch="$sketch_dir" --output="temp-build" --run > "../$test_log" 2>&1; then
            echo "✅ COMPILATION SUCCESS"
            echo "📊 No compilation errors after refactoring"
            rm -rf temp-build
            cd ..
            return 0
        else
            echo "❌ COMPILATION FAILED"
            echo "📄 Error details in: $test_log"
            cd ..
            return 1
        fi
    else
        echo "⚠️ Manual compilation testing required"
        echo "📁 Test file: $workspace/$target_file"
        cd ..
        return 2
    fi
}

# Document refactoring outcome
document_refactoring_result() {
    local result_type="$1"
    local notes="$2"
    
    cat >> refactoring-log.md <<EOF
**Result**: $result_type
**Notes**: $notes
**Timestamp**: $(date)
---

EOF
    
    echo "📝 Refactoring result documented"
}
```

#### **Rollback and Recovery**
```bash
# Rollback failed refactoring
rollback_refactoring() {
    local target_file="$1"
    local workspace="refactoring-workspace"
    
    echo "↩️ Rolling back refactoring for: $target_file"
    
    # Find most recent backup
    local backup_file=$(ls -1t "$workspace/$target_file.backup-"* 2>/dev/null | head -1)
    
    if [ -n "$backup_file" ]; then
        cp "$backup_file" "$workspace/$target_file"
        echo "✅ Rollback successful"
        echo "📂 Restored from: $(basename "$backup_file")"
        
        # Document rollback
        cat >> refactoring-log.md <<EOF
## $(date): ROLLBACK $target_file
**Reason**: Compilation failure or validation issue
**Restored from**: $(basename "$backup_file")
---

EOF
    else
        echo "❌ No backup found for rollback"
        echo "⚠️ Manual recovery required"
    fi
}
```

### **Batch Refactoring Strategy**

#### **Progressive Refactoring Plan**
```bash
# Create systematic refactoring plan
create_refactoring_plan() {
    local focus_area="$1"
    
    echo "📋 Creating refactoring plan for: $focus_area"
    
    cat > refactoring-plan-$focus_area.md <<EOF
# Processing Refactoring Plan: $focus_area

**Created**: $(date)
**Focus Area**: $focus_area
**Strategy**: Progressive refactoring with compilation validation

## Refactoring Targets

### Phase 1: High-Priority Files
- [ ] File 1: [Description of changes needed]
- [ ] File 2: [Description of changes needed]

### Phase 2: Medium-Priority Files
- [ ] File 3: [Description of changes needed]
- [ ] File 4: [Description of changes needed]

### Phase 3: Low-Priority Files
- [ ] File 5: [Description of changes needed]

## Success Criteria
- [ ] All files compile successfully
- [ ] Visual output matches expected behavior
- [ ] Performance maintained or improved
- [ ] Reference documentation updated accordingly

## Risk Assessment
**High Risk**: [Files that might break compilation]
**Medium Risk**: [Files with complex dependencies]
**Low Risk**: [Isolated files or simple changes]

## Rollback Plan
Each file has backup created before modification.
Compilation testing after each change.
Immediate rollback on failure.
EOF
    
    echo "✅ Refactoring plan created: refactoring-plan-$focus_area.md"
}
```

---

## 📊 AUDIT AND QUALITY FRAMEWORKS (Processing-Adapted)

### **Processing Code Quality Assessment**

#### **Processing-Specific Audit Categories**
```markdown
## Processing Code Audit Framework

### Category 1: COMPILATION INTEGRITY (Weight: 40%)
- **Syntax Correctness**: Valid Processing/Java syntax
- **Library Dependencies**: Proper import statements and availability
- **Function Signatures**: Correct setup(), draw(), and event handlers
- **Variable Scope**: Proper global vs local variable usage
- **Memory Management**: Efficient array and object handling

### Category 2: VISUAL OUTPUT VALIDATION (Weight: 25%)
- **Rendering Correctness**: Expected visual output maintained
- **Performance**: Frame rate and responsiveness preserved
- **Interactive Elements**: Mouse, keyboard, and other inputs functional
- **Canvas Management**: Proper size, color modes, and transformations

### Category 3: CODE STRUCTURE (Weight: 20%)
- **Modularity**: Functions and classes properly organized
- **Readability**: Clear variable names and code structure
- **Comments**: Adequate documentation for complex logic
- **Processing Conventions**: Following Processing best practices

### Category 4: INTEGRATION INTEGRITY (Weight: 10%)
- **Cross-File Dependencies**: Proper handling of multiple tabs/files
- **Data File Access**: Correct loading of images, fonts, data files
- **Library Integration**: Proper use of external Processing libraries

### Category 5: DOCUMENTATION ALIGNMENT (Weight: 5%)
- **Reference Doc Accuracy**: Code matches documentation
- **Example Consistency**: Working examples that compile and run
- **Comment Updates**: Code comments reflect actual functionality
```

#### **Processing Light Audit Protocol (10-15 minutes)**
```bash
# Quick Processing sketch audit
audit_processing_sketch() {
    local sketch_file="$1"
    local audit_time_start=$(date +%s)
    
    echo "🔍 Auditing Processing sketch: $sketch_file"
    
    # Phase 1: Quick Syntax Check (3 minutes)
    echo "Phase 1: Syntax validation..."
    local syntax_issues=0
    
    # Check for common Processing syntax requirements
    if ! grep -q "void setup()" "$sketch_file"; then
        echo "⚠️ Missing setup() function"
        ((syntax_issues++))
    fi
    
    if ! grep -q "void draw()" "$sketch_file"; then
        echo "⚠️ Missing draw() function (may be intentional for static sketches)"
    fi
    
    # Check for unclosed braces, parentheses
    local open_braces=$(grep -o "{" "$sketch_file" | wc -l)
    local close_braces=$(grep -o "}" "$sketch_file" | wc -l)
    if [ "$open_braces" -ne "$close_braces" ]; then
        echo "❌ Mismatched braces: $open_braces open, $close_braces close"
        ((syntax_issues++))
    fi
    
    # Phase 2: Processing-Specific Validation (5 minutes)
    echo "Phase 2: Processing conventions..."
    local convention_issues=0
    
    # Check for proper size() call
    if grep -q "size(" "$sketch_file"; then
        if ! grep -q "size.*;" "$sketch_file"; then
            echo "⚠️ size() call may have syntax issues"
            ((convention_issues++))
        fi
    fi
    
    # Check for undefined variables (basic check)
    grep -o "\b[a-zA-Z_][a-zA-Z0-9_]*\b" "$sketch_file" | sort | uniq > temp_vars.txt
    # This would need more sophisticated analysis for actual undefined variables
    
    # Phase 3: Compilation Test (5-7 minutes)
    echo "Phase 3: Compilation test..."
    local compile_status="UNKNOWN"
    if command -v processing-java >/dev/null; then
        if test_compilation "$sketch_file"; then
            compile_status="PASS"
        else
            compile_status="FAIL"
            ((syntax_issues++))
        fi
    else
        compile_status="MANUAL_REQUIRED"
    fi
    
    # Generate audit result
    local audit_time_end=$(date +%s)
    local audit_duration=$((audit_time_end - audit_time_start))
    
    cat > "audit-$(basename "$sketch_file" .pde)-$(date +%Y%m%d-%H%M%S).md" <<EOF
# Processing Sketch Audit: $(basename "$sketch_file")

**Audit Date**: $(date)
**File**: $sketch_file
**Duration**: ${audit_duration}s
**Overall Status**: $([ $((syntax_issues + convention_issues)) -eq 0 ] && echo "PASS" || echo "NEEDS_REVIEW")

## Results Summary
- **Syntax Issues**: $syntax_issues
- **Convention Issues**: $convention_issues
- **Compilation**: $compile_status

## Detailed Findings
[Specific issues would be documented here]

## Recommendations
$([ $((syntax_issues + convention_issues)) -eq 0 ] && echo "✅ Sketch ready for refactoring" || echo "🔧 Address identified issues before refactoring")
EOF
    
    echo "✅ Audit completed in ${audit_duration}s"
    echo "📄 Report: audit-$(basename "$sketch_file" .pde)-$(date +%Y%m%d-%H%M%S).md"
    
    rm -f temp_vars.txt
}
```

---

## 🔗 REFERENCE DOCUMENTATION INTEGRATION

### **Documentation Preservation Strategy**

#### **Reference Doc Analysis and Integration**
```bash
# Analyze existing reference documentation
analyze_reference_docs() {
    echo "📖 Analyzing reference documentation..."
    
    # Create documentation inventory
    cat > reference-docs-analysis.md <<EOF
# Reference Documentation Analysis

**Analysis Date**: $(date)

## Documentation Inventory
EOF
    
    # Find all documentation files
    find . -name "*.md" -o -name "*.txt" -o -name "*.pdf" -o -name "*.html" | while read doc; do
        echo "### $(basename "$doc")" >> reference-docs-analysis.md
        echo "- **Path**: $doc" >> reference-docs-analysis.md
        echo "- **Size**: $(stat -f%z "$doc" 2>/dev/null || stat -c%s "$doc") bytes" >> reference-docs-analysis.md
        echo "- **Modified**: $(stat -f%Sm "$doc" 2>/dev/null || stat -c%y "$doc")" >> reference-docs-analysis.md
        
        # Basic content analysis for text files
        if [[ "$doc" == *.md ]] || [[ "$doc" == *.txt ]]; then
            local word_count=$(wc -w < "$doc")
            echo "- **Word Count**: $word_count" >> reference-docs-analysis.md
            
            # Look for code examples
            local code_blocks=$(grep -c "```" "$doc" 2>/dev/null || echo "0")
            echo "- **Code Blocks**: $((code_blocks / 2))" >> reference-docs-analysis.md
        fi
        
        echo "" >> reference-docs-analysis.md
    done
    
    echo "✅ Reference documentation analysis complete"
}

# Create documentation update tracking
track_doc_updates() {
    local code_file="$1"
    local doc_files="$2"
    
    echo "📝 Tracking documentation updates needed for: $code_file"
    
    cat >> doc-update-tracker.md <<EOF
## $(date): Code Changes Requiring Doc Updates

### Modified Code
**File**: $code_file
**Changes**: [To be documented]

### Documentation Files to Review
$(echo "$doc_files" | tr ',' '\n' | sed 's/^/- /')

### Update Requirements
- [ ] Review code examples in documentation
- [ ] Update function signatures if changed
- [ ] Verify screenshots still accurate
- [ ] Check cross-references and links

---
EOF
    
    echo "✅ Documentation update tracking added"
}
```

### **Documentation Synchronization**
```bash
# Synchronize code changes with documentation
sync_docs_with_code() {
    echo "🔄 Synchronizing documentation with code changes..."
    
    # Create documentation work plan
    cat > doc-sync-plan.md <<EOF
# Documentation Synchronization Plan

**Created**: $(date)
**Purpose**: Keep reference docs aligned with refactored code

## Synchronization Tasks

### Automated Checks
- [ ] Find code examples in documentation
- [ ] Extract function signatures from code
- [ ] Compare with documented signatures
- [ ] Identify mismatches

### Manual Review Required
- [ ] Visual elements (screenshots, diagrams)
- [ ] Conceptual explanations
- [ ] Tutorial completeness
- [ ] Cross-reference accuracy

## Documentation Files by Priority
### High Priority (Core API docs)
[List of critical documentation files]

### Medium Priority (Tutorials and guides)
[List of tutorial documentation]

### Low Priority (Supplementary materials)
[List of supplementary docs]
EOF
    
    echo "✅ Documentation sync plan created"
}
```

---

## 🚀 MASTER WORKFLOW ORCHESTRATION

### **Complete Processing Refactoring Session**
```bash
#!/bin/bash
# processing-refactoring-session.sh - Complete workflow orchestration

set -e

# Configuration
PROJECT_NAME="${1:-ProcessingRefactoring}"
SESSION_TYPE="${2:-analysis}"  # analysis, refactoring, documentation
FOCUS_AREA="${3:-all}"

# Main orchestration
main() {
    echo "=== Processing Codebase Refactoring Session ==="
    echo "Project: $PROJECT_NAME"
    echo "Session Type: $SESSION_TYPE"
    echo "Focus Area: $FOCUS_AREA"
    echo ""
    
    case "$SESSION_TYPE" in
        "analysis")
            run_analysis_session
            ;;
        "refactoring")
            run_refactoring_session
            ;;
        "documentation")
            run_documentation_session
            ;;
        "complete")
            run_complete_session
            ;;
        *)
            echo "❌ Unknown session type: $SESSION_TYPE"
            show_usage
            exit 1
            ;;
    esac
    
    echo "🎉 Session completed successfully!"
}

run_analysis_session() {
    echo "🔍 Running analysis session..."
    
    # Phase 1: Environment setup
    check_processing_environment
    setup_processing_safety
    
    # Phase 2: Codebase discovery
    analyze_processing_structure
    map_processing_dependencies
    create_compilation_baseline
    
    # Phase 3: Reference documentation
    analyze_reference_docs
    
    # Phase 4: Planning
    create_refactoring_plan "$FOCUS_AREA"
    
    echo "✅ Analysis session complete"
    echo "📄 Next steps documented in refactoring-plan-$FOCUS_AREA.md"
}

run_refactoring_session() {
    echo "🔧 Running refactoring session..."
    
    # Validate environment
    if [ ! -d "refactoring-workspace" ]; then
        echo "❌ Refactoring workspace not found. Run analysis session first."
        exit 1
    fi
    
    # Load refactoring plan
    if [ -f "refactoring-plan-$FOCUS_AREA.md" ]; then
        echo "📋 Loading refactoring plan for: $FOCUS_AREA"
    else
        echo "⚠️ No refactoring plan found. Creating basic plan..."
        create_refactoring_plan "$FOCUS_AREA"
    fi
    
    echo "✅ Refactoring session ready"
    echo "📁 Work in: refactoring-workspace/"
    echo "🔧 Use: refactor_processing_file <filename> <description>"
}

show_usage() {
    cat <<EOF
Usage: $0 [PROJECT_NAME] [SESSION_TYPE] [FOCUS_AREA]

SESSION_TYPES:
  analysis      - Initial codebase analysis and setup
  refactoring   - Interactive refactoring session
  documentation - Documentation synchronization
  complete      - Full analysis + refactoring + docs

FOCUS_AREAS:
  all          - Entire codebase
  core         - Core functionality only
  ui           - User interface components
  data         - Data processing components
  custom       - Custom focus area

Examples:
  $0 MyProject analysis all
  $0 MyProject refactoring core
  $0 MyProject documentation all
EOF
}

# Execute main function
main "$@"
```

---

## 📊 SUCCESS METRICS AND VALIDATION

### **Processing Project Success Criteria**
```markdown
## Processing Refactoring Success Metrics

### Technical Metrics
- **Compilation Success Rate**: 100% of sketches compile successfully
- **Performance Maintenance**: Frame rates maintained or improved
- **Visual Output Integrity**: All visual elements render correctly
- **Interactive Functionality**: All user interactions work as expected

### Code Quality Metrics
- **Readability Improvement**: Clear variable names and structure
- **Modularity Enhancement**: Better function and class organization
- **Comment Quality**: Adequate documentation for complex logic
- **Processing Best Practices**: Following Processing conventions

### Documentation Alignment
- **Reference Accuracy**: All code examples in docs work correctly
- **Completeness**: All functions and features documented
- **Synchronization**: Code changes reflected in documentation
- **Usability**: Documentation supports learning and implementation

### Project Management
- **Change Tracking**: All modifications documented with rationale
- **Safety Compliance**: Original files preserved throughout process
- **Recovery Capability**: Ability to rollback any problematic changes
- **Session Continuity**: Seamless work across multiple sessions
```

### **Validation Checklist**
```bash
# Final project validation
validate_processing_refactoring() {
    echo "✅ Final Processing refactoring validation..."
    
    local validation_report="validation-report-$(date +%Y%m%d).md"
    
    cat > "$validation_report" <<EOF
# Processing Refactoring Validation Report

**Generated**: $(date)
**Project**: $PROJECT_NAME

## Compilation Validation
EOF
    
    # Test all sketches compile
    local total_sketches=0
    local successful_compiles=0
    
    find refactoring-workspace -name "*.pde" | while read sketch; do
        ((total_sketches++))
        if test_compilation "$sketch"; then
            ((successful_compiles++))
        fi
    done
    
    echo "- **Total Sketches**: $total_sketches" >> "$validation_report"
    echo "- **Successful Compiles**: $successful_compiles" >> "$validation_report"
    echo "- **Success Rate**: $(($successful_compiles * 100 / $total_sketches))%" >> "$validation_report"
    
    # Additional validations...
    echo "📊 Validation report: $validation_report"
}
```

---

**Implementation Note**: This comprehensive workflow framework provides systematic protocols for Processing codebase refactoring projects that require compilation validation, reference documentation integration, and iterative development cycles. The framework emphasizes safety, continuity, and measurable progress while accommodating the unique requirements of visual/interactive coding environments.
