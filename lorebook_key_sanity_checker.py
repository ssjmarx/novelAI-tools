#!/usr/bin/env python3
"""
Final Improved Simple Key Sanity Checker for NovelAI Lorebooks

This script scans a lorebook and ensures that entries of specific types
include the singular form of their name in their activation keys.

Key improvements:
- Better name extraction for "Name of Place" patterns (prefers proper names)
- Multi-character name detection for "Name1 and Name2" patterns
- Redundant key checking (prevents adding keys that are subsets of existing keys)
- Expanded type synonyms including races
- Smarter name vs description detection
- Better handling of "of" patterns
"""

import json
import sys
import os
import argparse
import re
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime


class FinalSimpleKeySanityChecker:
    """Checks and fixes missing name-based keys in lorebook entries."""
    
    def __init__(self):
        # Define target types and their synonyms (expanded)
        self.type_patterns = {
            'character': ['character', 'characters', 'person', 'people', 'individual', 'npc', 'protagonist', 'antagonist'],
            'organization': ['organization', 'organisation', 'group', 'faction', 'guild', 'cult', 'company', 'order', 'society', 'clan', 'organizations'],
            'location': ['location', 'locations', 'place', 'area', 'region', 'site', 'spot', 'venue', 'destination'],
            'item': ['item', 'items', 'object', 'objects', 'artifact', 'artifacts', 'equipment', 'gear', 'tool', 'weapon', 'weaponry'],
            'race': ['race', 'races', 'species', 'subrace', 'subspecies']
        }
        
        # Common prefixes to strip from names
        self.name_prefixes = [
            'the ', 'a ', 'an ', 'lord ', 'lady ', 'king ', 'queen ', 'prince ', 'princess ',
            'duke ', 'duchess ', 'sir ', 'master ', 'mistress ', 'captain ', 'general ',
            'elder ', 'high ', 'grand ', 'arch-', 'chief ', 'head '
        ]
        
        # Common suffixes to strip from names
        self.name_suffixes = [
            ' the great', ' the wise', ' the bold', ' the strong', ' the brave', ' the mighty',
            ' the old', ' the young', ' the elder', ' the younger', ' i', ' ii', ' iii', ' iv',
            ' v', ' vi', ' vii', ' viii', ' ix', ' x', ' jr', ' sr', ' senior', ' junior'
        ]
        
        # Common English words (for name vs description detection)
        self.common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'now', 'then', 'here', 'there', 'when', 'where',
            'why', 'how', 'again', 'further', 'once', 'here', 'there',
            # Additional common words that shouldn't be keys
            'their', 'your', 'our', 'its', 'his', 'her', 'my', 'yourself', 'himself',
            'herself', 'itself', 'ourselves', 'themselves', 'myself', 'oneself'
        }
    
    def extract_entry_info(self, entry: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Extract the title, type, and description from a lorebook entry.
        """
        text = entry.get('text', '')
        display_name = entry.get('displayName', '')
        
        # Parse the text field to get title and type
        lines = text.split('\n')
        title = ""
        entry_type = ""
        description = ""
        
        for line in lines:
            if line.startswith('----'):
                continue
            elif line.startswith('Type:'):
                entry_type = line.replace('Type:', '').strip().lower()
            elif line.strip() and not line.startswith('Type:'):
                if not title:
                    title = line.strip()
                else:
                    description += line.strip() + " "
        
        # If no title found in text, use displayName
        if not title and display_name:
            title = display_name
        
        return title, entry_type, description.strip()
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize a name to its singular form by removing common prefixes and suffixes.
        """
        if not name:
            return ""
        
        # Convert to lowercase for processing
        normalized = name.lower().strip()
        
        # Remove common prefixes
        for prefix in self.name_prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        
        # Remove common suffixes
        for suffix in self.name_suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
                break
        
        # Handle plural forms (basic rules)
        if normalized.endswith('ies'):
            normalized = normalized[:-3] + 'y'
        elif normalized.endswith('es') and len(normalized) > 3:
            normalized = normalized[:-2]
        elif normalized.endswith('s') and not normalized.endswith('ss'):
            normalized = normalized[:-1]
        
        # Handle specific cases
        if normalized.endswith('cav'):
            normalized = normalized[:-3] + 'cave'
        
        return normalized.strip()
    
    def get_entry_type_category(self, entry_type: str) -> str:
        """
        Determine the category of an entry type.
        """
        entry_type_lower = entry_type.lower()
        
        for category, synonyms in self.type_patterns.items():
            if entry_type_lower in synonyms:
                return category
        
        return 'other'
    
    def should_check_entry(self, entry_type: str) -> bool:
        """
        Check if an entry type should be processed.
        """
        category = self.get_entry_type_category(entry_type)
        return category in ['character', 'organization', 'location', 'item', 'race']
    
    def extract_names_from_title(self, title: str, entry_type: str) -> List[str]:
        """
        Extract names from title, handling various patterns.
        """
        if not title:
            return []
        
        names = []
        
        # Handle "Name, Title" pattern first (highest priority)
        if ',' in title:
            name_part = title.split(',')[0].strip()
            core_name = self.extract_core_name(name_part)
            if core_name:
                names.append(core_name)
            return names
        
        # Handle "Name: Subtitle" pattern
        colon_match = re.match(r'^([^:]+):', title, re.IGNORECASE)
        if colon_match:
            core_name = self.extract_core_name(colon_match.group(1).strip())
            if core_name:
                names.append(core_name)
            return names
        
        # Handle "Name of Place" pattern - different logic for locations vs characters
        of_match = re.match(r'^([^,]+?)\s+of\s+([^,]+?)(?:\s+.+)?$', title, re.IGNORECASE)
        if of_match:
            # Get both parts
            first_part = of_match.group(1).strip()
            second_part = of_match.group(2).strip()
            
            # For locations: prefer second part (likely proper name)
            if entry_type in ['location', 'locations', 'place', 'area', 'region', 'site', 'spot', 'venue', 'destination']:
                # Prefer second part (likely proper name) if it's not a common word
                if not self.is_common_word(second_part):
                    core_place_name = self.extract_core_name(second_part)
                    if core_place_name:
                        names.append(core_place_name)
                        return names
                
                # If second part is common, try first part
                core_first_name = self.extract_core_name(first_part)
                if core_first_name:
                    names.append(core_first_name)
                
                return names
            
            # For characters: prefer first part (the person's name)
            else:
                core_person_name = self.extract_core_name(first_part)
                if core_person_name:
                    names.append(core_person_name)
                
                return names
        
        # Handle "Name1 and Name2" pattern (multi-character entries) - lowest priority
        and_match = re.search(r'^(.+?)\s+and\s+(.+?)(?:\s+.+)?$', title, re.IGNORECASE)
        if and_match:
            name1 = and_match.group(1).strip()
            name2 = and_match.group(2).strip()
            
            # Extract core names (remove titles, etc.)
            core_name1 = self.extract_core_name(name1)
            core_name2 = self.extract_core_name(name2)
            
            if core_name1:
                names.append(core_name1)
            if core_name2:
                names.append(core_name2)
            
            return names
        
        # Default: extract core name from full title
        core_name = self.extract_core_name(title)
        if core_name:
            names.append(core_name)
        
        return names
    
    def extract_core_name(self, name: str) -> str:
        """
        Extract the core name from a title/name.
        """
        if not name:
            return ""
        
        # Remove common title patterns
        core_name = name.strip()
        
        # Handle patterns like "Name the Adjective"
        match = re.match(r'^([^,]+?)\s+the\s+.+$', core_name, re.IGNORECASE)
        if match:
            core_name = match.group(1).strip()
        
        # Handle patterns like "Name, Title"
        if ',' in core_name:
            core_name = core_name.split(',')[0].strip()
        
        # Remove prefixes and normalize
        normalized = self.normalize_name(core_name)
        
        return normalized
    
    def is_common_word(self, word: str) -> bool:
        """
        Check if a word is a common English word.
        """
        return word.lower() in self.common_words
    
    def is_redundant_key(self, new_key: str, existing_keys: List[str]) -> bool:
        """
        Check if adding this key would be redundant.
        """
        new_key_lower = new_key.lower()
        
        for existing_key in existing_keys:
            existing_key_lower = existing_key.lower()
            
            # If new key is contained in existing key or vice versa
            if (new_key_lower in existing_key_lower or 
                existing_key_lower in new_key_lower):
                return True
        
        return False
    
    def check_and_fix_entry(self, entry: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, List[str]]:
        """
        Check and fix a single lorebook entry.
        """
        title, entry_type, description = self.extract_entry_info(entry)
        current_keys = entry.get('keys', [])
        
        # Skip if this entry type shouldn't be checked
        if not self.should_check_entry(entry_type):
            return entry, False, []
        
        # Extract names from title
        names = self.extract_names_from_title(title, entry_type)
        
        if not names:
            return entry, False, []
        
        changes_made = []
        updated_keys = current_keys.copy()
        was_modified = False
        
        for name in names:
            if not name:
                continue
            
            # Skip common words
            if self.is_common_word(name):
                changes_made.append(f"Skipped common word: '{name}'")
                continue
            
            # Check if name is already in keys (case-insensitive)
            name_in_keys = any(name.lower() == key.lower() for key in updated_keys)
            
            if not name_in_keys:
                # Check for redundancy
                if not self.is_redundant_key(name, updated_keys):
                    updated_keys.append(name)
                    changes_made.append(f"Added missing name key: '{name}'")
                    was_modified = True
                else:
                    changes_made.append(f"Skipped redundant key: '{name}'")
        
        # Special case: for names ending in "ves", also add singular form with "f"
        # This should check the original title before normalization
        if title.lower().endswith('ves'):
            # Extract the base name before normalization
            base_name = title.lower()
            if base_name.endswith('ves'):
                singular_f_form = base_name[:-3] + 'f'
                # Check if singular form is already in keys
                singular_f_in_keys = any(singular_f_form.lower() == key.lower() for key in updated_keys)
                if not singular_f_in_keys and not self.is_redundant_key(singular_f_form, updated_keys):
                    updated_keys.append(singular_f_form)
                    changes_made.append(f"Added missing name key: '{singular_f_form}'")
        
        if was_modified or len(changes_made) > 0:
            updated_entry = entry.copy()
            updated_entry['keys'] = updated_keys
            updated_entry['lastUpdatedAt'] = int(datetime.now().timestamp() * 1000)
            return updated_entry, True, changes_made
        
        return entry, False, []
    
    def check_lorebook(self, input_file: str, output_file: str = None, check_only: bool = False) -> None:
        """
        Check and optionally fix the entire lorebook.
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lorebook = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{input_file}': {e}")
            sys.exit(1)
        
        entries = lorebook.get('entries', [])
        if not entries:
            print("Warning: No entries found in lorebook.")
            return
        
        print(f"Checking {len(entries)} entries for missing name keys...")
        print(f"Target types: character, organization, location, item, race")
        print()
        
        processed_entries = []
        total_issues_found = 0
        entries_fixed = 0
        
        for i, entry in enumerate(entries, 1):
            title, entry_type, description = self.extract_entry_info(entry)
            
            if not self.should_check_entry(entry_type):
                print(f"Entry {i:3d}: '{title}' - Skipped (type: {entry_type})")
                processed_entries.append(entry)
                continue
            
            updated_entry, was_modified, changes = self.check_and_fix_entry(entry)
            
            if changes:
                total_issues_found += len([c for c in changes if not c.startswith("Skipped")])
                entries_fixed += 1
                print(f"Entry {i:3d}: '{title}' - ISSUES FOUND")
                print(f"  Type: {entry_type}")
                for change in changes:
                    print(f"  - {change}")
                print(f"  Current keys: {', '.join(updated_entry['keys'])}")
            else:
                print(f"Entry {i:3d}: '{title}' - OK (type: {entry_type})")
            
            processed_entries.append(updated_entry)
        
        print()
        print("="*60)
        if check_only:
            print("CHECK RESULTS (READ-ONLY)")
        else:
            print("SANITY CHECK RESULTS")
        print("="*60)
        print(f"Total entries processed: {len(entries)}")
        print(f"Entries with issues: {entries_fixed}")
        print(f"Total issues found: {total_issues_found}")
        
        if not check_only and total_issues_found > 0:
            # Create the new lorebook
            new_lorebook = {
                "lorebookVersion": lorebook.get("lorebookVersion", 6),
                "entries": processed_entries,
                "categories": lorebook.get("categories", []),
                "settings": lorebook.get("settings", {})
            }
            
            # Save the updated lorebook
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(new_lorebook, f, indent=2, ensure_ascii=False)
                print(f"Fixed lorebook saved to: {output_file}")
            except Exception as e:
                print(f"Error saving lorebook: {e}")
                sys.exit(1)
        elif check_only and total_issues_found > 0:
            print("Run with output file to fix these issues.")
        else:
            print("No issues found! All entries have proper name keys.")
        
        print("="*60)


def main():
    """Main function to handle command line arguments and execute sanity check."""
    parser = argparse.ArgumentParser(
        description='Check and fix missing name keys in NovelAI lorebook entries (Final Improved Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s lorebook.lorebook                    # Check and fix, auto-generate output
  %(prog)s lorebook.lorebook fixed.lorebook    # Check and fix with custom output
  %(prog)s lorebook.lorebook --check-only       # Check only, don't modify
        """
    )
    
    parser.add_argument('input_file', help='Input lorebook file (.lorebook)')
    parser.add_argument('output_file', nargs='?', 
                       help='Output lorebook file (optional, auto-generated if not provided)')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check for issues, don\'t modify the file')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided and not check-only
    if not args.output_file and not args.check_only:
        input_path = os.path.splitext(args.input_file)
        output_file = f"{input_path[0]}_sanity_checked_final{input_path[1]}"
    elif args.check_only:
        output_file = None
    else:
        output_file = args.output_file
    
    print(f"Input: {args.input_file}")
    if output_file:
        print(f"Output: {output_file}")
    if args.check_only:
        print("Mode: Check only (read-only)")
    print()
    
    # Process the lorebook
    checker = FinalSimpleKeySanityChecker()
    checker.check_lorebook(args.input_file, output_file, args.check_only)


if __name__ == "__main__":
    main()
