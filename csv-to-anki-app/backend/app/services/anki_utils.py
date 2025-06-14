import os
import tempfile
import csv
import random
from io import StringIO
import genanki

def fix_anki_csv_format(csv_content):
    """
    Fix common issues with Anki CSV format files
    
    Args:
        csv_content: The raw CSV content as a string
        
    Returns:
        Fixed CSV content as a string
    """
    # Check if it's an Anki format file
    if not csv_content.strip().startswith("#separator"):
        return csv_content  # Not Anki format, return as-is
    
    lines = csv_content.strip().split('\n')
    metadata_lines = []
    content_lines = []
    metadata_complete = False
    
    # Separate metadata from content
    for line in lines:
        if not metadata_complete and line.startswith('#'):
            metadata_lines.append(line)
        else:
            metadata_complete = True
            content_lines.append(line)
    
    # Process content
    if not content_lines:
        # If no content found, create a default header line
        content_lines = ["Japanese\tEnglish\tReading\tExample\tTags"]
    
    # Check for separator type
    separator = '\t'  # Default to tab
    for meta in metadata_lines:
        if meta.lower().startswith('#separator:'):
            if 'tab' in meta.lower():
                separator = '\t'
            else:
                separator = ','
    
    # Check if first content line is a header
    has_header = False
    if content_lines and len(content_lines[0]) > 0:
        # Handle possible escaping in the content line before splitting
        first_line = content_lines[0]
        first_cell = ""
        
        # Extract the first field more carefully
        if separator == '\t':
            if '\t' in first_line:
                first_cell = first_line.split('\t')[0].strip().lower()
            else:
                # If no tabs but it should be tab-separated, try comma as fallback
                first_cell = first_line.split(',')[0].strip().lower()
        else:
            # Parse comma-separated with quote handling
            in_quotes = False
            for char in first_line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    break
                else:
                    first_cell += char
            first_cell = first_cell.strip().lower()
        
        has_header = first_cell in ['japanese', 'front', 'word']
    
    # If no header, add one
    if not has_header and len(content_lines) > 0 and not content_lines[0].strip().startswith('#'):
        content_lines.insert(0, f"Japanese{separator}English{separator}Reading{separator}Example{separator}Tags")
    
    # Reconstruct the fixed content
    fixed_content = '\n'.join(metadata_lines + content_lines)
    
    # Handle special edge cases
    if "#separator:tab" in fixed_content and "," in fixed_content:
        print("Detected potential issue: Tab-separated file with comma values")
        # Make sure we're not inadvertently escaping commas in tab-separated files
        # Let our special parser handle it instead
    
    return fixed_content

def create_anki_package_from_csv(csv_content, deck_name, include_example_audio=False):
    """
    Create an Anki package from CSV content with improved error handling
    
    Args:
        csv_content: The CSV content as a string
        deck_name: The name for the Anki deck
        include_example_audio: Whether to include audio for example sentences
        
    Returns:
        genanki.Package object
    """
    # Fix CSV format issues
    csv_content = fix_anki_csv_format(csv_content)
    
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
    Example: {{Example}}
    {{#ExampleAudio}}
    <div class="example-audio">
        <div class="example-audio-label">Example Audio:</div>
        {{ExampleAudio}}
    </div>
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
            color: #006699;
            margin-top: 15px;
            font-style: italic;
        }
        .meaning {
            font-weight: bold;
            color: #009933;
        }
        .example-audio {
            margin-top: 8px;
            padding: 6px;
            background-color: #f0f5ff;
            border-radius: 4px;
            border: 1px solid #dde5ff;
        }
        .example-audio-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
            font-weight: bold;
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
    
    # Parse CSV content
    # Check if content has already been split by commas
    if dialect == 'excel-tab':
        # Handle tab separated files properly
        lines = content_for_csv.strip().split('\n')
        rows = []
        for line in lines:
            if not line.strip():
                continue
            
            # For tab-separated files that may contain commas within fields
            if '\t' in line:
                # Use proper tab splitting with a custom parser to handle commas within fields
                # This creates a more robust parser for tab-delimited data
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
                # For non-tab lines (could be comma-separated), use CSV reader
                try:
                    csv_reader = csv.reader([line])
                    row_parts = next(csv_reader, [])
                    rows.append(row_parts)
                except Exception as e:
                    print(f"Error parsing CSV line '{line}': {e}")
                    # Fallback - just use the line as a single field
                    rows.append([line])
    else:
        # Normal CSV parsing for comma-separated files
        try:
            csv_file = StringIO(content_for_csv)
            csv_reader = csv.reader(csv_file, dialect=dialect)
            rows = list(csv_reader)  # Convert to list for easier processing
        except Exception as e:
            # Fallback parsing with direct line splitting
            print(f"CSV parsing error: {e}, using fallback parser")
            rows = []
            lines = content_for_csv.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                # Simple comma split with quote handling
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
    
    # Skip header if present
    start_idx = 0
    if rows and rows[0] and rows[0][0].lower() in ['japanese', 'front', 'word']:
        start_idx = 1
    
    # Process rows and add cards
    media_files = []
    cards_added = 0
    
    for i in range(start_idx, len(rows)):
        row = rows[i]
        if not row or len(row) < 2:
            continue
            
        front = row[0].strip()
        if not front:
            continue
            
        back = row[1].strip() if len(row) > 1 and row[1].strip() else ""
        reading = row[2].strip() if len(row) > 2 and row[2].strip() else ""
        example = row[3].strip() if len(row) > 3 and row[3].strip() else ""
        tags_str = row[4].strip() if len(row) > 4 and row[4].strip() else ""
        
        # Process tags
        tags = []
        if tags_str:
            for tag in tags_str.replace(',', ' ').strip().split():
                # Clean up tag
                clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag)
                if clean_tag:
                    tags.append(clean_tag)
        
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
                    print(f"Audio generated for '{front}': {audio_filename}")
                    
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
                print(f"Generating example audio for: '{example}'")
                # Generate audio file for the example sentence
                example_audio_path = enrich_service.generate_example_audio(example)
                
                if example_audio_path and os.path.exists(example_audio_path):
                    example_audio_filename = os.path.basename(example_audio_path)
                    media_files.append(example_audio_path)
                    print(f"✓ Example audio generated for: '{example}' - File: {example_audio_filename}")
                    
                    # Use proper Anki sound tag format
                    example_audio_field = f"[sound:{example_audio_filename}]"
                else:
                    print(f"✗ Failed to generate example audio for '{example}'")
            except Exception as e:
                print(f"Error generating example audio: {str(e)}")
        
        # Create note with all fields including example audio
        print(f"Adding note for '{front}' with fields:")
        print(f"  - Front: '{front}'")
        print(f"  - Back: '{back}'")
        print(f"  - Reading: '{reading}'")
        print(f"  - Example: '{example}'")
        print(f"  - Audio: '{audio_field}'")
        print(f"  - Example Audio: '{example_audio_field}'")
        
        note = genanki.Note(
            model=model,
            fields=[front, back, reading, example, audio_field, example_audio_field],  # Now includes example audio
            tags=tags
        )
        anki_deck.add_note(note)
        cards_added += 1
    
    # Create package
    if cards_added == 0:
        raise ValueError("Could not create any cards from CSV content")
        
    package = genanki.Package([anki_deck])
    if media_files:
        package.media_files = media_files
        
    return package

def create_core2000_package_from_csv(csv_content, deck_name, include_example_audio=True):
    """
    Create an Anki package with Core 2000 style formatting from CSV content
    
    Args:
        csv_content: The CSV content as a string
        deck_name: The name for the Anki deck
        include_example_audio: Whether to include audio for example sentences
        
    Returns:
        genanki.Package object
    """
    # Fix CSV format issues
    csv_content = fix_anki_csv_format(csv_content)
    
    # Set up the Anki model for Core 2000 style Japanese vocabulary
    model_id = 1607392319  # Using consistent ID for compatibility
    model = genanki.Model(
        model_id,
        'Core 2000 Style',
        fields=[
            {'name': 'Japanese'},      # Japanese word
            {'name': 'Reading'},       # Reading in kana
            {'name': 'English'},       # English meaning
            {'name': 'Example'},       # Example sentence  
            {'name': 'Audio'},         # Audio pronunciation
            {'name': 'ExampleAudio'},  # Audio for example sentence
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
{{#Example}}
<div class="example">
  {{Example}}
  {{#ExampleAudio}}
  <div class="example-audio">
    <div class="example-audio-label">Example Audio:</div>
    {{ExampleAudio}}
  </div>
  {{/ExampleAudio}}
</div>
{{/Example}}
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
{{#Example}}
<div class="example">
  {{Example}}
  {{#ExampleAudio}}
  <div class="example-audio">
    <div class="example-audio-label">Example Audio:</div>
    {{ExampleAudio}}
  </div>
  {{/ExampleAudio}}
</div>
{{/Example}}
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
        }
        .example-audio {
            margin-top: 8px;
            padding: 6px;
            background-color: #f0f5ff;
            border-radius: 4px;
            border: 1px solid #dde5ff;
        }
        .example-audio-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
            font-weight: bold;
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
    
    # Parse CSV content using the same parsing logic as create_anki_package_from_csv
    if dialect == 'excel-tab':
        # Handle tab separated files properly
        lines = content_for_csv.strip().split('\n')
        rows = []
        for line in lines:
            if not line.strip():
                continue
            
            # For tab-separated files that may contain commas within fields
            if '\t' in line:
                # Use proper tab splitting with a custom parser to handle commas within fields
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
                # For non-tab lines (could be comma-separated), use CSV reader
                try:
                    csv_reader = csv.reader([line])
                    row_parts = next(csv_reader, [])
                    rows.append(row_parts)
                except Exception as e:
                    print(f"Error parsing CSV line '{line}': {e}")
                    # Fallback - just use the line as a single field
                    rows.append([line])
    else:
        # Normal CSV parsing for comma-separated files
        try:
            csv_file = StringIO(content_for_csv)
            csv_reader = csv.reader(csv_file, dialect=dialect)
            rows = list(csv_reader)  # Convert to list for easier processing
        except Exception as e:
            # Fallback parsing with direct line splitting
            print(f"CSV parsing error: {e}, using fallback parser")
            rows = []
            lines = content_for_csv.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                # Simple comma split with quote handling
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
    
    # Skip header if present
    start_idx = 0
    if rows and rows[0] and rows[0][0].lower() in ['japanese', 'front', 'word']:
        start_idx = 1
    
    # Process rows and add cards - Core 2000 style cards
    media_files = []
    cards_added = 0
    
    for i in range(start_idx, len(rows)):
        row = rows[i]
        if not row or len(row) < 2:
            continue
            
        # For Core 2000, we reorder the fields a bit
        japanese = row[0].strip()
        english = row[1].strip() if len(row) > 1 and row[1].strip() else ""
        reading = row[2].strip() if len(row) > 2 and row[2].strip() else ""
        example = row[3].strip() if len(row) > 3 and row[3].strip() else ""
        tags_str = row[4].strip() if len(row) > 4 and row[4].strip() else ""
        
        if not japanese:
            continue
            
        # Process tags
        tags = []
        if tags_str:
            for tag in tags_str.replace(',', ' ').strip().split():
                # Clean up tag
                clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag)
                if clean_tag:
                    tags.append(clean_tag)
        
        # Generate audio if we have Japanese characters
        audio_field = ""
        example_audio_field = ""
        
        # Create EnrichService if needed
        from app.services.enrich_service import EnrichService
        enrich_service = EnrichService()
        
        # Generate word audio
        if any(ord(c) > 127 for c in japanese):
            try:
                # Generate audio file for the vocabulary word
                audio_path = enrich_service.generate_audio(japanese)
                if audio_path and os.path.exists(audio_path):
                    audio_filename = os.path.basename(audio_path)
                    media_files.append(audio_path)
                    print(f"Audio generated for '{japanese}': {audio_filename}")
                    
                    # Use proper Anki sound tag format
                    audio_field = f"[sound:{audio_filename}]"
            except Exception as e:
                print(f"Error generating audio: {str(e)}")
        
        # Generate example sentence audio if present and enabled
        if include_example_audio and example and any(ord(c) > 127 for c in example):
            print(f"DEBUG: Processing example audio for '{japanese}' with example: '{example}'")
            print(f"DEBUG: include_example_audio flag is: {include_example_audio}")
            
            try:
                # Generate audio file for the example sentence
                print(f"DEBUG: Calling generate_example_audio with example: '{example}'")
                example_audio_path = enrich_service.generate_example_audio(example)
                
                if example_audio_path and os.path.exists(example_audio_path):
                    example_audio_filename = os.path.basename(example_audio_path)
                    # Ensure the audio file is actually added to media_files
                    if example_audio_path not in media_files:
                        media_files.append(example_audio_path)
                        print(f"✓ Example audio added to media files: {example_audio_path}")
                    else:
                        print(f"✓ Example audio already in media files: {example_audio_path}")
                    
                    print(f"✓ Example audio generated for: '{example}' - File: {example_audio_filename}")
                    
                    # Use proper Anki sound tag format
                    example_audio_field = f"[sound:{example_audio_filename}]"
                    print(f"DEBUG: Example audio field set to: '{example_audio_field}'")
                    
                    # Verify that the file exists and has content
                    file_size = os.path.getsize(example_audio_path)
                    print(f"DEBUG: Example audio file size: {file_size} bytes")
                    
                    # Track the media files for debugging
                    print(f"DEBUG: Current media files list ({len(media_files)} files):")
                    for i, f in enumerate(media_files):
                        if os.path.exists(f):
                            print(f"  {i+1}. {os.path.basename(f)} - {os.path.getsize(f)} bytes")
                        else:
                            print(f"  {i+1}. {os.path.basename(f)} - FILE NOT FOUND")
                else:
                    print(f"✗ Failed to generate example audio - Path invalid or file doesn't exist")
            except Exception as e:
                print(f"Error generating example audio: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Create note with Core 2000 field order including example audio
        print(f"DEBUG: Creating note for '{japanese}'")
        print(f"DEBUG: Fields:")
        print(f"  1. Japanese: '{japanese}'")
        print(f"  2. Reading: '{reading}'")
        print(f"  3. English: '{english}'")
        print(f"  4. Example: '{example}'")
        print(f"  5. Audio: '{audio_field}'")
        print(f"  6. Example Audio: '{example_audio_field}'")
        
        note = genanki.Note(
            model=model,
            fields=[japanese, reading, english, example, audio_field, example_audio_field],
            tags=tags
        )
        anki_deck.add_note(note)
        cards_added += 1
        
        print(f"Added note #{cards_added} for '{japanese}' with example: '{example[:30]}...'")
        if example_audio_field:
            print(f"  Note has example audio: {example_audio_field}")
        else:
            print(f"  Note does NOT have example audio")
    
    # Create package
    if cards_added == 0:
        raise ValueError("Could not create any cards from CSV content")
        
    package = genanki.Package([anki_deck])
    if media_files:
        package.media_files = media_files
        
    return package
