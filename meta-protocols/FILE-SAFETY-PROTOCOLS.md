# FILE SAFETY PROTOCOLS

**Purpose**: Universal file protection and backup strategies for any development project  
**Usage**: Prevent data loss, enable safe experimentation, provide recovery mechanisms  
**Extracted From**: Documentation Project safety practices and Processing refactoring workflows

---

## 🛡️ CORE SAFETY PRINCIPLES

### **1. PRESERVATION-FIRST APPROACH**
- **Original files are sacred** - Source files must remain untouched
- **Work on copies only** - All modifications happen in isolated environments
- **Explicit permission required** - Never delete or modify without clear approval
- **Backup before changes** - Create safety copies before any destructive operation

### **2. CHANGE MANAGEMENT HIERARCHY**
```
SAFETY LEVEL     | OPERATIONS ALLOWED           | APPROVAL REQUIRED
-----------------|------------------------------|------------------
READ-ONLY        | View, copy, analyze          | None
COPY-MODIFY      | Work on copies only          | User notification
BACKUP-MODIFY    | Modify with backup           | User approval
DIRECT-MODIFY    | Modify originals             | Explicit permission
DELETE           | Remove files                 | Double confirmation
```

### **3. INFRASTRUCTURE PROTECTION**
- **Session logs are historical records** - Never delete project history
- **Protocol documents are project infrastructure** - Preserve methodology
- **Configuration files maintain project state** - Essential for continuity

---

## 📁 BACKUP STRATEGY FRAMEWORK

### **Automated Backup Creation**
```bash
# Universal backup function
create_backup() {
    local source_path="$1"
    local backup_type="${2:-manual}"
    local reason="${3:-Standard backup procedure}"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_dir="backups/$backup_type-$timestamp"
    
    echo "🛡️ Creating $backup_type backup: $backup_dir"
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Copy files preserving structure
    if [ -d "$source_path" ]; then
        cp -r "$source_path" "$backup_dir/"
    elif [ -f "$source_path" ]; then
        cp "$source_path" "$backup_dir/"
    else
        echo "❌ Source path not found: $source_path"
        return 1
    fi
    
    # Create backup manifest
    cat > "$backup_dir/BACKUP-MANIFEST.md" <<EOF
# Backup Manifest

**Created**: $(date)
**Type**: $backup_type
**Source**: $source_path
**Reason**: $reason

## Contents
$(find "$backup_dir" -type f | grep -v BACKUP-MANIFEST.md | sort)

## Recovery Instructions
To restore this backup:
\`\`\`bash
cp -r $backup_dir/* $source_path/
\`\`\`

## File Checksums
$(find "$backup_dir" -type f | grep -v BACKUP-MANIFEST.md | xargs md5sum)
EOF
    
    echo "✅ Backup created: $backup_dir"
    return 0
}

# Backup before any major operation
backup_before_operation() {
    local operation_name="$1"
    local target_files="$2"
    
    echo "🛡️ Creating safety backup before: $operation_name"
    
    if ! create_backup "$target_files" "pre-$operation_name" "$operation_name"; then
        echo "❌ Backup failed - aborting operation"
        return 1
    fi
    
    return 0
}
```

### **Incremental Backup System**
```bash
# Maintain incremental backups with change tracking
create_incremental_backup() {
    local source_dir="$1"
    local backup_base="backups/incremental"
    local current_backup="$backup_base/$(date +%Y%m%d-%H%M%S)"
    local latest_link="$backup_base/latest"
    
    mkdir -p "$current_backup"
    
    # Create incremental backup using rsync
    if [ -L "$latest_link" ] && [ -d "$(readlink "$latest_link")" ]; then
        # Incremental backup
        rsync -av --link-dest="$(readlink "$latest_link")" "$source_dir/" "$current_backup/"
        echo "✅ Incremental backup created: $current_backup"
    else
        # Full backup (first time)
        rsync -av "$source_dir/" "$current_backup/"
        echo "✅ Full backup created: $current_backup"
    fi
    
    # Update latest symlink
    rm -f "$latest_link"
    ln -s "$(basename "$current_backup")" "$latest_link"
    
    # Create change summary
    if [ -L "$backup_base/previous" ]; then
        echo "## Changes since last backup:" > "$current_backup/CHANGES.md"
        diff -r "$(readlink "$backup_base/previous")" "$current_backup" >> "$current_backup/CHANGES.md" 2>/dev/null || true
    fi
    
    # Update previous link
    rm -f "$backup_base/previous"
    ln -s "$(basename "$current_backup")" "$backup_base/previous"
}
```

### **Project Snapshot System**
```bash
# Create complete project snapshots
create_project_snapshot() {
    local snapshot_name="${1:-$(date +%Y%m%d-%H%M%S)}"
    local snapshot_dir="snapshots/$snapshot_name"
    
    echo "📸 Creating project snapshot: $snapshot_name"
    
    mkdir -p "$snapshot_dir"
    
    # Copy all project files except temporary and output directories
    rsync -av \
        --exclude 'temp/' \
        --exclude 'output/' \
        --exclude '.git/' \
        --exclude 'node_modules/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        . "$snapshot_dir/"
    
    # Create snapshot metadata
    cat > "$snapshot_dir/SNAPSHOT-INFO.md" <<EOF
# Project Snapshot: $snapshot_name

**Created**: $(date)
**Git Commit**: $(git rev-parse HEAD 2>/dev/null || echo "No git repository")
**Git Status**: $(git status --porcelain 2>/dev/null || echo "No git repository")

## Project State
- **Last Modified Files**: $(find . -type f -name "*.py" -o -name "*.js" -o -name "*.md" | head -10 | xargs ls -lt | head -5)

## Environment
- **OS**: $(uname -s)
- **Working Directory**: $(pwd)
- **User**: $(whoami)
EOF
    
    echo "✅ Project snapshot created: $snapshot_dir"
}
```

---

## 🔒 SAFE WORKING COPY STRATEGIES

### **Isolated Working Environment Creation**
```bash
# Create protected working copy for modifications
create_working_copy() {
    local source_dir="$1"
    local work_dir="${2:-working-copy}"
    local operation="${3:-modification}"
    
    echo "🛡️ Creating safe working copy for: $operation"
    
    # Remove any existing working copy
    if [ -d "$work_dir" ]; then
        echo "Removing previous working copy..."
        rm -rf "$work_dir"
    fi
    
    # Create fresh working copy
    mkdir -p "$(dirname "$work_dir")"
    cp -r "$source_dir" "$work_dir"
    
    # Create working copy information
    cat > "$work_dir/WORKING-COPY-INFO.md" <<EOF
# Working Copy Information

**Created**: $(date)
**Source**: $source_dir
**Purpose**: $operation
**Safety Level**: COPY-MODIFY

## Important Notes
- This is a WORKING COPY - original files are preserved
- All modifications happen in this directory only
- Original files remain untouched at: $source_dir
- Changes can be safely tested without risk

## Original File Protection
Original files are protected and will not be modified.
To apply changes to originals, explicit approval is required.

## Working Copy Validation
To verify working copy integrity:
\`\`\`bash
diff -r "$source_dir" "$work_dir"
\`\`\`
EOF
    
    echo "✅ Working copy created: $work_dir"
    echo "🛡️ Original files protected at: $source_dir"
    return 0
}

# Validate working copy isolation
validate_copy_isolation() {
    local work_dir="$1"
    local source_dir="$2"
    
    # Check that working copy exists
    if [ ! -d "$work_dir" ]; then
        echo "❌ Working copy not found: $work_dir"
        return 1
    fi
    
    # Create comparison report
    echo "🔍 Validating working copy isolation..."
    
    if diff -r "$source_dir" "$work_dir" > temp-diff.txt 2>&1; then
        echo "📋 Working copy identical to source (no changes yet)"
        rm temp-diff.txt
    else
        echo "⚠️ Working copy has been modified (expected for active work)"
        echo "✅ Original files remain protected"
        
        # Show summary of changes
        echo "📊 Change summary:"
        wc -l temp-diff.txt
        rm temp-diff.txt
    fi
    
    return 0
}
```

### **Change Application with Approval Protocol**
```bash
# Apply changes from working copy to originals with user approval
request_change_approval() {
    local work_dir="$1"
    local source_dir="$2"
    local change_description="$3"
    
    echo "🔄 Requesting approval to apply changes..."
    echo ""
    echo "📋 Change Summary:"
    echo "   Source: $source_dir"
    echo "   Working Copy: $work_dir"
    echo "   Description: $change_description"
    echo ""
    
    # Generate detailed change report
    local change_report="pending-changes-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$change_report" <<EOF
CHANGE APPROVAL REQUEST
======================
Date: $(date)
Source Directory: $source_dir
Working Copy: $work_dir
Description: $change_description

DETAILED CHANGES:
EOF
    
    # Add diff to report
    diff -r "$source_dir" "$work_dir" >> "$change_report" 2>&1 || true
    
    echo "📊 Detailed change report generated: $change_report"
    echo ""
    echo "⚠️ MANUAL APPROVAL REQUIRED:"
    echo "   Review changes in: $change_report"
    echo "   To approve: apply_approved_changes \"$work_dir\" \"$source_dir\" \"APPROVED\""
    echo "   To reject: cleanup_working_copy \"$work_dir\""
    
    # Log the approval request
    cat >> "approval-requests.log" <<EOF
$(date): APPROVAL REQUIRED
Operation: Apply changes to original files
Source: $source_dir
Working Copy: $work_dir
Description: $change_description
Change Report: $change_report
Status: PENDING MANUAL REVIEW
---
EOF
    
    return 1  # Return error to halt automated processing
}

# Apply pre-approved changes
apply_approved_changes() {
    local work_dir="$1"
    local source_dir="$2"
    local approval_code="$3"
    
    # Verify approval code
    if [ "$approval_code" != "APPROVED" ]; then
        echo "❌ Invalid approval code. Changes not applied."
        echo "   Required approval code: APPROVED"
        echo "   Provided: $approval_code"
        return 1
    fi
    
    # Create final backup before applying changes
    if ! backup_before_operation "change-application" "$source_dir"; then
        echo "❌ Pre-change backup failed. Changes not applied."
        return 1
    fi
    
    # Apply changes using rsync for safety
    echo "✅ Applying approved changes..."
    rsync -av --delete "$work_dir/" "$source_dir/"
    
    # Verify changes applied correctly
    if diff -r "$source_dir" "$work_dir" >/dev/null 2>&1; then
        echo "✅ Changes successfully applied to original files"
        echo "🛡️ Backup available in backups/ directory"
        
        # Log successful application
        echo "$(date): Changes successfully applied from $work_dir to $source_dir" >> "change-application.log"
        
        # Clean up working copy
        rm -rf "$work_dir"
        echo "🧹 Working copy cleaned up"
        
        return 0
    else
        echo "❌ Change application verification failed"
        echo "⚠️ Check file integrity manually"
        return 1
    fi
}

# Clean up working copy without applying changes
cleanup_working_copy() {
    local work_dir="$1"
    
    if [ -d "$work_dir" ]; then
        echo "🧹 Cleaning up working copy: $work_dir"
        rm -rf "$work_dir"
        echo "✅ Working copy removed (changes discarded)"
    else
        echo "⚠️ Working copy not found: $work_dir"
    fi
    
    return 0
}
```

---

## 📋 CHANGE TRACKING AND AUDIT TRAIL

### **File Modification Documentation**
```bash
# Document all file modifications with audit trail
document_file_change() {
    local file_path="$1"
    local change_type="$2"
    local description="$3"
    local user="${4:-$(whoami)}"
    
    local audit_log="file-changes-audit.log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get file information
    local file_size_before="N/A"
    local file_size_after="N/A"
    local checksum_after="N/A"
    
    if [ -f "$file_path.backup" ]; then
        file_size_before=$(stat -f%z "$file_path.backup" 2>/dev/null || stat -c%s "$file_path.backup" 2>/dev/null || echo "N/A")
    fi
    
    if [ -f "$file_path" ]; then
        file_size_after=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null || echo "N/A")
        checksum_after=$(md5sum "$file_path" 2>/dev/null | cut -d' ' -f1 || echo "N/A")
    fi
    
    # Create audit entry
    cat >> "$audit_log" <<EOF
[$timestamp] $change_type: $file_path
User: $user
Description: $description
Size Before: $file_size_before bytes
Size After: $file_size_after bytes
Checksum: $checksum_after
---
EOF
    
    echo "📝 Change documented in audit log"
}

# Generate change summary report
generate_change_summary() {
    local start_date="${1:-$(date -d '1 week ago' '+%Y-%m-%d' 2>/dev/null || date -v-7d '+%Y-%m-%d' 2>/dev/null || echo '1970-01-01')}"
    local end_date="${2:-$(date '+%Y-%m-%d')}"
    local report_file="change-summary-$(date +%Y%m%d).md"
    
    cat > "$report_file" <<EOF
# File Change Summary Report

**Period**: $start_date to $end_date
**Generated**: $(date)

## Change Statistics
EOF
    
    # Count changes by type
    if [ -f "file-changes-audit.log" ]; then
        grep "^\[" file-changes-audit.log | \
        awk -v start="$start_date" -v end="$end_date" '
        $1 >= "[" start && $1 <= "[" end {
            split($3, parts, ":")
            change_type = parts[1]
            counts[change_type]++
            total++
        }
        END {
            for (type in counts) {
                print "- " type ": " counts[type] " changes"
            }
            print "- **Total**: " total " changes"
        }' >> "$report_file"
    else
        echo "- No change audit log found" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## Recent Changes" >> "$report_file"
    
    # Add recent changes
    if [ -f "file-changes-audit.log" ]; then
        tail -20 file-changes-audit.log >> "$report_file"
    fi
    
    echo "📊 Change summary generated: $report_file"
}
```

### **File Integrity Monitoring**
```bash
# Create file integrity baseline
create_integrity_baseline() {
    local directory="$1"
    local baseline_file="integrity-baseline.txt"
    
    echo "🔍 Creating integrity baseline for: $directory"
    
    # Generate checksums for all files
    find "$directory" -type f -exec md5sum {} \; | sort > "$baseline_file"
    
    local file_count=$(wc -l < "$baseline_file")
    echo "✅ Integrity baseline created: $baseline_file"
    echo "📊 Monitoring $file_count files"
    
    # Create baseline metadata
    cat > "integrity-baseline-info.txt" <<EOF
Integrity Baseline Information
==============================
Created: $(date)
Directory: $directory
Files Monitored: $file_count
Baseline File: $baseline_file

To check integrity:
  check_file_integrity "$directory"

To update baseline:
  create_integrity_baseline "$directory"
EOF
    
    return 0
}

# Check for file integrity violations
check_file_integrity() {
    local directory="$1"
    local baseline_file="integrity-baseline.txt"
    local violations_file="integrity-violations-$(date +%Y%m%d-%H%M%S).txt"
    
    if [ ! -f "$baseline_file" ]; then
        echo "❌ No integrity baseline found. Run create_integrity_baseline first."
        return 1
    fi
    
    echo "🔍 Checking file integrity against baseline..."
    
    # Generate current checksums
    find "$directory" -type f -exec md5sum {} \; | sort > temp-checksums.txt
    
    # Compare with baseline
    if diff "$baseline_file" temp-checksums.txt > "$violations_file" 2>&1; then
        echo "✅ File integrity verified - no violations detected"
        rm temp-checksums.txt "$violations_file"
        return 0
    else
        echo "⚠️ Integrity violations detected!"
        echo "📄 Details saved to: $violations_file"
        
        # Show summary of violations
        echo ""
        echo "Modified files:"
        grep "^>" "$violations_file" | cut -c3- | cut -d' ' -f2- | head -10
        
        local violation_count=$(grep -c "^>" "$violations_file")
        echo "Total violations: $violation_count"
        
        rm temp-checksums.txt
        return 1
    fi
}
```

---

## 🚨 EMERGENCY RECOVERY PROCEDURES

### **Automated Recovery Functions**
```bash
# Emergency recovery from most recent backup
emergency_restore() {
    local recovery_type="${1:-latest}"
    
    echo "🚨 Initiating emergency recovery: $recovery_type"
    
    case "$recovery_type" in
        "latest")
            restore_from_latest_backup
            ;;
        "incremental")
            restore_from_incremental_backup
            ;;
        "snapshot")
            restore_from_snapshot
            ;;
        *)
            echo "❌ Unknown recovery type: $recovery_type"
            echo "Available types: latest, incremental, snapshot"
            return 1
            ;;
    esac
}

restore_from_latest_backup() {
    # Find most recent backup
    local latest_backup=$(find backups/ -type d -name "*-*" | sort | tail -1)
    
    if [ -z "$latest_backup" ]; then
        echo "❌ No backups found for recovery"
        return 1
    fi
    
    echo "📁 Latest backup found: $latest_backup"
    echo "⚠️ This will restore files from backup"
    echo "   Current files will be moved to emergency-backup-$(date +%Y%m%d-%H%M%S)/"
    echo ""
    echo "🛑 MANUAL CONFIRMATION REQUIRED"
    echo "   To proceed: confirm_emergency_restore \"$latest_backup\""
    
    return 1  # Require manual confirmation
}

confirm_emergency_restore() {
    local backup_path="$1"
    local confirmation="${2:-}"
    
    if [ "$confirmation" != "CONFIRMED" ]; then
        echo "❌ Emergency restore requires explicit confirmation"
        echo "   Usage: confirm_emergency_restore \"$backup_path\" \"CONFIRMED\""
        return 1
    fi
    
    # Move current files to emergency backup
    local emergency_backup="emergency-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$emergency_backup"
    
    # Identify what needs to be backed up
    local backup_manifest="$backup_path/BACKUP-MANIFEST.md"
    if [ -f "$backup_manifest" ]; then
        # Extract original source path from manifest
        local original_source=$(grep "^Source:" "$backup_manifest" | cut -d' ' -f2-)
        if [ -d "$original_source" ]; then
            echo "🛡️ Moving current files to: $emergency_backup"
            mv "$original_source" "$emergency_backup/"
        fi
    fi
    
    # Restore from backup
    echo "📂 Restoring from backup: $backup_path"
    cp -r "$backup_path"/* ./
    
    echo "✅ Emergency restore completed"
    echo "🛡️ Previous files preserved in: $emergency_backup"
    echo "📄 Restore details logged in emergency-restore.log"
    
    # Log the restore operation
    cat >> emergency-restore.log <<EOF
$(date): Emergency restore completed
Backup Source: $backup_path
Emergency Backup: $emergency_backup
Restored By: $(whoami)
---
EOF
}
```

### **File System Repair Utilities**
```bash
# Repair common file system issues
repair_file_system() {
    echo "🔧 Running file system repair utilities..."
    
    # Fix file permissions
    echo "Fixing file permissions..."
    find . -type f -exec chmod 644 {} \;
    find . -type d -exec chmod 755 {} \;
    find . -name "*.sh" -exec chmod +x {} \;
    
    # Remove temporary files
    echo "Cleaning temporary files..."
    find . -name "*.tmp" -delete 2>/dev/null || true
    find . -name "*.temp" -delete 2>/dev/null || true
    find . -name "*~" -delete 2>/dev/null || true
    
    # Fix line endings (if needed)
    echo "Checking line endings..."
    find . -name "*.txt" -o -name "*.md" -o -name "*.py" -o -name "*.js" | while read file; do
        if file "$file" | grep -q "CRLF"; then
            echo "Converting CRLF to LF: $file"
            sed -i 's/\r$//' "$file"
        fi
    done
    
    echo "✅ File system repair completed"
}

# Validate project structure integrity
validate_project_structure() {
    echo "🔍 Validating project structure integrity..."
    
    local issues=0
    
    # Check for essential files
    local essential_files=("README.md" "PROJECT-STATUS-TRACKER.md")
    for file in "${essential_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "⚠️ Missing essential file: $file"
            ((issues++))
        fi
    done
    
    # Check for essential directories
    local essential_dirs=("session-logs" "backups")
    for dir in "${essential_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            echo "⚠️ Missing essential directory: $dir"
            mkdir -p "$dir"
            echo "✅ Created directory: $dir"
        fi
    done
    
    # Check for suspicious files
    find . -name "*.core" -o -name "core.*" | while read core_file; do
        echo "⚠️ Core dump file found: $core_file"
        ((issues++))
    done
    
    if [ $issues -eq 0 ]; then
        echo "✅ Project structure integrity verified"
        return 0
    else
        echo "⚠️ Project structure issues detected: $issues"
        return 1
    fi
}
```

---

## 📊 SAFETY MONITORING AND REPORTING

### **Safety Status Dashboard**
```bash
# Generate comprehensive safety status report
generate_safety_status() {
    local report_file="safety-status-$(date +%Y%m%d).md"
    
    cat > "$report_file" <<EOF
# File Safety Status Report

**Generated**: $(date)
**Project Directory**: $(pwd)

## Backup Status
EOF
    
    # Check backup availability
    if [ -d "backups" ]; then
        local backup_count=$(find backups -type d -name "*-*" | wc -l)
        local recent_backups=$(find backups -type d -mtime -7 | wc -l)
        local latest_backup=$(find backups -type d -name "*-*" | sort | tail -1)
        
        echo "- **Backup Directory**: ✅ Exists" >> "$report_file"
        echo "- **Total Backups**: $backup_count" >> "$report_file"
        echo "- **Recent Backups (7 days)**: $recent_backups" >> "$report_file"
        echo "- **Latest Backup**: $latest_backup" >> "$report_file"
    else
        echo "- **Backup Directory**: ❌ Missing" >> "$report_file"
    fi
    
    cat >> "$report_file" <<EOF

## File Protection Status
EOF
    
    # Check file integrity
    if [ -f "integrity-baseline.txt" ]; then
        echo "- **Integrity Baseline**: ✅ Available" >> "$report_file"
        if check_file_integrity . >/dev/null 2>&1; then
            echo "- **File Integrity**: ✅ Verified" >> "$report_file"
        else
            echo "- **File Integrity**: ⚠️ Violations detected" >> "$report_file"
        fi
    else
        echo "- **Integrity Baseline**: ❌ Not created" >> "$report_file"
    fi
    
    # Check for working copies
    local working_copies=$(find . -name "*working*" -type d | wc -l)
    echo "- **Active Working Copies**: $working_copies" >> "$report_file"
    
    cat >> "$report_file" <<EOF

## Audit Trail Status
EOF
    
    # Check audit logs
    if [ -f "file-changes-audit.log" ]; then
        local total_changes=$(grep -c "^\[" file-changes-audit.log)
        local recent_changes=$(grep "$(date '+%Y-%m-%d')" file-changes-audit.log | wc -l)
        
        echo "- **Change Audit Log**: ✅ Available" >> "$report_file"
        echo "- **Total Recorded Changes**: $total_changes" >> "$report_file"
        echo "- **Changes Today**: $recent_changes" >> "$report_file"
    else
        echo "- **Change Audit Log**: ❌ Not found" >> "$report_file"
    fi
    
    # Check for pending approvals
    if [ -f "approval-requests.log" ] && [ -s "approval-requests.log" ]; then
        local pending_requests=$(grep "PENDING" approval-requests.log | wc -l)
        echo "- **Pending Approval Requests**: $pending_requests" >> "$report_file"
    else
        echo "- **Pending Approval Requests**: 0" >> "$report_file"
    fi
    
    cat >> "$report_file" <<EOF

## Recommendations
EOF
    
    # Generate recommendations
    if [ ! -d "backups" ]; then
        echo "- Create backup directory and initial backup" >> "$report_file"
    fi
    
    if [ ! -f "integrity-baseline.txt" ]; then
        echo "- Create file integrity baseline" >> "$report_file"
    fi
    
    if [ ! -f "file-changes-audit.log" ]; then
        echo "- Initialize change audit logging" >> "$report_file"
    fi
    
    echo "📊 Safety status report generated: $report_file"
}
```

---

**These file safety protocols provide comprehensive protection mechanisms that can be adapted for any development project requiring data protection, change tracking, and recovery capabilities.**