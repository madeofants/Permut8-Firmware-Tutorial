#!/bin/bash
# file-classification-tool.sh - Automated file classification for archival
# Created: 2025-06-13
# Purpose: Classify files for safe archival based on age, type, and importance

echo "🔍 Documentation Project File Classifier"
echo "========================================"

# Configuration
CURRENT_DATE=$(date +%s)
SEVEN_DAYS_AGO=$((CURRENT_DATE - 604800))   # 7 days in seconds
FOURTEEN_DAYS_AGO=$((CURRENT_DATE - 1209600)) # 14 days in seconds

# Counters
ARCHIVE_SESSION=0
ARCHIVE_AUDIT=0
ARCHIVE_TEST=0
KEEP_PRODUCTION=0
KEEP_PROTOCOL=0
REVIEW_MANUAL=0

# Classification function
classify_file() {
    local file="$1"
    local basename=$(basename "$file")
    local file_date=$(stat -c %Y "$file" 2>/dev/null || echo $CURRENT_DATE)
    local age_days=$(( (CURRENT_DATE - file_date) / 86400 ))
    
    # Category A: Session History (archive if older than 7 days)
    if [[ "$basename" =~ -log\.md$|status\.md$|tracker\.md$|SESSION.*\.md$ ]] && [ $file_date -lt $SEVEN_DAYS_AGO ]; then
        echo "ARCHIVE_SESSION:$file:${age_days}d"
        ((ARCHIVE_SESSION++))
    
    # Category B: Audit Reports (archive if older than 14 days)
    elif [[ "$basename" =~ ^(audit-|terminology-|report-|AUDIT) ]] && [ $file_date -lt $FOURTEEN_DAYS_AGO ]; then
        echo "ARCHIVE_AUDIT:$file:${age_days}d"
        ((ARCHIVE_AUDIT++))
    
    # Category C: Test Files (always archive)
    elif [[ "$basename" =~ ^(test-|temp-|tmp-) ]] || [[ "$file" =~ test-temp-processing ]]; then
        echo "ARCHIVE_TEST:$file:${age_days}d"
        ((ARCHIVE_TEST++))
    
    # Category D: Production Content (never archive)
    elif [[ "$file" =~ /content/.*\.md$ ]]; then
        echo "KEEP_PRODUCTION:$file"
        ((KEEP_PRODUCTION++))
    
    # Category E: Active Protocols (never archive)
    elif [[ "$basename" =~ (session-start|CLAUDE|task-tracker|status-tracker|COMPREHENSIVE.*PLAN)\.md$ ]]; then
        echo "KEEP_PROTOCOL:$file"
        ((KEEP_PROTOCOL++))
    
    # Category F: Build Scripts (never archive)
    elif [[ "$basename" =~ \.(sh|py)$ ]]; then
        echo "KEEP_SCRIPT:$file"
        ((KEEP_PROTOCOL++))
    
    # Category G: HTML Output (never archive) 
    elif [[ "$file" =~ html-build/output/ ]]; then
        echo "KEEP_OUTPUT:$file"
        ((KEEP_PRODUCTION++))
    
    else
        echo "REVIEW_MANUAL:$file:${age_days}d"
        ((REVIEW_MANUAL++))
    fi
}

# Archive path generator
get_archive_path() {
    local classification="$1"
    local base_path="archive-non-production"
    
    case "$classification" in
        "ARCHIVE_SESSION")
            echo "$base_path/session-logs/2025-06/"
            ;;
        "ARCHIVE_AUDIT") 
            echo "$base_path/audit-reports/2025-06/"
            ;;
        "ARCHIVE_TEST")
            echo "$base_path/development-artifacts/test-files/"
            ;;
        *)
            echo "UNKNOWN_ARCHIVE_PATH"
            ;;
    esac
}

# Main processing
echo "📊 Scanning active/ directory..."
echo ""

# Process all files in active directory
while IFS= read -r -d '' file; do
    classify_file "$file"
done < <(find active/ -type f -print0)

echo ""
echo "📈 CLASSIFICATION SUMMARY"
echo "========================"
echo "📦 Archive Session Files: $ARCHIVE_SESSION"
echo "📦 Archive Audit Files: $ARCHIVE_AUDIT"  
echo "📦 Archive Test Files: $ARCHIVE_TEST"
echo "✅ Keep Production Files: $KEEP_PRODUCTION"
echo "✅ Keep Protocol Files: $KEEP_PROTOCOL"
echo "⚠️  Manual Review Required: $REVIEW_MANUAL"
echo ""

TOTAL_TO_ARCHIVE=$((ARCHIVE_SESSION + ARCHIVE_AUDIT + ARCHIVE_TEST))
TOTAL_TO_KEEP=$((KEEP_PRODUCTION + KEEP_PROTOCOL))

echo "🎯 ARCHIVE PLAN SUMMARY"
echo "======================"
echo "Files to archive: $TOTAL_TO_ARCHIVE"
echo "Files to keep active: $TOTAL_TO_KEEP"
echo "Files needing review: $REVIEW_MANUAL"
echo ""

if [ $REVIEW_MANUAL -gt 0 ]; then
    echo "⚠️  WARNING: $REVIEW_MANUAL files need manual review before archival"
    echo "   Run with --show-manual to see these files"
fi

# Show manual review files if requested
if [[ "$1" == "--show-manual" ]]; then
    echo ""
    echo "🔍 FILES REQUIRING MANUAL REVIEW:"
    echo "================================="
    while IFS= read -r -d '' file; do
        result=$(classify_file "$file")
        if [[ "$result" =~ ^REVIEW_MANUAL ]]; then
            echo "  $file"
        fi
    done < <(find active/ -type f -print0)
fi

# Generate archive commands if requested
if [[ "$1" == "--generate-commands" ]]; then
    echo ""
    echo "📝 ARCHIVE COMMANDS (review before executing):"
    echo "=============================================="
    echo ""
    
    echo "# Create archive directories"
    echo "mkdir -p archive-non-production/session-logs/2025-06/"
    echo "mkdir -p archive-non-production/audit-reports/2025-06/"
    echo "mkdir -p archive-non-production/development-artifacts/test-files/"
    echo ""
    
    echo "# Archive session files"
    while IFS= read -r -d '' file; do
        result=$(classify_file "$file")
        if [[ "$result" =~ ^ARCHIVE_SESSION ]]; then
            echo "mv \"$file\" archive-non-production/session-logs/2025-06/"
        fi
    done < <(find active/ -type f -print0)
    echo ""
    
    echo "# Archive audit files"
    while IFS= read -r -d '' file; do
        result=$(classify_file "$file")
        if [[ "$result" =~ ^ARCHIVE_AUDIT ]]; then
            echo "mv \"$file\" archive-non-production/audit-reports/2025-06/"
        fi
    done < <(find active/ -type f -print0)
    echo ""
    
    echo "# Archive test files"
    while IFS= read -r -d '' file; do
        result=$(classify_file "$file")
        if [[ "$result" =~ ^ARCHIVE_TEST ]]; then
            echo "mv \"$file\" archive-non-production/development-artifacts/test-files/"
        fi
    done < <(find active/ -type f -print0)
fi

echo ""
echo "✅ Classification complete!"
echo ""
echo "Usage:"
echo "  $0                    # Show summary only"
echo "  $0 --show-manual     # Show files needing manual review"  
echo "  $0 --generate-commands # Generate archive commands"