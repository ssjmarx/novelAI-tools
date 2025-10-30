#!/usr/bin/env python3
"""
NovelAI Lorebook Converter

A tool to convert NovelAI .lorebook JSON files to readable TXT format and back.
This makes it easier to read, edit, and manage lorebook entries.

Usage:
    python lorebook_converter.py input.lorebook        # Convert JSON to TXT
    python lorebook_converter.py input.txt --to-json   # Convert TXT to JSON
    python lorebook_converter.py input.txt output.lorebook  # Convert TXT to JSON with custom output
"""

import json
import argparse
import sys
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class LorebookConverter:
    """Handles conversion between NovelAI lorebook JSON and TXT formats."""
    
    def __init__(self):
        self.category_map = {}  # Maps category names to IDs
        self.reverse_category_map = {}  # Maps category IDs to names
    
    def json_to_txt(self, input_file: str, output_file: Optional[str] = None) -> str:
        """Convert a .lorebook JSON file to a readable TXT file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lorebook = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{input_file}': {e}")
            sys.exit(1)
        
        # Build category mappings
        for category in lorebook.get('categories', []):
            self.reverse_category_map[category['id']] = category['name']
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.txt'))
        
        # Generate TXT content
        txt_content = self._generate_txt_content(lorebook)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        print(f"Successfully converted '{input_file}' to '{output_file}'")
        return output_file
    
    def txt_to_json(self, input_file: str, output_file: Optional[str] = None) -> str:
        """Convert a TXT file back to a .lorebook JSON file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                txt_content = f.read()
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        
        # Parse TXT content
        lorebook = self._parse_txt_content(txt_content)
        
        # Generate output filename if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.lorebook'))
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lorebook, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully converted '{input_file}' to '{output_file}'")
        return output_file
    
    def _generate_txt_content(self, lorebook: Dict[str, Any]) -> str:
        """Generate readable TXT content from lorebook JSON."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("NOVELAI LOREBOOK")
        lines.append("=" * 80)
        lines.append(f"Version: {lorebook.get('lorebookVersion', 6)}")
        lines.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Categories
        if lorebook.get('categories'):
            lines.append("CATEGORIES")
            lines.append("-" * 40)
            for category in lorebook['categories']:
                lines.append(f"Category: {category['name']}")
                lines.append(f"ID: {category['id']}")
                lines.append(f"Enabled: {category.get('enabled', True)}")
                if category.get('createSubcontext', False):
                    lines.append(f"Creates Subcontext: Yes")
                lines.append("")
        
        # Entries
        if lorebook.get('entries'):
            lines.append("LORE ENTRIES")
            lines.append("-" * 40)
            
            for i, entry in enumerate(lorebook['entries'], 1):
                lines.append(f"ENTRY #{i}")
                lines.append("=" * 60)
                
                # Basic info
                lines.append(f"Display Name: {entry['displayName']}")
                lines.append(f"ID: {entry['id']}")
                
                # Category
                category_id = entry.get('category', '')
                category_name = self.reverse_category_map.get(category_id, 'Unknown')
                lines.append(f"Category: {category_name} ({category_id})")
                
                # Keys
                keys = entry.get('keys', [])
                lines.append(f"Activation Keys: {', '.join(keys)}")
                
                # Status
                lines.append(f"Enabled: {entry.get('enabled', True)}")
                lines.append(f"Force Activation: {entry.get('forceActivation', False)}")
                lines.append(f"Search Range: {entry.get('searchRange', 1000)}")
                
                # Content
                lines.append("")
                lines.append("CONTENT:")
                lines.append("-" * 20)
                
                # Parse the text field to extract title and description
                text = entry.get('text', '')
                if text.startswith('----\n'):
                    text_parts = text.split('\n', 2)
                    if len(text_parts) >= 3:
                        title = text_parts[1]
                        description = text_parts[2]
                        lines.append(f"Title: {title}")
                        lines.append(f"Description: {description}")
                    else:
                        lines.append(text)
                else:
                    lines.append(text)
                
                # Context Configuration
                context_config = entry.get('contextConfig', {})
                lines.append("")
                lines.append("CONTEXT CONFIGURATION:")
                lines.append("-" * 25)
                
                if context_config.get('prefix'):
                    lines.append(f"Prefix: {repr(context_config['prefix'])}")
                else:
                    lines.append("Prefix: ''")
                    
                if context_config.get('suffix'):
                    lines.append(f"Suffix: {repr(context_config['suffix'])}")
                else:
                    lines.append("Suffix: '\\n'")
                    
                lines.append(f"Token Budget: {context_config.get('tokenBudget', 100)}")
                lines.append(f"Budget Priority: {context_config.get('budgetPriority', 400)}")
                lines.append(f"Trim Direction: {context_config.get('trimDirection', 'trimBottom')}")
                
                # Advanced Conditions
                advanced_conditions = entry.get('advancedConditions', [])
                lines.append("")
                lines.append("ADVANCED CONDITIONS:")
                lines.append("-" * 22)
                if advanced_conditions:
                    for condition in advanced_conditions:
                        lines.append(f"  Type: {condition.get('type', 'unknown')}")
                        lines.append(f"  Key: {condition.get('key', '')}")
                        lines.append(f"  Range: {condition.get('range', 0)}")
                        lines.append("")
                else:
                    lines.append("  (No advanced conditions)")
                
                # Lore Bias Groups
                bias_groups = entry.get('loreBiasGroups', [])
                lines.append("")
                lines.append("LORE BIAS GROUPS:")
                lines.append("-" * 18)
                if bias_groups:
                    for bias in bias_groups:
                        if bias.get('phrases'):
                            lines.append(f"  Phrases: {', '.join(bias['phrases'])}")
                        lines.append(f"  Bias: {bias.get('bias', 0)}")
                        lines.append(f"  Enabled: {bias.get('enabled', True)}")
                        lines.append("")
                else:
                    lines.append("  (No lore bias groups)")
                
                lines.append("")
                lines.append("")
        
        # Settings
        settings = lorebook.get('settings', {})
        if settings:
            lines.append("SETTINGS")
            lines.append("-" * 40)
            for key, value in settings.items():
                lines.append(f"{key}: {value}")
        
        return '\n'.join(lines)
    
    def _parse_txt_content(self, txt_content: str) -> Dict[str, Any]:
        """Parse TXT content back to lorebook JSON format."""
        lines = txt_content.split('\n')
        
        lorebook = {
            'lorebookVersion': 6,
            'entries': [],
            'categories': [],
            'settings': {
                'orderByKeyLocations': False
            }
        }
        
        current_section = None
        current_entry = None
        current_category = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and separators
            if not line or line.startswith('=') or line.startswith('-'):
                i += 1
                continue
            
            # Parse header information
            if line.startswith('Version:'):
                try:
                    lorebook['lorebookVersion'] = int(line.split(':', 1)[1].strip())
                except:
                    pass
                i += 1
                continue
            
            # Section headers
            if line == 'CATEGORIES':
                current_section = 'categories'
                i += 1
                continue
            elif line == 'LORE ENTRIES':
                current_section = 'entries'
                i += 1
                continue
            elif line == 'SETTINGS':
                current_section = 'settings'
                i += 1
                continue
            
            # Parse based on current section
            if current_section == 'categories':
                if line.startswith('Category:'):
                    if current_category:
                        lorebook['categories'].append(current_category)
                    current_category = {
                        'name': line.split(':', 1)[1].strip(),
                        'id': str(uuid.uuid4()),
                        'enabled': True,
                        'createSubcontext': False,
                        'subcontextSettings': self._get_default_context_config(),
                        'useCategoryDefaults': False,
                        'categoryDefaults': {},
                        'categoryBiasGroups': [],
                        'settings': {}
                    }
                elif line.startswith('ID:') and current_category:
                    current_category['id'] = line.split(':', 1)[1].strip()
                elif line.startswith('Enabled:') and current_category:
                    current_category['enabled'] = line.split(':', 1)[1].strip().lower() == 'true'
                elif line.startswith('Creates Subcontext:') and current_category:
                    current_category['createSubcontext'] = line.split(':', 1)[1].strip().lower() == 'true'
            
            elif current_section == 'entries':
                if line.startswith('ENTRY #'):
                    # Save previous entry
                    if current_entry:
                        lorebook['entries'].append(current_entry)
                    
                    # Start new entry
                    current_entry = {
                        'text': '',
                        'contextConfig': self._get_default_context_config(),
                        'lastUpdatedAt': int(datetime.now().timestamp() * 1000),
                        'displayName': '',
                        'id': str(uuid.uuid4()),
                        'keys': [],
                        'searchRange': 1000,
                        'enabled': True,
                        'forceActivation': False,
                        'keyRelative': False,
                        'nonStoryActivatable': False,
                        'category': '',
                        'loreBiasGroups': [],
                        'advancedConditions': []
                    }
                
                elif current_entry:
                    if line.startswith('Display Name:'):
                        current_entry['displayName'] = line.split(':', 1)[1].strip()
                    elif line.startswith('ID:'):
                        current_entry['id'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Category:'):
                        category_line = line.split(':', 1)[1].strip()
                        # Extract category name (before parentheses)
                        if '(' in category_line:
                            category_name = category_line.split('(')[0].strip()
                            category_id = category_line.split('(')[1].split(')')[0].strip()
                        else:
                            category_name = category_line
                            category_id = self._find_or_create_category_id(category_name, lorebook)
                        current_entry['category'] = category_id
                    elif line.startswith('Activation Keys:'):
                        keys_str = line.split(':', 1)[1].strip()
                        current_entry['keys'] = [k.strip() for k in keys_str.split(',')]
                    elif line.startswith('Enabled:'):
                        current_entry['enabled'] = line.split(':', 1)[1].strip().lower() == 'true'
                    elif line.startswith('Force Activation:'):
                        current_entry['forceActivation'] = line.split(':', 1)[1].strip().lower() == 'true'
                    elif line.startswith('Search Range:'):
                        try:
                            current_entry['searchRange'] = int(line.split(':', 1)[1].strip())
                        except:
                            pass
                    elif line.startswith('Title:'):
                        title = line.split(':', 1)[1].strip()
                        # Look ahead for description
                        description = ''
                        j = i + 1
                        while j < len(lines) and not lines[j].strip().startswith(('=', '-', 'CONTEXT', 'ADVANCED', 'LORE')):
                            if lines[j].strip().startswith('Description:'):
                                description = lines[j].strip().split(':', 1)[1].strip()
                                # Remove "Type: " prefix if it exists in description
                                if description.startswith('Type: '):
                                    description = description.split('\n', 1)[1] if '\n' in description else ''
                                break
                            j += 1
                        current_entry['text'] = f"----\n{title}\nType: {self._get_category_name(current_entry['category'], lorebook)}\n{description}"
                    elif line.startswith('Token Budget:'):
                        try:
                            current_entry['contextConfig']['tokenBudget'] = int(line.split(':', 1)[1].strip())
                        except:
                            pass
                    elif line.startswith('Budget Priority:'):
                        try:
                            current_entry['contextConfig']['budgetPriority'] = int(line.split(':', 1)[1].strip())
                        except:
                            pass
                    elif line.startswith('Trim Direction:'):
                        current_entry['contextConfig']['trimDirection'] = line.split(':', 1)[1].strip()
            
            elif current_section == 'settings':
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to convert to appropriate type
                    if value.lower() == 'true':
                        lorebook['settings'][key] = True
                    elif value.lower() == 'false':
                        lorebook['settings'][key] = False
                    elif value.isdigit():
                        lorebook['settings'][key] = int(value)
                    else:
                        lorebook['settings'][key] = value
            
            i += 1
        
        # Add final entry and category
        if current_entry:
            lorebook['entries'].append(current_entry)
        if current_category:
            lorebook['categories'].append(current_category)
        
        return lorebook
    
    def _get_default_context_config(self) -> Dict[str, Any]:
        """Get default context configuration."""
        return {
            'prefix': '',
            'suffix': '\n',
            'tokenBudget': 100,
            'reservedTokens': 0,
            'budgetPriority': 400,
            'trimDirection': 'trimBottom',
            'insertionType': 'newline',
            'maximumTrimType': 'sentence',
            'insertionPosition': -1
        }
    
    def _find_or_create_category_id(self, category_name: str, lorebook: Dict[str, Any]) -> str:
        """Find category ID by name or create a new one."""
        for category in lorebook.get('categories', []):
            if category['name'] == category_name:
                return category['id']
        
        # Create new category
        new_category = {
            'name': category_name,
            'id': str(uuid.uuid4()),
            'enabled': True,
            'createSubcontext': False,
            'subcontextSettings': self._get_default_context_config(),
            'useCategoryDefaults': False,
            'categoryDefaults': {},
            'categoryBiasGroups': [],
            'settings': {}
        }
        lorebook['categories'].append(new_category)
        return new_category['id']
    
    def _get_category_name(self, category_id: str, lorebook: Dict[str, Any]) -> str:
        """Get category name by ID."""
        for category in lorebook.get('categories', []):
            if category['id'] == category_id:
                return category['name']
        return 'Unknown'


def main():
    """Main function to handle command line arguments and execute conversion."""
    parser = argparse.ArgumentParser(
        description='Convert NovelAI lorebook files between JSON and TXT formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s lorebook.lorebook              # Convert JSON to TXT
  %(prog)s lorebook.txt --to-json         # Convert TXT to JSON
  %(prog)s lorebook.txt output.lorebook   # Convert TXT to JSON with custom output
        """
    )
    
    parser.add_argument('input_file', help='Input file path (.lorebook or .txt)')
    parser.add_argument('output_file', nargs='?', help='Output file path (optional)')
    parser.add_argument('--to-json', action='store_true', 
                       help='Force conversion to JSON format (from TXT)')
    
    args = parser.parse_args()
    
    converter = LorebookConverter()
    
    # Determine conversion direction
    input_path = Path(args.input_file)
    
    if args.to_json or input_path.suffix.lower() == '.txt':
        # Convert TXT to JSON
        output_file = args.output_file
        if not output_file and not args.to_json:
            # If input is .txt but no --to-json flag, assume user wants JSON
            output_file = str(input_path.with_suffix('.lorebook'))
        converter.txt_to_json(args.input_file, output_file)
    else:
        # Convert JSON to TXT
        converter.json_to_txt(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
