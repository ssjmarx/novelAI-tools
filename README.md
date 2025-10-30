# NovelAI Tools

A collection of Python utilities for managing and enhancing NovelAI lorebooks. These tools help you convert, edit, and automatically generate activation keys for your NovelAI lorebook entries.

## 🛠️ Tools Included

### 1. Lorebook Converter (`lorebook_converter.py`)
Convert NovelAI lorebook files between JSON (.lorebook) and human-readable TXT formats for easier editing and management.

**Features:**
- Bidirectional conversion (JSON ↔ TXT)
- Preserves all metadata, categories, and settings
- Human-readable TXT format with structured layout
- Maintains UUIDs and timestamps
- Command-line interface with flexible options

### 2. Lorebook Key Generator (`generate_lorebook_keys.py`)
Automatically generates relevant activation keys for lorebook entries using NovelAI's AI models.

**Features:**
- AI-powered key generation using NovelAI's Kayra model
- Contextually relevant keys based on entry content
- User control with manual initiation (NovelAI requirement)
- Quality validation with retry/regenerate options
- Secure API token handling
- Batch processing of entire lorebooks

## 📋 Requirements

- Python 3.7+
- NovelAI API access (for key generator)
- Required packages:
  ```bash
  pip install novelai-api
  ```

## 🚀 Quick Start

### Installing Dependencies

```bash
pip install novelai-api
```

### Basic Usage

#### Convert Lorebook to Readable Format
```bash
# Convert JSON to TXT for easy editing
python lorebook_converter.py my_lorebook.lorebook

# Convert TXT back to JSON
python lorebook_converter.py my_lorebook.txt --to-json
```

#### Generate AI-Powered Keys
```bash
# Generate keys for entries that need them
python generate_lorebook_keys.py my_lorebook.lorebook

# Specify custom output file
python generate_lorebook_keys.py my_lorebook.lorebook my_lorebook_updated.lorebook
```

## 📖 Detailed Usage

### Lorebook Converter

The converter makes it easy to edit lorebooks in a human-readable format:

```bash
# Convert JSON to TXT
python lorebook_converter.py input.lorebook

# Convert TXT to JSON (auto-detects from .txt extension)
python lorebook_converter.py input.txt

# Force conversion to JSON
python lorebook_converter.py input.txt --to-json

# Specify custom output
python lorebook_converter.py input.txt output.lorebook
```

**TXT Format Features:**
- Structured entry display with all metadata
- Category information and settings
- Context configuration details
- Advanced conditions and bias groups
- Easy-to-read content sections

### Lorebook Key Generator

The key generator uses AI to create relevant activation keys:

```bash
python generate_lorebook_keys.py <input_lorebook> [output_lorebook]
```

**Interactive Process:**
1. Enter your NovelAI API token when prompted
2. Script analyzes each entry in your lorebook
3. For entries needing keys:
   - Shows entry details (title, type, description)
   - Press Enter to initiate AI generation
   - Review generated keys (4-10 per entry)
   - Choose to accept, regenerate, skip, or retry

**Key Generation Examples:**
- **Sci-fi item**: "Quantum Plasma Rifle" → `weapon, plasma, rifle, prototype, energy weapon, military, sci-fi`
- **Location**: "Neo-Tokyo District 7" → `city, cyberpunk, neon, futuristic, district, tokyo, rain, corporate`
- **Character**: "Detective Sarah Chen" → `detective, cybernetic, investigator, private eye, chen, neo-tokyo, missing persons`

## 🔄 Workflow Example

Here's a typical workflow for managing a lorebook:

```bash
# 1. Convert your lorebook to editable format
python lorebook_converter.py my_story.lorebook

# 2. Edit the TXT file (add entries, modify content, etc.)
# Open my_story.txt in your favorite text editor...

# 3. Convert back to JSON format
python lorebook_converter.py my_story.txt --to-json

# 4. Generate AI keys for new/updated entries
python generate_lorebook_keys.py my_story.lorebook my_story_final.lorebook
```

## 📁 File Structure

```
novelAI-tools/
├── README.md                          # This file
├── README_lorebook_generator.md       # Detailed docs for key generator
├── lorebook_converter.py              # JSON ↔ TXT converter
├── generate_lorebook_keys.py          # AI key generator
├── test_lorebook.lorebook             # Sample lorebook (JSON)
├── test_lorebook.txt                  # Sample lorebook (TXT)
├── test_lorebook_with_keys.lorebook  # Sample with generated keys
└── .git/                              # Version control
```

## 🛡️ Security

- **API Tokens**: Prompted interactively, never stored in files
- **No Hardcoded Credentials**: All sensitive input is user-provided
- **Local Processing**: All file operations happen locally
- **Open Source**: Full transparency in code functionality

## 🎯 Use Cases

### For Writers
- **Easy Editing**: Convert lorebooks to TXT for comfortable editing
- **Consistent Keys**: Ensure all entries have proper activation keys
- **Batch Processing**: Update entire lorebooks efficiently

### For Game Masters
- **World Building**: Manage complex lore with multiple categories
- **AI Assistance**: Let AI suggest relevant keywords for your entries
- **Format Flexibility**: Work in your preferred format

### For Developers
- **Integration**: Use scripts in automated workflows
- **API Integration**: Leverage NovelAI's capabilities programmatically
- **Data Management**: Maintain consistent lorebook structures

## 🔧 Advanced Features

### Context Configuration
Both tools preserve and handle:
- Token budgets and priorities
- Prefix/suffix settings
- Trim directions
- Insertion positions

### Categories and Organization
- Full category support with UUIDs
- Subcontext creation options
- Category-specific defaults
- Bias groups and advanced conditions

### Metadata Preservation
- Original timestamps maintained
- UUID consistency across conversions
- Entry ordering preserved
- Settings and configurations intact

## 🐛 Troubleshooting

### Common Issues

**"Error: Invalid JSON"**
- Check that your .lorebook file is valid JSON
- Ensure file encoding is UTF-8

**"Error generating keys"**
- Verify your NovelAI API token is valid
- Check internet connection
- Ensure you have API access permissions

**"Only generated X keys (minimum: 4)"**
- Use option 2 to regenerate with different parameters
- Try option 4 to retry the generation
- Consider manually adding keys if AI struggles

**File not found errors**
- Check file paths and extensions
- Ensure files exist in specified locations
- Use absolute paths if needed

### Debug Mode

For detailed error information, run scripts with Python's verbose mode:
```bash
python -v lorebook_converter.py input.lorebook
python -v generate_lorebook_keys.py input.lorebook
```

## 📝 Contributing

This project is open to contributions! Areas for improvement:

- Additional output formats (Markdown, CSV, etc.)
- Batch processing for multiple lorebooks
- GUI interface for easier use
- More sophisticated key generation algorithms
- Integration with other AI platforms

## 📄 License

This project is provided as-is for educational and personal use. Please respect NovelAI's terms of service when using the API.

## 🔗 Related Resources

- [NovelAI Official Documentation](https://docs.novelai.net/)
- [NovelAI API Reference](https://api.novelai.net/docs)
- [Python novelai-api Package](https://pypi.org/project/novelai-api/)

---

**Made with ❤️ for the NovelAI community**
