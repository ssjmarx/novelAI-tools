# Simple Key Sanity Checker for NovelAI Lorebooks

A Python script that ensures lorebook entries of specific types (character, organization, location, item) include the singular form of their name in their activation keys.

## Purpose

This script solves a common problem in NovelAI lorebooks: entries that should be activated when their name is mentioned, but lack the proper name-based activation keys. For example, a character named "Master Elara" should have "elara" and/or "Master Elara" in her keys to ensure she's activated when someone mentions her by name.

## Features

- **Type Detection**: Automatically identifies entries of types: character, organization, location, item (and synonyms)
- **Smart Name Extraction**: Extracts core names from titles, removing prefixes like "The", "Lord", "King", etc.
- **Singular Form Generation**: Converts plural names to singular form (e.g., "Crystal Caves" → "crystal cave")
- **Dual Key Addition**: Adds both normalized singular form and original core name when different
- **Check-Only Mode**: Preview issues without modifying files
- **Comprehensive Reporting**: Detailed output showing what changes would be made

## How It Works

1. **Type Matching**: Scans entries for target types and their synonyms
2. **Name Extraction**: Removes common prefixes/suffixes from titles to get core names
3. **Normalization**: Converts to singular form and lowercase
4. **Key Checking**: Verifies if name-based keys already exist
5. **Key Addition**: Adds missing name keys while preserving existing ones

## Usage

### Check Only (Preview Mode)
```bash
# Check for issues without modifying files
python3 simple_key_sanity_checker.py lorebook.lorebook --check-only
```

### Fix Issues
```bash
# Auto-generate output filename
python3 simple_key_sanity_checker.py lorebook.lorebook

# Specify custom output filename
python3 simple_key_sanity_checker.py lorebook.lorebook fixed_lorebook.lorebook
```

### Command Line Arguments
- `input_file`: Path to input .lorebook file (required)
- `output_file`: Output file path (optional, auto-generated if not provided)
- `--check-only`: Only check for issues, don't modify the file

## Supported Types and Synonyms

| Category | Synonyms |
|----------|----------|
| **character** | character, characters, person, people, individual, npc, protagonist, antagonist |
| **organization** | organization, organisation, group, faction, guild, cult, company, order, society, clan |
| **location** | location, locations, place, area, region, site, spot, venue, destination |
| **item** | item, items, object, objects, artifact, artifacts, equipment, gear, tool, weapon, weaponry |

## Name Processing Examples

| Original Title | Core Name | Normalized | Keys Added |
|----------------|------------|-------------|------------|
| "The Ancient Library of Alexandria" | "Ancient Library of Alexandria" | "ancient library" | "ancient library", "Ancient Library" |
| "Master Elara" | "Master Elara" | "elara" | "elara", "Master Elara" |
| "The Crystal Caves" | "Crystal Caves" | "crystal cave" | "crystal cave", "Crystal Caves" |
| "King Vorlagun the Unyielding" | "Vorlagun" | "vorlagun" | "vorlagun", "Vorlagun" |

## Example Output

```
Input: my_lorebook.lorebook
Mode: Check only (read-only)

Checking 57 entries for missing name keys...
Target types: character, organization, location, item

Entry   1: 'The Ancient Library of Alexandria' - ISSUES FOUND
  Type: locations
  - Added missing name key: 'ancient library'
  - Added original name key: 'The Ancient Library'
  Current keys: library, ancient, ruins, knowledge, ancient library, The Ancient Library

Entry   2: 'Master Elara' - ISSUES FOUND
  Type: characters
  - Added missing name key: 'elara'
  - Added original name key: 'Master Elara'
  Current keys: sorceress, guardian, magic, elara, Master Elara

============================================================
CHECK RESULTS (READ-ONLY)
============================================================
Total entries processed: 57
Entries with issues: 42
Total issues found: 89
Run with output file to fix these issues.
============================================================
```

## Name Normalization Rules

1. **Prefix Removal**: Strips common titles like "The", "Lord", "King", "Queen", "Sir", "Master", etc.
2. **Suffix Removal**: Removes honorifics like "the Great", "the Wise", "I", "II", "Jr", "Sr", etc.
3. **Pattern Handling**: 
   - "Name the Adjective" → "Name"
   - "Name, Title" → "Name"
   - "Name of Place" → "Name"
4. **Plural to Singular**:
   - "ies" → "y" (cities → city)
   - "es" → "e" (boxes → box)
   - "s" → "" (caves → cave)
5. **Special Cases**: Handles specific irregular forms

## Integration with Other Tools

This script works perfectly with other NovelAI tools:

1. **Before Key Reduction**: Run sanity checker first to ensure name keys exist
2. **After Key Generation**: Use after `generate_lorebook_keys.py` to add missing name keys
3. **Before Manual Editing**: Check for issues before making manual adjustments
4. **Quality Assurance**: Use as final check before importing to NovelAI

## Safety Features

- **Preserves Existing Keys**: Never removes or modifies existing activation keys
- **Updates Timestamps**: Modified entries get updated `lastUpdatedAt` timestamps
- **Case-Insensitive Checking**: Avoids duplicate keys with different capitalization
- **Error Handling**: Graceful handling of file errors and invalid JSON
- **Backup Friendly**: Always creates new files, never overwrites originals

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Tips for Best Results

1. **Run Check-Only First**: Always preview changes before applying them
2. **Review Results**: Check that added keys make sense for your lorebook
3. **Combine with Key Reduction**: Use after reducing keys to ensure essential name keys remain
4. **Regular Maintenance**: Run periodically after adding new entries
5. **Custom Types**: Modify the type patterns if you have custom categories

## Troubleshooting

**No entries processed**: Check that your lorebook has the correct JSON structure
**Type not recognized**: Verify your type field matches one of the supported synonyms
**Name extraction issues**: Some complex titles may need manual adjustment
**Duplicate keys**: Script prevents duplicates but check the output for any unexpected additions

## Advanced Usage

The script can be easily customized by modifying the class variables:

```python
# Add custom type synonyms
self.type_patterns['my_type'] = ['my_type', 'synonym1', 'synonym2']

# Add custom prefixes to strip
self.name_prefixes.extend(['custom_prefix ', 'another_prefix '])

# Add custom suffixes to strip
self.name_suffixes.extend(['custom_suffix', 'another_suffix'])
```

## License

This script is part of the NovelAI tools collection and follows the same license terms.
