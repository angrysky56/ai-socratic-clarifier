#!/usr/bin/env python3
"""
Script to initialize custom detection patterns.
This creates a custom_patterns directory and adds some default patterns.
"""

import os
import json

def ensure_dir(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def write_patterns(filename, patterns):
    """Write patterns to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(patterns, f, indent=2)
    print(f"Wrote {len(patterns)} patterns to {filename}")

def main():
    """Initialize custom detection patterns."""
    # Create custom_patterns directory
    patterns_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_patterns')
    ensure_dir(patterns_dir)
    
    # Initialize vague term patterns
    vague_patterns = [
        r'\b(?:significant|substantial|several|various|most|many|some|few)\b',
        r'\b(?:recently|soon|later|earlier|sometimes|occasionally|often|frequently)\b',
        r'\b(?:good|bad|better|worse|best|worst|greatest|improved|effective)\b'
    ]
    write_patterns(os.path.join(patterns_dir, 'vague.json'), vague_patterns)
    
    # Initialize gender bias patterns
    gender_bias_patterns = [
        r'\b(?:mankind|manpower|manmade|chairman|policeman|fireman|stewardess|mailman)\b',
        r'\b(?:he|his|him)\b(?:\s+or\s+(?:she|her))?'  # Male default
    ]
    write_patterns(os.path.join(patterns_dir, 'gender_bias.json'), gender_bias_patterns)
    
    # Initialize stereotype patterns
    stereotype_patterns = [
        r'\ball\s+(?:\w+\s+)*(?:women|men|asians|africans|latinos|elderly|millennials)\s+(?:are|have|do)\b',
        r'\b(?:women|men)\s+(?:are better|are worse|can\'t|always|never)\b',
        r'\b(?:USA|America|United States|country)\s+(?:is|are)\s+(?:the\s+)?(?:greatest|best|worst|most)\b'
    ]
    write_patterns(os.path.join(patterns_dir, 'stereotype.json'), stereotype_patterns)
    
    # Initialize non-inclusive patterns
    non_inclusive_patterns = [
        r'\b(?:blacklist|whitelist|master|slave|crazy|insane|lame|retarded|crippled)\b',
        r'\b(?:illegal alien|colored people|oriental|gypped|jewed|ghetto)\b'
    ]
    write_patterns(os.path.join(patterns_dir, 'non_inclusive.json'), non_inclusive_patterns)
    
    print("Custom patterns initialization complete!")

if __name__ == "__main__":
    main()
