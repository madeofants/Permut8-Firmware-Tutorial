# Link Conversion Mapping: .md Files to HTML Anchors

**Generated**: June 16, 2025  
**Purpose**: Map all .md file references to their corresponding HTML anchor IDs

## HTML Anchor Generation Rules

Based on `generate_documentation_html.py`, anchors are created as:
```python
filename = os.path.basename(file_path).replace('.md', '')
anchor_id = filename.lower().replace(' ', '-').replace('_', '-')
```

## Key File Mappings

### Foundation Path Files
- `QUICKSTART.md` → `#quickstart`
- `how-dsp-affects-sound.md` → `#how-dsp-affects-sound`
- `getting-audio-in-and-out.md` → `#getting-audio-in-and-out`
- `simplest-distortion.md` → `#simplest-distortion`
- `audio-engineering-for-programmers.md` → `#audio-engineering-for-programmers`

### Most Referenced Files (244 total .md references found)
- `../index.md` → `#index` (21 references)
- `basic-filter.md` → `#basic-filter` (6 references)
- `parameter-mapping.md` → `#parameter-mapping` (4 references)
- `make-a-delay.md` → `#make-a-delay` (4 references)
- `debug-your-plugin.md` → `#debug-your-plugin` (4 references)

### Language Reference
- `core_language_reference.md` → `#core-language-reference`
- `language-syntax-reference.md` → `#language-syntax-reference`
- `standard-library-reference.md` → `#standard-library-reference`
- `types-and-operators.md` → `#types-and-operators`
- `core-functions.md` → `#core-functions`

### Architecture Files
- `memory-layout.md` → `#memory-layout`
- `memory-model.md` → `#memory-model`
- `processing-order.md` → `#processing-order`
- `state-management.md` → `#state-management`
- `p8bank-format.md` → `#p8bank-format`

### Tutorial Files
- `creating-firmware-banks.md` → `#creating-firmware-banks`
- `compiler-troubleshooting-guide.md` → `#compiler-troubleshooting-guide`
- `complete-development-workflow.md` → `#complete-development-workflow`
- `mod-vs-full-architecture-guide.md` → `#mod-vs-full-architecture-guide`

### Cookbook Files
- `bitcrusher.md` → `#bitcrusher`
- `ring-modulation.md` → `#ring-modulation`
- `parameter-smoothing.md` → `#parameter-smoothing`
- `knob-to-frequency.md` → `#knob-to-frequency`
- `control-leds.md` → `#control-leds`
- `display-patterns.md` → `#display-patterns`
- `sync-to-tempo.md` → `#sync-to-tempo`

### Assembly Files
- `gazl-assembly-guide.md` → `#gazl-assembly-guide`
- `gazl-instruction-reference.md` → `#gazl-instruction-reference`

## Conversion Strategy

### 1. Simple Filename Links
```markdown
[Text](filename.md) → [Text](#filename)
```

### 2. Relative Path Links
```markdown
[Text](../path/filename.md) → [Text](#filename)
[Text](../../path/filename.md) → [Text](#filename)
[Text](../../../path/filename.md) → [Text](#filename)
```

### 3. Complex Path Handling
All relative paths should resolve to just the final filename for anchor conversion:
- `../user-guides/tutorials/debug-your-plugin.md` → `#debug-your-plugin`
- `../../../fundamentals/audio-engineering-for-programmers.md` → `#audio-engineering-for-programmers`

## High-Priority Conversion Files

### Master Navigation Hub
- `index/master-index.md` - Contains 50+ .md links, central navigation

### Foundation Learning Path
- `user-guides/cookbook/fundamentals/simplest-distortion.md` - The file user identified
- `fundamentals/audio-engineering-for-programmers.md` - 15+ links
- `user-guides/QUICKSTART.md` - Entry point

### Language Documentation
- `language/language-syntax-reference.md` - 12+ links
- `language/core_language_reference.md` - 12+ links

## Validation Requirements

After conversion, verify:
1. All anchor IDs exist in generated HTML
2. Links work correctly when clicked
3. No broken internal navigation
4. Cross-references maintain logical flow

## Implementation Notes

- Process files in order of highest link count first
- Update all files referencing each target before moving to next
- Test each batch conversion before proceeding
- Maintain audit trail of all changes