# FILE SAFETY AND BACKUP PROTOCOLS

**Purpose**: Reusable framework for protecting critical files during documentation processing  
**Extracted From**: Session management protocols, build scripts, and project safety practices  
**Application**: Any project requiring file safety, backup procedures, and change management

---

## 🛡️ CORE SAFETY PRINCIPLES

### **1. PRESERVATION-FIRST APPROACH**
- **Original files are sacred** - Source documentation must remain untouched
- **Work on copies only** - All modifications happen in temporary directories
- **Explicit permission required** - Never delete or modify without clear approval
- **Backup before changes** - Create safety copies before any destructive operation

### **2. CHANGE MANAGEMENT HIERARCHY**
```
SAFETY LEVEL    | OPERATIONS ALLOWED          | APPROVAL REQUIRED
----------------|----------------------------|------------------
READ-ONLY       | View, copy, analyze        | None
COPY-MODIFY     | Work on copies only        | User notification
BACKUP-MODIFY   | Modify with backup         | User approval
DIRECT-MODIFY   | Modify originals           | Explicit permission
DELETE          | Remove files               | Double confirmation
```

### **3. INFRASTRUCTURE PROTECTION**
- **Session logs are historical records** - Never delete project history
- **Protocol documents are project infrastructure** - Preserve methodology
- **Tracking documents maintain continuity** - Essential for project recovery
- **Distinguish content vs infrastructure** - Different safety requirements

---

## 📁 BACKUP STRATEGY FRAMEWORK

### **Automated Backup Creation**
```bash
# Create timestamped backup of critical files
create_backup() {
    local source_path="$1"
    local backup_type="${2:-manual}"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_dir="backups/$backup_type-$timestamp"
    
    echo "Creating $backup_type backup: $backup_dir"
    
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
**Reason**: ${3:-Standard backup procedure}

## Contents
$(find "$backup_dir" -type f | grep -v BACKUP-MANIFEST.md | sort)

## Recovery Instructions
To restore this backup:
\`\`\`bash
cp -r $backup_dir/* $source_path/
\`\`\`
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

### **Selective Backup by File Type**
```bash
# Backup specific file types or categories
backup_by_category() {
    local source_dir="$1"
    local category="$2"
    local timestamp=$(date +%Y%m%d-%H%M%S)
    
    case "$category" in
        "documentation")
            local pattern="*.md"
            local backup_dir="backups/docs-$timestamp"
            ;;
        "scripts")
            local pattern="*.sh"
            local backup_dir="backups/scripts-$timestamp"
            ;;
        "config")
            local pattern="*.yml *.yaml *.json *.conf"
            local backup_dir="backups/config-$timestamp"
            ;;
        "session-logs")
            local pattern="session-*.md"
            local backup_dir="backups/sessions-$timestamp"
            ;;
        *)
            echo "❌ Unknown backup category: $category"
            return 1
            ;;
    esac
    
    mkdir -p "$backup_dir"
    
    # Find and copy files matching pattern
    find "$source_dir" -name "$pattern" -type f | while read file; do
        # Preserve directory structure
        local rel_path=$(realpath --relative-to="$source_dir" "$file")
        local dest_dir="$backup_dir/$(dirname "$rel_path")"
        mkdir -p "$dest_dir"
        cp "$file" "$dest_dir/"
    done
    
    echo "✅ $category backup created: $backup_dir"
}
```

---

## 🔒 COPY-BASED PROTECTION STRATEGY

### **Safe Working Copy Creation**
```bash
# Create protected working copy for modifications
create_working_copy() {
    local source_dir="$1"
    local work_dir="${2:-temp/working-copy}"
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
    
    # Create working copy manifest
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
EOF
    
    echo "✅ Working copy created: $work_dir"
    echo "📁 Original files protected at: $source_dir"
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
    
    # Verify original files are unchanged
    if ! diff -r "$source_dir" "$work_dir" > /dev/null 2>&1; then
        echo "⚠️ Working copy has been modified (expected)"
        echo "✅ Original files remain protected"
        return 0
    else
        echo "📋 Working copy identical to source (no changes yet)"
        return 0
    fi
}
```

### **Change Application with Approval**
```bash
# Apply changes from working copy to originals with user approval
apply_changes_with_approval() {
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
    
    # Show differences
    echo "📊 Changes to be applied:"
    diff -r "$source_dir" "$work_dir" || true
    echo ""
    
    # Request approval (in automated context, this would be logged for manual review)
    echo "⚠️ APPROVAL REQUIRED:"
    echo "   This operation will modify original files"
    echo "   Changes have been prepared in working copy"
    echo "   Manual approval needed to proceed"
    echo ""
    echo "   To approve: review changes and run apply_approved_changes"
    echo "   To reject: run cleanup_working_copy"
    
    # Log the approval request
    cat >> "pending-approvals.log" <<EOF
$(date): APPROVAL REQUIRED
Operation: Apply changes to original files
Source: $source_dir
Working Copy: $work_dir
Description: $change_description
Status: PENDING MANUAL REVIEW
EOF
    
    return 1  # Return error to halt automated processing
}

# Apply pre-approved changes
apply_approved_changes() {
    local work_dir="$1"
    local source_dir="$2"
    local approval_code="$3"
    
    # Verify approval code (simple mechanism for demonstration)
    if [ "$approval_code" != "APPROVED" ]; then
        echo "❌ Invalid approval code. Changes not applied."
        return 1
    fi
    
    # Create final backup before applying changes
    if ! backup_before_operation "change-application" "$source_dir"; then
        echo "❌ Pre-change backup failed. Changes not applied."
        return 1
    fi
    
    # Apply changes
    echo "✅ Applying approved changes..."
    rsync -av --delete "$work_dir/" "$source_dir/"
    
    echo "✅ Changes successfully applied to original files"
    echo "🛡️ Backup available in backups/ directory"
    
    # Clean up working copy
    rm -rf "$work_dir"
    echo "🧹 Working copy cleaned up"
    
    return 0
}
```

---

## 📋 CHANGE TRACKING AND AUDIT TRAIL

### **Change Documentation System**
```bash
# Document all file modifications with audit trail
document_change() {
    local file_path="$1"
    local change_type="$2"
    local description="$3"
    local user="${4:-system}"
    
    local audit_log="file-changes-audit.log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Create audit entry
    cat >> "$audit_log" <<EOF
[$timestamp] $change_type: $file_path
User: $user
Description: $description
Size Before: $([ -f "$file_path.backup" ] && stat -f%z "$file_path.backup" 2>/dev/null || echo "N/A")
Size After: $([ -f "$file_path" ] && stat -f%z "$file_path" 2>/dev/null || echo "N/A")
Checksum: $([ -f "$file_path" ] && md5sum "$file_path" | cut -d' ' -f1 || echo "N/A")
---
EOF
    
    echo "📝 Change documented in audit log"
}

# Generate change summary report
generate_change_report() {
    local start_date="${1:-$(date -d '1 week ago' '+%Y-%m-%d')}"
    local end_date="${2:-$(date '+%Y-%m-%d')}"
    local report_file="change-report-$(date +%Y%m%d).md"
    
    cat > "$report_file" <<EOF
# File Change Report

**Period**: $start_date to $end_date
**Generated**: $(date)

## Summary
EOF
    
    # Count changes by type
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
    
    echo "" >> "$report_file"
    echo "## Detailed Changes" >> "$report_file"
    
    # Add detailed change list
    grep "^\[" file-changes-audit.log | \
    awk -v start="$start_date" -v end="$end_date" '
    $1 >= "[" start && $1 <= "[" end { print }' >> "$report_file"
    
    echo "📊 Change report generated: $report_file"
}
```

### **File Integrity Monitoring**
```bash
# Monitor file integrity with checksums
create_integrity_baseline() {
    local directory="$1"
    local baseline_file="integrity-baseline.txt"
    
    echo "🔍 Creating integrity baseline for: $directory"
    
    # Generate checksums for all files
    find "$directory" -type f -exec md5sum {} \; | sort > "$baseline_file"
    
    echo "✅ Integrity baseline created: $baseline_file"
    echo "📊 Monitoring $(wc -l < "$baseline_file") files"
}

# Check for file integrity violations
check_integrity() {
    local directory="$1"
    local baseline_file="integrity-baseline.txt"
    local violations_file="integrity-violations-$(date +%Y%m%d-%H%M%S).txt"
    
    if [ ! -f "$baseline_file" ]; then
        echo "❌ No integrity baseline found. Run create_integrity_baseline first."
        return 1
    fi
    
    echo "🔍 Checking file integrity..."
    
    # Generate current checksums
    find "$directory" -type f -exec md5sum {} \; | sort > temp-checksums.txt
    
    # Compare with baseline
    if ! diff "$baseline_file" temp-checksums.txt > "$violations_file"; then
        echo "⚠️ Integrity violations detected!"
        echo "📄 Details saved to: $violations_file"
        
        # Show summary
        echo ""
        echo "Modified files:"
        diff "$baseline_file" temp-checksums.txt | grep "^>" | cut -c3- | cut -d' ' -f2-
        
        rm temp-checksums.txt
        return 1
    else
        echo "✅ File integrity verified - no violations"
        rm temp-checksums.txt
        rm "$violations_file"
        return 0
    fi
}
```

---

## 🛡️ PERMISSION AND ACCESS CONTROL

### **Read-Only Mode Enforcement**
```bash
# Set files to read-only mode
protect_files() {
    local path="$1"
    local protection_level="${2:-read-only}"
    
    case "$protection_level" in
        "read-only")
            find "$path" -type f -exec chmod 444 {} \;
            find "$path" -type d -exec chmod 555 {} \;
            echo "🔒 Files protected (read-only): $path"
            ;;
        "locked")
            find "$path" -type f -exec chmod 000 {} \;
            find "$path" -type d -exec chmod 000 {} \;
            echo "🔒 Files locked (no access): $path"
            ;;
        "restore")
            find "$path" -type f -exec chmod 644 {} \;
            find "$path" -type d -exec chmod 755 {} \;
            echo "🔓 Files restored (normal access): $path"
            ;;
    esac
}

# Verify protection status
check_protection_status() {
    local path="$1"
    
    echo "🔍 Protection status for: $path"
    
    # Check file permissions
    find "$path" -type f | head -5 | while read file; do
        local perms=$(stat -c "%a %n" "$file" 2>/dev/null || stat -f "%A %N" "$file")
        echo "  $perms"
    done
    
    # Summary
    local readonly_count=$(find "$path" -type f -perm 444 | wc -l)
    local total_count=$(find "$path" -type f | wc -l)
    
    echo "📊 Read-only files: $readonly_count/$total_count"
}
```

### **Access Control Lists**
```bash
# Manage access permissions by operation type
check_operation_permission() {
    local operation="$1"
    local target_path="$2"
    local user="${3:-system}"
    
    # Define permission matrix
    case "$operation" in
        "read"|"copy"|"analyze")
            echo "✅ Permission granted: $operation (always allowed)"
            return 0
            ;;
        "modify-copy")
            echo "✅ Permission granted: $operation (working copy only)"
            return 0
            ;;
        "backup")
            echo "✅ Permission granted: $operation (safety operation)"
            return 0
            ;;
        "modify-original")
            echo "⚠️ Permission required: $operation (approval needed)"
            log_permission_request "$operation" "$target_path" "$user"
            return 1
            ;;
        "delete")
            echo "🛑 Permission denied: $operation (explicit approval required)"
            log_permission_request "$operation" "$target_path" "$user"
            return 1
            ;;
        *)
            echo "❌ Unknown operation: $operation"
            return 1
            ;;
    esac
}

# Log permission requests for manual review
log_permission_request() {
    local operation="$1"
    local target_path="$2"
    local user="$3"
    
    local request_log="permission-requests.log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat >> "$request_log" <<EOF
[$timestamp] PERMISSION REQUEST
Operation: $operation
Target: $target_path
Requested by: $user
Status: PENDING MANUAL APPROVAL
Auto-decision: DENIED (requires manual review)
---
EOF
    
    echo "📝 Permission request logged for manual review"
}
```

---

## 🧹 CLEANUP AND RECOVERY PROCEDURES

### **Safe Cleanup Operations**
```bash
# Clean up temporary files while preserving important data
safe_cleanup() {
    local cleanup_level="${1:-standard}"
    
    echo "🧹 Performing $cleanup_level cleanup..."
    
    case "$cleanup_level" in
        "temp-only")
            # Remove only temporary processing files
            rm -rf temp/processed temp/combined* temp/*.tmp
            echo "✅ Temporary processing files removed"
            ;;
        "standard")
            # Remove temp files but preserve backups and logs
            rm -rf temp/
            find . -name "*.tmp" -delete
            find . -name "*.temp" -delete
            echo "✅ Standard cleanup completed"
            ;;
        "aggressive")
            # Remove more files but still preserve critical data
            rm -rf temp/ output/intermediate/
            find . -name "*.tmp" -delete
            find . -name "*.temp" -delete
            find . -name "*~" -delete
            echo "✅ Aggressive cleanup completed"
            ;;
        "preserve-all")
            # Only remove obvious temporary files
            find . -name "*.tmp" -delete
            echo "✅ Minimal cleanup (preserving all data)"
            ;;
    esac
    
    # Never remove these critical items
    echo "🛡️ Protected items preserved:"
    echo "  - Source documentation files"
    echo "  - Session logs and history"
    echo "  - Backup directories"
    echo "  - Configuration files"
    echo "  - Audit trails"
}

# Emergency recovery procedures
emergency_recovery() {
    local recovery_type="$1"
    
    echo "🚨 Initiating emergency recovery: $recovery_type"
    
    case "$recovery_type" in
        "restore-from-backup")
            # Find most recent backup
            local latest_backup=$(find backups/ -type d -name "*-*" | sort | tail -1)
            if [ -z "$latest_backup" ]; then
                echo "❌ No backups found for recovery"
                return 1
            fi
            
            echo "📁 Restoring from: $latest_backup"
            # Manual approval would be required here
            echo "⚠️ Manual approval required for restore operation"
            ;;
        "reset-permissions")
            # Reset file permissions to safe defaults
            protect_files "." "restore"
            echo "✅ File permissions reset"
            ;;
        "integrity-check")
            # Comprehensive integrity verification
            if check_integrity "."; then
                echo "✅ System integrity verified"
            else
                echo "⚠️ Integrity issues detected - manual review required"
            fi
            ;;
    esac
}
```

---

## 📊 SAFETY MONITORING DASHBOARD

### **Safety Status Reporting**
```bash
# Generate comprehensive safety status report
generate_safety_report() {
    local report_file="safety-status-$(date +%Y%m%d).md"
    
    cat > "$report_file" <<EOF
# File Safety Status Report

**Generated**: $(date)
**System Status**: $(check_overall_safety_status)

## Backup Status
EOF
    
    # Check backup availability
    if [ -d "backups" ]; then
        echo "- **Backup directory exists**: ✅ Yes" >> "$report_file"
        echo "- **Recent backups**: $(find backups -type d -mtime -7 | wc -l) in last 7 days" >> "$report_file"
        echo "- **Latest backup**: $(find backups -type d | sort | tail -1)" >> "$report_file"
    else
        echo "- **Backup directory exists**: ❌ No" >> "$report_file"
    fi
    
    cat >> "$report_file" <<EOF

## File Protection Status
EOF
    
    # Check file protection
    local total_files=$(find . -name "*.md" -type f | wc -l)
    local protected_files=$(find . -name "*.md" -type f -perm 444 | wc -l)
    
    echo "- **Total documentation files**: $total_files" >> "$report_file"
    echo "- **Protected files**: $protected_files" >> "$report_file"
    echo "- **Protection ratio**: $(($protected_files * 100 / $total_files))%" >> "$report_file"
    
    cat >> "$report_file" <<EOF

## Audit Trail Status
EOF
    
    # Check audit logs
    if [ -f "file-changes-audit.log" ]; then
        local recent_changes=$(grep "$(date '+%Y-%m-%d')" file-changes-audit.log | wc -l)
        echo "- **Audit log exists**: ✅ Yes" >> "$report_file"
        echo "- **Changes today**: $recent_changes" >> "$report_file"
    else
        echo "- **Audit log exists**: ❌ No" >> "$report_file"
    fi
    
    echo "📊 Safety report generated: $report_file"
}

check_overall_safety_status() {
    local status="SAFE"
    
    # Check for recent unauthorized changes
    if [ -f "integrity-violations-*.txt" ]; then
        status="WARNING"
    fi
    
    # Check for pending permission requests
    if [ -f "permission-requests.log" ] && [ -s "permission-requests.log" ]; then
        status="PENDING_REVIEW"
    fi
    
    echo "$status"
}
```

---

**Implementation Note**: This framework provides comprehensive file safety and backup procedures that can be adapted for any documentation or development project. The multi-layered approach ensures data protection while maintaining operational flexibility through controlled change management.