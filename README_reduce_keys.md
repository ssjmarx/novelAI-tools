# NovelAI Lorebook Key Reducer

A Python script to efficiently reduce the number of activation keys in NovelAI .lorebook JSON files while preserving the most relevant keys.

## Features

- **Intelligent Key Prioritization**: Uses a scoring system to keep the most relevant keys
- **Context-Aware**: Considers key appearance in entry text for relevance
- **Configurable Reduction**: Set maximum number of keys per entry
- **Detailed Reporting**: Shows before/after comparison and summary statistics
- **Safe Processing**: Preserves all other lorebook data and structure

## How It Works

The script prioritizes keys based on multiple factors:

1. **Text Relevance**: Keys that appear in the entry text get higher scores
2. **Specificity**: Longer keys and proper nouns are preferred
3. **Uniqueness**: Keys with numbers, spaces, or special characters score higher
4. **Common Word Penalty**: Very common words get lower scores

## Usage

### Basic Usage
```bash
# Reduce to default 5 keys per entry
python3 reduce_lorebook_keys.py input.lorebook

# Reduce to 3 keys per entry
python3 reduce_lorebook_keys.py input.lorebook 3

# Reduce to 5 keys with custom output file
python3 reduce_lorebook_keys.py input.lorebook 5 output.lorebook
```

### Command Line Arguments
- `input_file`: Path to input .lorebook file (required)
- `max_keys`: Maximum keys per entry (default: 5)
- `output_file`: Output file path (optional, auto-generated if not provided)

### Examples
```bash
# Reduce to 3 keys, auto-generate output filename
python3 reduce_lorebook_keys.py "My Lorebook.lorebook" 3

# Reduce to 5 keys with custom output
python3 reduce_lorebook_keys.py "My Lorebook.lorebook" 5 "Reduced Lorebook.lorebook"

# Use default 5 keys
python3 reduce_lorebook_keys.py "My Lorebook.lorebook"
```

## Output

The script provides detailed output including:
- Processing progress for each entry
- Before/after key lists for modified entries
- Summary statistics (total entries modified, keys removed, etc.)
- Path to the output file

## Example Output

```
Input: test_lorebook_with_keys.lorebook
Output: test_reduced.lorebook
Maximum keys per entry: 3

Processing 3 entries...
Reducing keys to maximum of 3 per entry
Entry   1: 'The Ancient Library of Alexandria' - Reduced from 8 to 3 keys (removed 5)
  Original: library, ancient, ruins, knowledge, philosophy, mathematics, astronomy, medicine
  Reduced:  mathematics, philosophy, knowledge

============================================================
KEY REDUCTION SUMMARY
============================================================
Total entries processed: 3
Entries modified: 3
Total keys removed: 12
Average keys per entry (after): 3.0
Output saved to: test_reduced.lorebook
============================================================
```

## Key Scoring Algorithm

The script uses a sophisticated scoring system:

| Factor | Score | Description |
|--------|-------|-------------|
| Text Appearance | +10 | Key appears in entry text |
| Key Length | +0.5 per character | Longer keys are more specific |
| Numbers/Special Chars | +2 | Contains digits or special characters |
| Compound Words | +1 | Contains spaces or hyphens |
| Proper Nouns | +1 | Starts with capital letter |
| Common Words | -5 | Very common English words |

## Safety Features

- **Preserves Structure**: All lorebook metadata, categories, and settings are preserved
- **Updates Timestamps**: Modified entries get updated `lastUpdatedAt` timestamps
- **Error Handling**: Graceful handling of file errors and invalid JSON
- **Validation**: Ensures max_keys is at least 1

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Integration with Other Tools

This script works well with other NovelAI tools in this directory:

- Use after `generate_lorebook_keys.py` if too many keys were generated
- Use before `lorebook_converter.py` to convert reduced lorebook to readable format
- Combine with manual editing for optimal results

## Tips

1. **Start Conservative**: Try reducing to 5 keys first, then lower if needed
2. **Review Results**: Check the output to ensure important keys weren't removed
3. **Backup Original**: Always keep a copy of your original lorebook file
4. **Iterative Process**: You may need to run multiple times with different settings

## Troubleshooting

**File not found**: Ensure the input file path is correct and the file exists
**Permission denied**: Make sure you have read/write permissions for the files
**Invalid JSON**: Check that your input file is a valid NovelAI lorebook JSON file

## License

This script is part of the NovelAI tools collection and follows the same license terms.
