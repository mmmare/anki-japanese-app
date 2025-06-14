#!/usr/bin/env python
"""
Test script to specifically debug Anki .apkg generation
"""

import os
import random
import genanki
import textwrap
import hashlib
from datetime import datetime
from io import StringIO
import csv

# The sample CSV content in tab-separated format
ANKI_FORMAT_CSV = """#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front	Back	Tags
こんにちは	Hello	greeting
ありがとう	Thank you	greeting
さようなら	Goodbye	greeting
はい	Yes	basic
いいえ	No	basic"""

# Sample in standard CSV format
STANDARD_CSV = """Japanese,English,Tags
こんにちは,Hello,greeting
ありがとう,Thank you,greeting
さようなら,Goodbye,greeting
はい,Yes,basic
いいえ,No,basic"""

# Sample with commas in fields
COMPLEX_CSV = """Japanese,English,Reading,Example,Tags
猫,"cat, feline",ねこ,"猫が好きです, とても可愛いです (I like cats, they are very cute)",animal house
犬,"dog, canine",いぬ,"犬は友達です, 散歩が好きです (Dogs are friends, they like walks)","animal, pet"
本,"book, novel",ほん,"本を読みます, 面白いです (I read a book, it's interesting)",object library"""

# Sample with commas in Anki tab format
COMPLEX_ANKI_FORMAT = """#separator:tab
#html:true
Japanese\tEnglish\tReading\tExample\tTags
猫\tcat, feline\tねこ\t猫が好きです, とても可愛いです (I like cats, they are very cute)\tanimal house
犬\tdog, canine\tいぬ\t犬は友達です, 散歩が好きです (Dogs are friends, they like walks)\tanimal, pet
本\tbook, novel\tほん\t本を読みます, 面白いです (I read a book, it's interesting)\tobject library"""

def debug_csv_parsing(csv_content, dialect='excel'):
    """Print detailed debugging information about CSV parsing"""
    print(f"\n{'='*80}")
    print(f"CSV DEBUG: Analyzing CSV content with dialect '{dialect}'")
    print(f"{'='*80}")
    
    print(f"\nFirst 200 characters:\n{csv_content[:200]}")
    print(f"\nContent length: {len(csv_content)} characters")
    print(f"\nFirst 5 lines:")
    
    lines = csv_content.strip().split('\n')
    for i, line in enumerate(lines[:5]):
        print(f"Line {i}: {line}")
    
    if len(lines) > 5:
        print(f"... (total {len(lines)} lines)")
    
    # Check for Anki format directives
    is_anki_format = csv_content.strip().startswith('#separator')
    print(f"\nIs Anki format: {is_anki_format}")
    
    if is_anki_format:
        for line in lines:
            if line.startswith('#'):
                print(f"Directive: {line}")
            else:
                break
        
        # Determine separator
        separator = '\t' if '#separator:tab' in lines[0].lower() else ','
        sep_repr = '\\t' if separator == '\t' else separator
        print(f"Separator: '{separator}' (represented as {sep_repr})")
    
    # Try to parse with CSV reader
    try:
        csv_file = StringIO(csv_content)
        csv_reader = csv.reader(csv_file, dialect=dialect)
        rows = list(csv_reader)
        print(f"\nSuccessfully parsed {len(rows)} rows with CSV reader")
        
        # Show first few rows
        for i, row in enumerate(rows[:3]):
            print(f"Row {i}: {row}")
        
        if len(rows) > 3:
            print(f"... (remaining rows omitted)")
            
    except Exception as e:
        print(f"\nError parsing with CSV reader: {e}")
    
    # Try to parse with fallback method
    print(f"\n{'-'*80}")
    print("Using robust parsing method:")
    
    try:
        rows = []
        for line in lines:
            if line.startswith('#'):
                continue
            
            # For tab-separated data
            if '\t' in line:
                # More robust tab parsing with quote handling
                field_values = []
                current_field = ""
                in_quotes = False
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == '\t' and not in_quotes:
                        field_values.append(current_field)
                        current_field = ""
                    else:
                        current_field += char
                        
                # Add the last field
                field_values.append(current_field)
                rows.append(field_values)
            else:
                # For comma-separated data with manual quote handling
                field_values = []
                current_field = ""
                in_quotes = False
                
                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        field_values.append(current_field)
                        current_field = ""
                    else:
                        current_field += char
                        
                # Add the last field
                field_values.append(current_field)
                rows.append(field_values)
        
        print(f"Successfully parsed {len(rows)} rows with robust method")
        
        # Show first few rows
        for i, row in enumerate(rows[:3]):
            print(f"Row {i}: {row}")
        
        if len(rows) > 3:
            print(f"... (remaining rows omitted)")
            
    except Exception as e:
        print(f"Error parsing with robust method: {e}")
    
    print(f"\n{'-'*80}")
    print("Checking for commas within fields in tab-separated data:")
    
    if is_anki_format and '#separator:tab' in lines[0].lower():
        has_commas_in_fields = False
        for line in lines:
            if line.startswith('#'):
                continue
            if '\t' in line and ',' in line:
                has_commas_in_fields = True
                print(f"Found line with tabs and commas: {line}")
        
        if not has_commas_in_fields:
            print("No commas found within fields in tab-separated data")
    else:
        print("Not a tab-separated Anki format file")
    
    print(f"\n{'='*80}")
    print("End of CSV parsing debug")
    print(f"{'='*80}\n")

def create_anki_package(csv_content, deck_name="Japanese Vocab Test"):
    """Create an Anki .apkg file directly using genanki"""
    try:
        print(f"\nCreating Anki package for deck: {deck_name}")
        
        # Standard Basic model ID from Anki
        model_id = 1607392319
        
        # Create a model that matches Basic type
        model = genanki.Model(
            model_id,
            'Basic',
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
                },
            ],
            css=textwrap.dedent("""\
                .card {
                    font-family: arial;
                    font-size: 20px;
                    text-align: center;
                    color: black;
                    background-color: white;
                }
            """)
        )
        
        # Create a deterministic deck ID
        deck_id = random.randrange(1 << 30, 1 << 31)
        anki_deck = genanki.Deck(deck_id, deck_name)
        
        print(f"Using Model ID: {model_id}, Deck ID: {deck_id}")
        
        # Parse the CSV content
        is_anki_format = csv_content.strip().startswith("#separator")
        
        if is_anki_format:
            print("Detected Anki format CSV")
            lines = csv_content.strip().split('\n')
            metadata_count = 0
            dialect = 'excel-tab' if "#separator:tab" in lines[0].lower() else 'excel'
            
            for line in lines:
                if line.startswith('#'):
                    metadata_count += 1
                else:
                    break
                    
            csv_content = '\n'.join(lines[metadata_count:])
        else:
            print("Using standard CSV format")
            dialect = 'excel'
        
        print(f"CSV dialect: {dialect}")
        first_line = csv_content.split('\n')[0] if '\n' in csv_content else csv_content
        print(f"First line: {first_line}")
        
        csv_file = StringIO(csv_content)
        csv_reader = csv.reader(csv_file, dialect=dialect)
        
        # Skip header if standard CSV
        if not is_anki_format:
            next(csv_reader, None)
        
        cards_added = 0
        
        for row in csv_reader:
            if len(row) < 2:
                continue
                
            front = row[0].strip()
            back = row[1].strip()
            
            if not front or not back:
                continue
                
            tags = []
            if len(row) >= 3 and row[2].strip():
                # Standard approach: single-word tags
                raw_tags = row[2].split()
                for tag in raw_tags:
                    clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag)
                    if clean_tag:
                        tags.append(clean_tag)
        
            print(f"Adding note: Front='{front}', Back='{back}', Tags={tags}")
            
            note = genanki.Note(
                model=model,
                fields=[front, back],
                tags=tags
            )
            anki_deck.add_note(note)
            cards_added += 1
        
        if cards_added == 0:
            raise ValueError("No cards were added to the deck")
            
        print(f"Added {cards_added} cards to the deck")
        
        # Create package
        package = genanki.Package([anki_deck])
        
        # Save to file
        output_path = f"{deck_name.replace(' ', '_')}.apkg"
        package.write_to_file(output_path)
        print(f"Package saved to {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

# Test with all formats
if __name__ == "__main__":
    import sys
    
    # If a file is provided as argument, use it
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            custom_csv = f.read()
            
        print(f"=== Testing with user-provided file: {sys.argv[1]} ===")
        # Debug parsing first
        debug_csv_parsing(custom_csv, 'excel')
        if custom_csv.strip().startswith('#separator:tab'):
            debug_csv_parsing(custom_csv, 'excel-tab')
            
        # Try creating package
        custom_path = create_anki_package(custom_csv, "Custom CSV Test")
        if custom_path:
            print(f"\nCustom package created: {os.path.abspath(custom_path)}")
            print(f"File size: {os.path.getsize(custom_path)} bytes")
    else:
        # Test with our predefined samples
        print("=== Testing with Standard Anki Format ===")
        anki_format_path = create_anki_package(ANKI_FORMAT_CSV, "Anki Format Test")
        
        print("\n=== Testing with Standard CSV Format ===")
        standard_csv_path = create_anki_package(STANDARD_CSV, "Standard CSV Test")
        
        print("\n=== Testing with Complex CSV Format (commas in fields) ===")
        debug_csv_parsing(COMPLEX_CSV, 'excel')
        complex_csv_path = create_anki_package(COMPLEX_CSV, "Complex CSV Test")
        
        print("\n=== Testing with Complex Anki Format (tabs + commas) ===")
        debug_csv_parsing(COMPLEX_ANKI_FORMAT, 'excel-tab')
        complex_anki_path = create_anki_package(COMPLEX_ANKI_FORMAT, "Complex Anki Format Test")
        
        # Report on all created files
        for name, path in [
            ("Anki Format", anki_format_path),
            ("Standard CSV", standard_csv_path),
            ("Complex CSV", complex_csv_path),
            ("Complex Anki Format", complex_anki_path)
        ]:
            if path and os.path.exists(path):
                print(f"\n{name} package created: {os.path.abspath(path)}")
                print(f"File size: {os.path.getsize(path)} bytes")
            else:
                print(f"\n{name} package creation failed!")
