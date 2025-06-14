#!/usr/bin/env python
"""
Test APKG creation directly from CSV data
"""

import genanki
import random
from io import StringIO
import csv
import textwrap

# Test data
ANKI_FORMAT_CSV = """#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front	Back	Tags
こんにちは	Hello	greeting
ありがとう	Thank you	greeting
さようなら	Goodbye	greeting
はい	Yes	basic
いいえ	No	basic"""

def test_apkg_creation():
    """Test direct creation of an .apkg file"""
    
    print("=== Testing direct .apkg creation ===")
    
    # Create a model ID
    model_id = random.randrange(1 << 30, 1 << 31)
    
    # Create a simple model that matches the Basic built-in model
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
    
    # Create a unique deck ID
    import hashlib
    deck_name = "Test Japanese Vocabulary"
    deck_id = random.randrange(1 << 30, 1 << 31)
    anki_deck = genanki.Deck(deck_id, deck_name)
    
    # Process the CSV content
    lines = ANKI_FORMAT_CSV.strip().split('\n')
    
    # Check for Anki format directives
    metadata_count = 0
    dialect = 'excel'
    
    if lines[0].startswith('#separator:'):
        print("Detected Anki format directives")
        for line in lines:
            if line.startswith('#'):
                metadata_count += 1
                print(f"Metadata: {line}")
            else:
                break
        
        # Use tab as separator for Anki format
        if '#separator:tab' in lines[0].lower():
            dialect = 'excel-tab'
            print("Using tab separator")
        
    # Extract actual content
    content = '\n'.join(lines[metadata_count:])
    csv_file = StringIO(content)
    csv_reader = csv.reader(csv_file, dialect=dialect)
    
    cards_added = 0
    for i, row in enumerate(csv_reader):
        if i == 0 and row[0].lower() in ['front']: 
            # Skip header if present
            print(f"Skipping header row: {row}")
            continue
            
        if len(row) < 2:
            continue
            
        front = row[0].strip()
        back = row[1].strip()
        
        if not front or not back:
            continue
            
        # Process tags
        tags = []
        if len(row) >= 3 and row[2].strip():
            for tag in row[2].split(','):
                clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag.strip())
                if clean_tag:
                    tags.append(clean_tag)
        
        print(f"Creating note - Front: '{front}', Back: '{back}', Tags: {tags}")
        
        # Create a note with the Basic model
        note = genanki.Note(
            model=model,
            fields=[front, back],
            tags=tags
        )
        
        anki_deck.add_note(note)
        cards_added += 1
    
    print(f"Added {cards_added} cards to the deck")
    
    # Create the package and write to file
    package = genanki.Package([anki_deck])
    output_file = "test_output.apkg"
    package.write_to_file(output_file)
    
    print(f"Wrote Anki package to {output_file}")

if __name__ == "__main__":
    test_apkg_creation()
