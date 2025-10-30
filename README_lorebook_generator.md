# NovelAI Lorebook Key Generator

A Python script that automatically generates relevant activation keys for NovelAI lorebook entries using the NovelAI API.

## Features

- **AI-Powered Key Generation**: Uses NovelAI's Kayra model to generate contextually relevant keys
- **User Control**: Requires manual initiation for each entry (NovelAI requirement)
- **Quality Assurance**: Validates key count and provides retry/regenerate options
- **Secure**: Prompts for API token instead of reading from files
- **Flexible**: Works with any .lorebook file format

## Requirements

- Python 3.7+
- NovelAI API access
- Required packages: `novelai-api`

## Installation

1. Install the NovelAI API package:
```bash
pip install novelai-api
```

2. Ensure you have a valid NovelAI API token

## Usage

```bash
python generate_lorebook_keys.py <input_lorebook> [output_lorebook]
```

### Examples

```bash
# Basic usage (auto-generates output filename)
python generate_lorebook_keys.py "my_lorebook.lorebook"

# Specify output file
python generate_lorebook_keys.py "my_lorebook.lorebook" "my_lorebook_updated.lorebook"
```

## How It Works

1. **Login**: Prompts for your NovelAI API token
2. **Analysis**: Reads and parses your lorebook file
3. **Generation**: For each entry needing keys:
   - Shows entry details
   - Waits for your press of Enter to initiate generation
   - Generates 4-10 relevant keys using AI
   - Allows you to accept, retry, regenerate, or skip
4. **Output**: Saves updated lorebook with new keys

## Key Generation

The script uses carefully crafted examples to guide the AI in generating appropriate keys:

- **Sci-fi item**: Quantum Plasma Rifle → weapon, plasma, rifle, prototype, energy weapon, military, sci-fi
- **Cyberpunk location**: Neo-Tokyo District 7 → city, cyberpunk, neon, futuristic, district, tokyo, rain, corporate  
- **Modern character**: Detective Sarah Chen → detective, cybernetic, investigator, private eye, chen, neo-tokyo, missing persons

## Options During Generation

**After every key generation**, you can choose to:

1. **Accept** - Use the generated keys and continue
2. **Regenerate** - Generate new keys for the same entry
3. **Skip** - Keep existing keys (if any) and continue
4. **Retry** - Try generating again (same as regenerate)

*Note: Options are available for every generation, not just when there are errors*

## Output

The script creates a new lorebook file with:
- All original entries and metadata preserved
- New AI-generated keys added to entries that needed them
- Updated timestamps for modified entries
- Same file structure and format as input

## Security

- API tokens are prompted interactively (never stored in files)
- No sensitive information is hardcoded in the script
- All examples are original content (no copyrighted material)

## Troubleshooting

**"Error generating keys"**: Check your API token and internet connection
**"Only generated X keys (minimum: 4)"**: Use option 2 to regenerate or option 4 to retry
**Script won't start**: Ensure you have Python 3.7+ and required packages installed

## File Format

The script works with standard NovelAI lorebook format (.lorebook files) containing:
- Entry metadata (title, type, description, keys)
- Categories and settings
- Proper JSON structure

Generated keys follow NovelAI best practices:
- 4-10 keys per entry
- Contextually relevant terms
- Proper formatting for activation
