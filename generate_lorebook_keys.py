#!/usr/bin/env python3
"""
Script to generate keys for NovelAI lorebook entries using AI
"""

import asyncio
import json
import re
import sys
import os
from datetime import datetime
from novelai_api import NovelAIAPI
from novelai_api.GlobalSettings import GlobalSettings
from novelai_api.Preset import Model, Preset
from novelai_api.Tokenizer import Tokenizer
from novelai_api.utils import b64_to_tokens


class LorebookKeyGenerator:
    def __init__(self, min_keys=4, max_keys=10):
        self.min_keys = min_keys
        self.max_keys = max_keys
        self.api = None
        
    async def login(self):
        """Login to NovelAI API"""
        self.api = NovelAIAPI()
        
        # Prompt user for API token instead of reading from file
        token = input("Enter your NovelAI API token: ").strip()
        if not token:
            print("Error: No API token provided!")
            return False
            
        print("Connecting to NovelAI...")
        await self.api.high_level.login_with_token(token)
        print("Login successful!")
        return True
        
    def extract_entry_info(self, entry):
        """Extract relevant information from a lorebook entry"""
        # Parse the text field to get title and description
        text = entry.get('text', '')
        
        # Split by newlines and find the title and type
        lines = text.split('\n')
        title = ""
        entry_type = ""
        description = ""
        
        for line in lines:
            if line.startswith('----'):
                continue
            elif line.startswith('Type:'):
                entry_type = line.replace('Type:', '').strip()
            elif line.strip() and not line.startswith('Type:'):
                if not title:
                    title = line.strip()
                else:
                    description += line.strip() + " "
        
        return {
            'title': title,
            'type': entry_type,
            'description': description.strip(),
            'display_name': entry.get('displayName', ''),
            'current_keys': entry.get('keys', [])
        }
        
    def create_generation_prompt(self, entry_info):
        """Create an instruction prompt for key generation"""
        title = entry_info['title']
        entry_type = entry_info['type']
        description = entry_info['description']
        current_keys = entry_info['current_keys']
        
        # Include original examples to show what we want
        prompt = f"""Examples of completed entries:

----
Quantum Plasma Rifle
Type: item
A prototype energy weapon that fires superheated plasma bolts capable of melting through armor plating. The rifle's power core must be recharged after every fifty shots.
Tags: weapon, plasma, rifle, prototype, energy weapon, military, sci-fi

----
Neo-Tokyo District 7
Type: location
A sprawling cyberpunk metropolis where neon signs illuminate perpetual rain. Towering skyscrapers house corporate offices while street level markets sell illegal cybernetic enhancements.
Tags: city, cyberpunk, neon, futuristic, district, tokyo, rain, corporate

----
Detective Sarah Chen
Type: person
A hard-boiled private investigator with cybernetic eye implants and a troubled past. She specializes in cases involving corporate espionage and missing persons in the neon-drenched streets of Neo-Tokyo.
Tags: detective, cybernetic, investigator, private eye, chen, neo-tokyo, missing persons

Now complete this entry with appropriate keys:

----
{title}
Type: {entry_type}
{description}
Tags:"""
        
        return prompt
        
    def clean_generated_keys(self, raw_text):
        """Clean and parse the AI-generated keys"""
        # Remove any explanatory text and extract just the first line of keys
        text = raw_text.strip()
        
        # Stop at four dashes if present (AI started generating new entries)
        if '----' in text:
            text = text.split('----')[0].strip()
        
        # Take only the first line if there are multiple lines
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else text.strip()
        
        # Look for comma-separated keys on the first line
        if ',' in first_line:
            keys_text = first_line
        else:
            # Try to extract from numbered list on first line
            numbered_match = re.search(r'(?:\d+[\.\)]\s*([^\n]+)', first_line)
            if numbered_match:
                keys_text = numbered_match.group(1)
            else:
                # If no commas or numbers, treat the whole first line as one key
                keys_text = first_line
        
        # Clean up the keys text
        keys = []
        for key in keys_text.split(','):
            key = key.strip()
            # Remove any remaining formatting
            key = re.sub(r'^\d+[\.\)]\s*', '', key)  # Remove numbering
            key = re.sub(r'^[-*]\s*', '', key)  # Remove bullet points
            key = re.sub(r'^["\']|["\']$', '', key)  # Remove quotes
            key = key.strip()
            if key and len(key) > 0:
                keys.append(key)
        
        # Filter to valid keys and limit count
        valid_keys = []
        for key in keys:
            if len(key) > 0 and len(key) <= 50:  # Reasonable length limit
                valid_keys.append(key)
        
        return valid_keys[:self.max_keys]  # Limit to max_keys
        
    async def generate_keys_for_entry(self, entry_info):
        """Generate keys for a single lorebook entry"""
        prompt = self.create_generation_prompt(entry_info)
        
        # Create preset for key generation (focused, concise output)
        preset = Preset("key_generation", Model.Kayra, {
            "temperature": 0.3,  # Lower temperature for more consistent output
            "max_length": 80,   # Short output to force conciseness
            "min_length": 20,   # Ensure we get enough keys
            "top_p": 0.8,
            "repetition_penalty": 1.2,
            "repetition_penalty_range": 100,
            "top_k": 10
        })
        
        global_settings = GlobalSettings(num_logprobs=GlobalSettings.NO_LOGPROBS)
        
        print(f"\n{'='*60}")
        print(f"Entry: {entry_info['display_name']}")
        print(f"Type: {entry_info['type']}")
        print(f"Description: {entry_info['description'][:100]}...")
        print(f"Current keys: {len(entry_info['current_keys'])}")
        print(f"{'='*60}")
        
        try:
            result = await self.api.high_level.generate(
                prompt,
                Model.Kayra,
                preset,
                global_settings
            )
            
            # Decode the result
            generated_tokens = b64_to_tokens(result["output"], 2)  # Kayra uses 2 bytes per token
            generated_text = Tokenizer.decode(Model.Kayra, generated_tokens)
            
            print(f"AI Response: {generated_text}")
            
            # Clean and validate the generated keys
            cleaned_keys = self.clean_generated_keys(generated_text)
            
            if len(cleaned_keys) < self.min_keys:
                print(f"Warning: Only generated {len(cleaned_keys)} keys (minimum: {self.min_keys})")
                print("You can:")
                print("1. Accept these keys and continue")
                print("2. Regenerate this entry")
                print("3. Skip this entry")
                print("4. Retry this entry")
                
                choice = input("Your choice (1/2/3/4): ").strip()
                if choice == '2':
                    return await self.generate_keys_for_entry(entry_info)
                elif choice == '3':
                    return entry_info['current_keys']  # Return existing keys
                elif choice == '4':
                    return await self.generate_keys_for_entry(entry_info)
                elif choice != '1':
                    print("Invalid choice. Continuing with generated keys...")
            
            print(f"Generated {len(cleaned_keys)} keys: {', '.join(cleaned_keys)}")
            
            # Always provide user options
            print("\nYou can:")
            print("1. Accept these keys and continue")
            print("2. Regenerate this entry")
            print("3. Skip this entry")
            print("4. Retry this entry")
            
            choice = input("Your choice (1/2/3/4): ").strip()
            if choice == '2':
                return await self.generate_keys_for_entry(entry_info)
            elif choice == '3':
                return entry_info['current_keys']  # Return existing keys
            elif choice == '4':
                return await self.generate_keys_for_entry(entry_info)
            elif choice != '1':
                print("Invalid choice. Continuing with generated keys...")
            
            return cleaned_keys
            
        except Exception as e:
            print(f"Error generating keys: {e}")
            return entry_info['current_keys']  # Return existing keys on error
            
    async def process_lorebook(self, input_file, output_file):
        """Process the entire lorebook"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lorebook = json.load(f)
        except Exception as e:
            print(f"Error reading lorebook: {e}")
            return
            
        print(f"\nProcessing {len(lorebook['entries'])} entries...")
        
        processed_entries = []
        entries_updated = 0
        
        for i, entry in enumerate(lorebook['entries']):
            entry_info = self.extract_entry_info(entry)
            current_keys = entry_info['current_keys']
            
            # Check if entry needs new keys
            if len(current_keys) >= self.min_keys:
                print(f"\nEntry {i+1}/{len(lorebook['entries'])}: '{entry_info['display_name']}' - Already has {len(current_keys)} keys")
                processed_entries.append(entry)
                continue
                
            # Entry needs keys generation
            print(f"\nEntry {i+1}/{len(lorebook['entries'])}: '{entry_info['display_name']}' - Needs keys")
            
            # Wait for user initiation (NovelAI requirement)
            input("Press Enter to initiate key generation for this entry...")
            
            # Generate keys
            new_keys = await self.generate_keys_for_entry(entry_info)
            
            # Update the entry with new keys
            updated_entry = entry.copy()
            updated_entry['keys'] = new_keys
            updated_entry['lastUpdatedAt'] = int(datetime.now().timestamp() * 1000)
            processed_entries.append(updated_entry)
            entries_updated += 1
            
            # Update entry_info for next iteration
            entry_info['current_keys'] = new_keys
            
            print(f"✓ Keys updated for '{entry_info['display_name']}'")
        
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
            print(f"\n✓ Updated lorebook saved to: {output_file}")
            print(f"✓ Processed {len(lorebook['entries'])} entries, updated {entries_updated} entries")
        except Exception as e:
            print(f"Error saving lorebook: {e}")


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python generate_lorebook_keys.py <input_lorebook> [output_lorebook]")
        print("Example: python generate_lorebook_keys.py 'Sleeper's Dream (Wed Oct 29 2025).lorebook'")
        return
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Generate output filename based on input
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_with_keys.lorebook"
    
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    generator = LorebookKeyGenerator()
    
    # Login to API
    if not await generator.login():
        return
    
    # Process the lorebook
    await generator.process_lorebook(input_file, output_file)
    
    print("\n" + "="*50)
    print("Lorebook key generation complete!")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
