#!/usr/bin/env python3
"""
Script to reduce the number of activation keys in NovelAI lorebook entries

This script takes a lorebook JSON file and reduces the number of activation keys
in each entry to a specified maximum, keeping the most relevant keys.

Usage:
    python reduce_lorebook_keys.py input.lorebook [max_keys] [output.lorebook]
    python reduce_lorebook_keys.py input.lorebook 5 reduced.lorebook
"""

import json
import sys
import os
import argparse
from typing import List, Dict, Any
from datetime import datetime


class LorebookKeyReducer:
    """Handles reduction of activation keys in lorebook entries."""
    
    def __init__(self, max_keys: int = 5):
        self.max_keys = max_keys
        
    def prioritize_keys(self, keys: List[str], entry_text: str = "") -> List[str]:
        """
        Prioritize keys based on relevance and importance.
        
        Args:
            keys: List of current activation keys
            entry_text: The text content of the entry for context
            
        Returns:
            Prioritized list of keys
        """
        if len(keys) <= self.max_keys:
            return keys
        
        # Convert to lowercase for case-insensitive comparison
        keys_lower = [k.lower() for k in keys]
        entry_text_lower = entry_text.lower()
        
        # Scoring system for keys
        key_scores = []
        
        for i, key in enumerate(keys):
            key_lower = keys_lower[i]
            score = 0
            
            # Higher score for keys that appear in the entry text
            if key_lower in entry_text_lower:
                score += 10
            
            # Higher score for longer, more specific keys
            score += len(key) * 0.5
            
            # Lower score for very common words
            common_words = {
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
                'why', 'how', 'again', 'further', 'once', 'here', 'there'
            }
            
            if key_lower in common_words:
                score -= 5
            
            # Higher score for keys that contain numbers or special characters (more specific)
            if any(c.isdigit() for c in key):
                score += 2
            
            # Higher score for compound words (contain spaces or hyphens)
            if ' ' in key or '-' in key:
                score += 1
            
            # Higher score for proper nouns (starts with capital letter)
            if key and key[0].isupper():
                score += 1
            
            key_scores.append((score, key, i))
        
        # Sort by score (descending), then by original position (ascending) for tie-breaking
        key_scores.sort(key=lambda x: (-x[0], x[2]))
        
        # Take the top keys
        prioritized_keys = [key for _, key, _ in key_scores[:self.max_keys]]
        
        return prioritized_keys
    
    def reduce_entry_keys(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reduce the number of keys in a single lorebook entry.
        
        Args:
            entry: A single lorebook entry dictionary
            
        Returns:
            Updated entry with reduced keys
        """
        current_keys = entry.get('keys', [])
        entry_text = entry.get('text', '')
        
        if len(current_keys) <= self.max_keys:
            return entry
        
        # Prioritize and reduce keys
        reduced_keys = self.prioritize_keys(current_keys, entry_text)
        
        # Create updated entry
        updated_entry = entry.copy()
        updated_entry['keys'] = reduced_keys
        updated_entry['lastUpdatedAt'] = int(datetime.now().timestamp() * 1000)
        
        return updated_entry
    
    def process_lorebook(self, input_file: str, output_file: str) -> None:
        """
        Process the entire lorebook and reduce keys in all entries.
        
        Args:
            input_file: Path to input lorebook file
            output_file: Path to output lorebook file
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
        
        print(f"Processing {len(entries)} entries...")
        print(f"Reducing keys to maximum of {self.max_keys} per entry")
        
        processed_entries = []
        total_keys_removed = 0
        entries_modified = 0
        
        for i, entry in enumerate(entries, 1):
            current_keys = entry.get('keys', [])
            original_count = len(current_keys)
            
            # Process the entry
            updated_entry = self.reduce_entry_keys(entry)
            new_keys = updated_entry.get('keys', [])
            new_count = len(new_keys)
            
            keys_removed = original_count - new_count
            total_keys_removed += keys_removed
            
            if keys_removed > 0:
                entries_modified += 1
                print(f"Entry {i:3d}: '{entry.get('displayName', 'Unknown')}' - "
                      f"Reduced from {original_count} to {new_count} keys "
                      f"(removed {keys_removed})")
                print(f"  Original: {', '.join(current_keys)}")
                print(f"  Reduced:  {', '.join(new_keys)}")
            else:
                print(f"Entry {i:3d}: '{entry.get('displayName', 'Unknown')}' - "
                      f"No reduction needed ({original_count} keys)")
            
            processed_entries.append(updated_entry)
        
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
            
            print(f"\n" + "="*60)
            print("KEY REDUCTION SUMMARY")
            print("="*60)
            print(f"Total entries processed: {len(entries)}")
            print(f"Entries modified: {entries_modified}")
            print(f"Total keys removed: {total_keys_removed}")
            print(f"Average keys per entry (after): {sum(len(e.get('keys', [])) for e in processed_entries) / len(processed_entries):.1f}")
            print(f"Output saved to: {output_file}")
            print("="*60)
            
        except Exception as e:
            print(f"Error saving lorebook: {e}")
            sys.exit(1)


def main():
    """Main function to handle command line arguments and execute key reduction."""
    parser = argparse.ArgumentParser(
        description='Reduce the number of activation keys in NovelAI lorebook entries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s lorebook.lorebook                    # Reduce to 5 keys (default)
  %(prog)s lorebook.lorebook 3                  # Reduce to 3 keys
  %(prog)s lorebook.lorebook 5 reduced.lorebook # Reduce to 5 keys, custom output
        """
    )
    
    parser.add_argument('input_file', help='Input lorebook file (.lorebook)')
    parser.add_argument('max_keys', nargs='?', type=int, default=5,
                       help='Maximum number of keys per entry (default: 5)')
    parser.add_argument('output_file', nargs='?', 
                       help='Output lorebook file (optional, auto-generated if not provided)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.max_keys < 1:
        print("Error: max_keys must be at least 1")
        sys.exit(1)
    
    # Generate output filename if not provided
    if not args.output_file:
        input_path = os.path.splitext(args.input_file)
        output_file = f"{input_path[0]}_reduced_to_{args.max_keys}_keys{input_path[1]}"
    else:
        output_file = args.output_file
    
    print(f"Input: {args.input_file}")
    print(f"Output: {output_file}")
    print(f"Maximum keys per entry: {args.max_keys}")
    print()
    
    # Process the lorebook
    reducer = LorebookKeyReducer(args.max_keys)
    reducer.process_lorebook(args.input_file, output_file)


if __name__ == "__main__":
    main()
