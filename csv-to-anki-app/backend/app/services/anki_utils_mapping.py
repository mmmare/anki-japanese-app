def create_anki_package_with_mapping(csv_content, deck_name, field_mapping=None, include_example_audio=False, enrich_cards=False, include_examples=False):
    """
    Create an Anki package from CSV content with custom field mapping
    
    Args:
        csv_content: The CSV content as a string
        deck_name: The name for the Anki deck
        field_mapping: Dictionary mapping Anki fields to CSV column names
        include_example_audio: Whether to include audio for example sentences
        enrich_cards: Whether to enrich cards with dictionary lookups
        include_examples: Whether to include enhanced example sentences when enriching
        
    Returns:
        genanki.Package object
    """
    import os
    import tempfile
    import csv
    import random
    from io import StringIO
    import genanki
    
    # Fix CSV format issues
    # Function should be imported from anki_utils
    # But we'll just pass it through if it's not defined
    try:
        from .anki_utils import fix_anki_csv_format
        csv_content = fix_anki_csv_format(csv_content)
    except (ImportError, AttributeError):
        print("Warning: fix_anki_csv_format not available, skipping CSV format fix")
    
    # Default field mapping
    default_mapping = {
        'japanese': 'Japanese',
        'english': 'English',
        'reading': 'Reading',
        'example': 'Example',
        'tags': 'Tags'
    }
    
    # Use provided mapping if available, otherwise use default
    mapping = field_mapping if field_mapping else default_mapping
    
    # Set up the Anki model for Japanese vocabulary
    model_id = 1607392319
    model = genanki.Model(
        model_id,
        'Japanese Enhanced',
        fields=[
            {'name': 'Front'},      # Japanese word
            {'name': 'Back'},       # English translation
            {'name': 'Reading'},    # Reading in hiragana/katakana or romaji
            {'name': 'Example'},    # Example sentence  
            {'name': 'Audio'},      # Audio pronunciation
            {'name': 'ExampleAudio'},  # Audio for example sentence
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}<br>{{#Audio}}{{Audio}}{{/Audio}}',  # Audio field contains [sound:xxx] format
                'afmt': '''{{FrontSide}}
<hr id="answer">
<div class="meaning">{{Back}}</div>
{{#Reading}}<div class="reading">Reading: {{Reading}}</div>{{/Reading}}
{{#Example}}
<div class="example">
    <div class="example-title">例文 (Example):</div>
    <div class="example-text">{{Example}}</div>
    {{#ExampleAudio}}
    <div class="example-audio-container">{{ExampleAudio}}</div>
    {{/ExampleAudio}}
</div>
{{/Example}}
''',
            },
        ],
        css='''.card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .reading {
            font-size: 16px;
            color: #585858;
            margin-top: 10px;
        }
        .example {
            font-size: 16px;
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #e6f2ff;
            border-radius: 8px;
            background-color: #f0f7ff;
        }
        .example-title {
            font-weight: bold;
            color: #0066cc;
            margin-bottom: 5px;
        }
        .example-text {
            font-style: italic;
            color: #006699;
        }
        .example-audio-container {
            margin-top: 8px;
        }
        .meaning {
            font-weight: bold;
            color: #009933;
        }
        .audio-placeholder {
            display: none;
        }'''
    )
    
    # Create deck
    deck_id = random.randrange(1 << 30, 1 << 31)
    anki_deck = genanki.Deck(deck_id, deck_name)
    
    # Determine dialect
    dialect = 'excel-tab' if csv_content.strip().startswith("#separator:tab") else 'excel'
    
    # Process Anki format directives
    if csv_content.strip().startswith("#separator"):
        lines = csv_content.strip().split('\n')
        metadata_count = 0
        for line in lines:
            if line.startswith('#'):
                metadata_count += 1
            else:
                break
        
        # Extract content after metadata
        content_for_csv = '\n'.join(lines[metadata_count:])
    else:
        content_for_csv = csv_content
    
    # Parse CSV content using appropriate dialect
    rows = []
    header_map = {}
    
    try:
        csv_file = StringIO(content_for_csv)
        csv_reader = csv.reader(csv_file, dialect=dialect)
        rows = list(csv_reader)
        
        # Get header row
        if rows:
            headers = rows[0]
            
            # Map field positions based on field mapping
            for anki_field, csv_field in mapping.items():
                if csv_field in headers:
                    header_map[anki_field] = headers.index(csv_field)
                
            # Skip header in subsequent processing
            rows = rows[1:]
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return None
    
    # Process rows and add cards
    media_files = []
    cards_added = 0
    
    for row in rows:
        if not row or len(row) < 1:
            continue
        
        # Extract data using mapping
        front = ""
        back = ""
        reading = ""
        example = ""
        tags_str = ""
        
        # Get Japanese (Front) field
        if 'japanese' in header_map and header_map['japanese'] < len(row):
            front = row[header_map['japanese']].strip()
        elif len(row) > 0:  # Fallback to first column
            front = row[0].strip()
            
        # Skip if no front field
        if not front:
            continue
            
        # Get English (Back) field
        if 'english' in header_map and header_map['english'] < len(row):
            back = row[header_map['english']].strip()
        elif len(row) > 1:  # Fallback to second column
            back = row[1].strip()
            
        # If back field is empty and front is Japanese text, look up translation
        if not back and any(ord(c) > 127 for c in front):
            try:
                # Import EnrichService 
                from app.services.enrich_service import EnrichService
                enrich_service = EnrichService()
                # Look up the translation
                lookup_result = enrich_service.lookup_word(front)
                if lookup_result and "meanings" in lookup_result and lookup_result["meanings"]:
                    back = "; ".join(lookup_result["meanings"][:3])  # First 3 translations
                    print(f"Auto-generated translation for '{front}': {back}")
            except Exception as e:
                print(f"Error looking up translation for '{front}': {str(e)}")
                # Keep back as empty string if lookup fails
            
        # Get Reading field
        if 'reading' in header_map and header_map['reading'] < len(row):
            reading = row[header_map['reading']].strip()
        elif len(row) > 2:  # Fallback to third column
            reading = row[2].strip()
            
        # Get Example field
        if 'example' in header_map and header_map['example'] < len(row):
            example = row[header_map['example']].strip()
        elif len(row) > 3:  # Fallback to fourth column
            example = row[3].strip()
            
        # Get Tags field
        if 'tags' in header_map and header_map['tags'] < len(row):
            tags_str = row[header_map['tags']].strip()
        elif len(row) > 4:  # Fallback to fifth column
            tags_str = row[4].strip()
        
        # Process tags
        tags = []
        if tags_str:
            for tag in tags_str.replace(',', ' ').strip().split():
                # Clean up tag
                clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag)
                if clean_tag:
                    tags.append(clean_tag)
        
        # Enrich cards if enrichment is enabled
        if enrich_cards:
            try:
                from app.services.enrich_service import EnrichService
                enrich_service = EnrichService()
                
                # Look up the word for enrichment
                lookup_result = enrich_service.lookup_word(front)
                
                # If no reading provided and we have enrichment data, use it
                if not reading and lookup_result and "reading" in lookup_result:
                    reading = lookup_result["reading"]
                    print(f"Auto-enriched reading for '{front}': {reading}")
                
                # If examples are requested and example field is empty, get enhanced examples
                if include_examples and not example and lookup_result and "examples" in lookup_result and lookup_result["examples"]:
                    # Use the first example from the enriched data
                    example_data = lookup_result["examples"][0]
                    example = f"{example_data['japanese']} ({example_data['english']})"
                    print(f"Auto-enriched example for '{front}': {example}")
                    
            except Exception as e:
                print(f"Error during enrichment for '{front}': {str(e)}")
        
        # Generate audio if we have Japanese characters
        audio_filename = ""
        example_audio_field = ""
        
        # Import EnrichService - needed for both regular and example audio
        from app.services.enrich_service import EnrichService
        enrich_service = EnrichService()
        
        # Generate audio for the vocabulary word if it contains Japanese characters
        if any(ord(c) > 127 for c in front):
            try:
                # Generate audio file for vocabulary word
                audio_path = enrich_service.generate_audio(front)
                if audio_path and os.path.exists(audio_path):
                    audio_filename = os.path.basename(audio_path)
                    media_files.append(audio_path)
                    # Use proper Anki sound tag format
                    audio_field = f"[sound:{audio_filename}]"
                else:
                    audio_field = ""
            except Exception as e:
                print(f"Error generating audio: {str(e)}")
                audio_field = ""
        else:
            audio_field = ""
        
        # Generate example sentence audio if enabled and example contains Japanese characters
        if include_example_audio and example and any(ord(c) > 127 for c in example):
            try:
                # Generate audio file for the example sentence
                example_audio_path = enrich_service.generate_example_audio(example)
                
                if example_audio_path and os.path.exists(example_audio_path):
                    example_audio_filename = os.path.basename(example_audio_path)
                    media_files.append(example_audio_path)
                    
                    # Use proper Anki sound tag format
                    example_audio_field = f"[sound:{example_audio_filename}]"
                else:
                    print(f"Failed to generate example audio for '{example}'")
            except Exception as e:
                print(f"Error generating example audio: {str(e)}")
        
        # Create note with all fields including example audio
        try:
            note = genanki.Note(
                model=model,
                fields=[front, back, reading, example, audio_field, example_audio_field],
                tags=tags
            )
            anki_deck.add_note(note)
            cards_added += 1
        except Exception as e:
            print(f"Error adding note: {str(e)}")
    
    # Create package
    if cards_added == 0:
        raise ValueError("Could not create any cards from CSV content")
        
    package = genanki.Package([anki_deck])
    if media_files:
        package.media_files = media_files
        
    return package
