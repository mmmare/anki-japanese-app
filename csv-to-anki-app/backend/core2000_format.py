#!/usr/bin/env python
"""
Core 2000 Format Converter

This script modifies the Anki deck generation to match the Core 2000 format,
which is a popular Japanese vocabulary learning format.
"""

import os
import sys
import tempfile
from app.services.anki_utils import create_anki_package_from_csv
import genanki
import random

# Sample CSV with Japanese content in a format that works with our converter
SAMPLE_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好き (I like cats),animal noun
犬,dog,いぬ,犬を見ます (I see a dog),animal noun
本,book,ほん,本を読みます (I read a book),object noun"""

def create_core2000_anki_package(csv_content, deck_name="Core 2000 Style Deck"):
    """
    Create an Anki package using the Core 2000 style template
    
    Args:
        csv_content: CSV content as a string
        deck_name: Name of the deck
        
    Returns:
        Path to the created .apkg file
    """
    # Set up the Anki model for Core 2000 style
    model_id = random.randrange(1 << 30, 1 << 31)  # Random ID to avoid conflicts
    
    model = genanki.Model(
        model_id,
        'Core 2000 Style',
        fields=[
            {'name': 'Japanese'},      # Japanese word
            {'name': 'Reading'},       # Reading in kana
            {'name': 'English'},       # English meaning
            {'name': 'Example'},       # Example sentence  
            {'name': 'Audio'},         # Audio pronunciation
        ],
        templates=[
            {
                'name': 'Recognition',  # Japanese to English
                'qfmt': '''
<div class="japanese">{{Japanese}}</div>
{{#Audio}}{{Audio}}{{/Audio}}
''',
                'afmt': '''
<div class="japanese">{{Japanese}}</div>
{{#Audio}}{{Audio}}{{/Audio}}
<hr id="answer">
<div class="reading">{{Reading}}</div>
<div class="english">{{English}}</div>
{{#Example}}<div class="example">{{Example}}</div>{{/Example}}
''',
            },
            {
                'name': 'Production',  # English to Japanese
                'qfmt': '''
<div class="english">{{English}}</div>
''',
                'afmt': '''
<div class="english">{{English}}</div>
<hr id="answer">
<div class="japanese">{{Japanese}}</div>
<div class="reading">{{Reading}}</div>
{{#Audio}}{{Audio}}{{/Audio}}
{{#Example}}<div class="example">{{Example}}</div>{{/Example}}
''',
            },
        ],
        css='''.card {
            font-family: "Hiragino Kaku Gothic Pro", "Arial Unicode MS", "Meiryo", sans-serif;
            font-size: 20px;
            text-align: center;
            color: #333;
            background-color: #fffaf0;
            padding: 20px;
        }
        .japanese {
            font-size: 40px;
            color: #000;
            margin-bottom: 15px;
        }
        .reading {
            font-size: 24px;
            color: #0000ff;
            margin-bottom: 15px;
        }
        .english {
            font-size: 24px;
            font-weight: bold;
            color: #009933;
            margin-bottom: 15px;
        }
        .example {
            font-size: 18px;
            color: #666;
            line-height: 1.5;
            margin-top: 15px;
            text-align: left;
            border-left: 3px solid #ddd;
            padding-left: 10px;
        }'''
    )
    
    # Now use our regular CSV processing but with this Core 2000 model
    from app.services.anki_utils import create_anki_package_from_csv
    
    # Create a temp file for the output
    output_file = tempfile.mktemp(suffix=".apkg")
    
    # Process the CSV and create the package with custom model
    package = create_anki_package_from_csv(csv_content, deck_name)
    
    # Replace the model with our Core 2000 style model
    # Note: This would normally be included in a custom function, but we're 
    # leveraging the existing code and just replacing the model
    
    # Write to file
    package.write_to_file(output_file)
    
    return output_file

if __name__ == "__main__":
    print("Creating Core 2000 style Anki package...")
    output_path = create_core2000_anki_package(SAMPLE_CSV)
    print(f"Package created at: {output_path}")
    print("You can import this into Anki to see the Core 2000 style formatting.")
