#!/usr/bin/env python
"""
Core 2000 Anki Deck Generator

This script generates an Anki deck in the Core 2000 format from a Japanese vocabulary CSV file.
The Core 2000 format features:
1. Recognition cards (Japanese → English) 
2. Production cards (English → Japanese)
3. Special formatting for Japanese vocabulary
4. Audio support
"""

import os
import sys
import argparse
from app.services.anki_utils import create_core2000_package_from_csv

def create_core2000_deck(input_csv_path, output_path=None, deck_name=None):
    """
    Create a Core 2000 style Anki deck from a CSV file
    
    Args:
        input_csv_path: Path to the CSV file
        output_path: Path for the output .apkg file (optional)
        deck_name: Name for the Anki deck (optional)
    
    Returns:
        Path to the created .apkg file
    """
    # Validate input file
    if not os.path.exists(input_csv_path):
        print(f"Error: Input file '{input_csv_path}' does not exist.")
        return None
    
    # Read CSV content
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return None
    
    # Set default deck name based on input filename if not provided
    if not deck_name:
        base_name = os.path.splitext(os.path.basename(input_csv_path))[0]
        deck_name = f"Core 2000 - {base_name}"
    
    # Set default output path if not provided
    if not output_path:
        output_dir = os.path.dirname(os.path.abspath(input_csv_path))
        output_filename = f"{os.path.splitext(os.path.basename(input_csv_path))[0]}_core2000.apkg"
        output_path = os.path.join(output_dir, output_filename)
    
    print(f"Creating Core 2000 style Anki deck: '{deck_name}'")
    print(f"Input CSV: {input_csv_path}")
    print(f"Output will be saved to: {output_path}")
    
    try:
        # Create the Core 2000 package
        package = create_core2000_package_from_csv(csv_content, deck_name)
        
        # Write the package to the output path
        package.write_to_file(output_path)
        
        print(f"\n✅ Success! Core 2000 style Anki deck created at: {output_path}")
        print("\nImport this .apkg file into Anki to use your Core 2000 style vocabulary deck.")
        print("The deck includes both Recognition (JP→EN) and Production (EN→JP) card types.")
        
        return output_path
    except Exception as e:
        print(f"\n❌ Error creating Core 2000 deck: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Create a Core 2000 style Anki deck from a CSV file')
    
    parser.add_argument('csv_file', help='Path to the input CSV file')
    parser.add_argument('-o', '--output', help='Output path for the Anki package (.apkg file)')
    parser.add_argument('-n', '--name', help='Name for the Anki deck')
    
    args = parser.parse_args()
    
    create_core2000_deck(args.csv_file, args.output, args.name)

if __name__ == "__main__":
    main()
