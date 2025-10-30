# NovelAI Tools

A collection of Python utilities for managing and enhancing NovelAI lorebooks. Right now there's only two.

## 🛠️ Tools Included

### 1. Lorebook Converter (`lorebook_converter.py`)
Convert NovelAI lorebook files between JSON (.lorebook) and human-readable TXT formats for easier editing and management.

### 2. Lorebook Key Generator (`generate_lorebook_keys.py`)
Automatically generates relevant activation keys for lorebook entries using NovelAI's AI models.  Uses your own NovelAI subscription and API key.

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