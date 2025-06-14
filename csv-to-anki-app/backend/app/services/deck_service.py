from typing import List
import csv
import random
import os
import genanki
from io import StringIO
from ..models import AnkiDeck, AnkiCard  # Use relative import

class DeckService:
    def create_deck_from_csv(self, file_content: str, deck_name: str) -> AnkiDeck:
        """
        Convert CSV content to an Anki deck structure
        
        CSV format should have at least two columns: Japanese word and meaning
        The expanded format has 5 columns: Japanese, English, Reading, Example, Tags
        """
        deck = AnkiDeck(name=deck_name)
        is_enriched = False
        
        csv_file = StringIO(file_content)
        
        # Check if the content starts with Anki format directives
        lines = file_content.strip().split('\n')
        is_anki_format = False
        dialect = 'excel'
        has_header = True
        
        if lines and lines[0].startswith('#separator:'):
            is_anki_format = True
            # Skip Anki metadata lines
            metadata_count = 0
            for line in lines:
                if line.startswith('#'):
                    metadata_count += 1
                else:
                    break
            
            # Use tab as separator for Anki format
            if '#separator:tab' in lines[0].lower():
                dialect = 'excel-tab'
            
            # Check if we have a #columns directive which specifies fields
            # If so, we should not treat the first data row as a header
            for i in range(metadata_count):
                if lines[i].startswith('#columns:'):
                    has_header = False
                    break
            
            # Reconstruct content without metadata for CSV reader
            if metadata_count > 0:
                temp_content = '\n'.join(lines[metadata_count:])
                csv_file = StringIO(temp_content)
        
        csv_reader = csv.reader(csv_file, dialect=dialect)
        
        # Detect if we have an enriched CSV by looking for the enriched header
        header_row = None
        if has_header and lines[0 if not is_anki_format else metadata_count].strip() == "Japanese,English,Reading,Example,Tags":
            is_enriched = True
        
        for row_index, row in enumerate(csv_reader):
            if len(row) >= 2:  # Make sure we have at least front and back
                front = row[0].strip()
                back = row[1].strip()
                
                # Skip header row if present in standard CSV
                if row_index == 0 and has_header:
                    if front.lower() in ["japanese", "word", "front"]:
                        # Store header row to check for enriched format
                        header_row = row
                        # If header has at least 4 columns with specific names, it's enriched
                        if len(row) >= 4 and row[2].lower() in ["reading", "pronunciation"] and row[3].lower() == "example":
                            is_enriched = True
                        continue
                
                # Create a new card with basic fields
                card = AnkiCard(front=front, back=back)
                
                # Handle the enriched format (more columns)
                if len(row) >= 3 and row[2].strip():
                    if is_enriched:
                        # Third column is reading in enriched format
                        card.reading = row[2].strip()
                    else:
                        # Third column could be tags in standard format
                        card.tags = [tag.strip().replace(' ', '_') for tag in row[2].split(',')]
                
                # Example sentence (4th column in enriched format)
                if len(row) >= 4 and row[3].strip():
                    card.example = row[3].strip()
                
                # Tags (5th column in enriched format)
                if len(row) >= 5 and row[4].strip():
                    # For enriched format, 5th column is tags
                    card.tags = [tag.strip().replace(' ', '_') for tag in row[4].split()]
                
                # Add default tag if needed
                if not card.tags and any(ord(c) > 127 for c in front):  # If Japanese characters
                    card.tags = ["japanese"]
                
                deck.cards.append(card)
        
        # Set the enriched flag on the deck
        deck.is_enriched = is_enriched
        
        return deck
                
        return deck
    
    def create_anki_package(self, deck: AnkiDeck) -> genanki.Package:
        """
        Convert our AnkiDeck model to a genanki Package that can be exported as a valid .apkg file
        """
        # Create a unique model ID - use consistent IDs to avoid issues
        model_id = 1607392319
        
        # Define the card template
        model = genanki.Model(
            model_id,
            'Japanese Vocabulary Model',
            fields=[
                {'name': 'Japanese'},
                {'name': 'Meaning'},
            ],
            templates=[
                {
                    'name': 'Japanese to English',
                    'qfmt': '<div style="font-size: 24px; text-align: center;">{{Japanese}}</div>',
                    'afmt': '<div style="font-size: 24px; text-align: center;">{{Japanese}}</div><hr id="answer"><div style="text-align: center;">{{Meaning}}</div>',
                },
            ])
        
        # Create a unique deck ID - use consistent IDs to avoid issues
        deck_id = 2059400110
        
        # Create an Anki deck
        anki_deck = genanki.Deck(deck_id, deck.name)
        
        # Add cards to the deck
        for card in deck.cards:
            # Ensure tags are properly formatted (no spaces, only alphanumeric and underscore)
            clean_tags = []
            for tag in card.tags:
                # Replace spaces with underscore and remove any non-alphanumeric/underscore characters
                clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag)
                if clean_tag:  # Only add non-empty tags
                    clean_tags.append(clean_tag)
            
            note = genanki.Note(
                model=model,
                fields=[card.front, card.back],
                tags=clean_tags
            )
            anki_deck.add_note(note)
        
        # Create the package
        package = genanki.Package([anki_deck])  # Note: Package takes a list of decks
        return package

    def save_deck(self, deck: AnkiDeck) -> None:
        # Logic to save the deck to a database or file system
        pass

    def load_deck(self, deck_id: int) -> AnkiDeck:
        # Logic to load a deck from a database or file system
        pass
        
    def create_anki_package_from_csv(self, csv_content: str, deck_name: str) -> genanki.Package:
        """
        Create a completely standard Anki deck using "genanki" with settings matching
        the standard Basic note type in Anki to ensure compatibility
        """
        import textwrap
        try:
            # Use Anki's standard model ID for Basic note type
            # This ensures maximum compatibility with Anki's built-in models
            model_id = 1607392319
            
            # Create an enhanced model for Japanese cards with reading, example, and audio
            model = genanki.Model(
                model_id,
                'Japanese Enhanced',
                fields=[
                    {'name': 'Front'},      # Japanese word
                    {'name': 'Back'},       # English translation
                    {'name': 'Reading'},    # Reading in hiragana/katakana or romaji
                    {'name': 'Example'},    # Example sentence  
                    {'name': 'Audio'},      # Audio pronunciation
                    {'name': 'ExampleAudio'}, # Audio for example sentence
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '{{Front}}<br>{{#Audio}}{{Audio}}{{/Audio}}',
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
                css=textwrap.dedent("""\
                    .card {
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
                    }
                """)
            )

            # Create a unique deck ID
            import random
            deck_id = random.randrange(1 << 30, 1 << 31)
            anki_deck = genanki.Deck(deck_id, deck_name)
            
            print(f"Creating Anki deck: {deck_name} (ID: {deck_id})")
            
            # Parse the CSV content
            is_anki_format = csv_content.strip().startswith("#separator")
            
            if is_anki_format:
                print("Detected Anki format CSV")
                lines = csv_content.strip().split('\n')
                metadata_count = 0
                dialect = 'excel-tab' if "#separator:tab" in lines[0].lower() else 'excel'
                separator = '\t' if dialect == 'excel-tab' else ','
                
                # Process metadata to extract column mapping if available
                column_mapping = None
                for i, line in enumerate(lines):
                    if line.startswith('#'):
                        metadata_count += 1
                        # Check if this is a column definition line
                        if line.lower().startswith('#columns:'):
                            column_parts = line[9:].strip().split(separator)
                            column_mapping = {i: name.strip() for i, name in enumerate(column_parts)}
                            print(f"Found column mapping: {column_mapping}")
                    else:
                        break
                        
                # Extract the actual CSV content after metadata
                csv_content = '\n'.join(lines[metadata_count:])
                
                # If we have an empty csv_content after metadata removal, there's an issue
                if not csv_content.strip():
                    print("WARNING: No CSV content found after removing metadata")
                    # Fallback: try to use content after the "#columns:" line
                    for i, line in enumerate(lines):
                        if line.lower().startswith('#columns:'):
                            csv_content = '\n'.join(lines[i+1:])
                            break
            else:
                print("Using standard CSV format")
                dialect = 'excel'
            
            print(f"CSV content after processing: '{csv_content[:100]}...'")
            
            # Handle possible empty content
            if not csv_content.strip():
                raise ValueError("Empty CSV content after processing metadata")
            
            # More robust CSV parsing that handles special cases
            rows = []
            if dialect == 'excel-tab':
                print("Using specialized tab-separated file parser")
                # For tab-separated files that may contain commas within fields
                content_lines = csv_content.strip().split('\n')
                
                for line in content_lines:
                    if not line.strip():
                        continue
                    
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
                            rows.append([line])
            else:
                # Standard CSV parsing for comma-separated files
                try:
                    csv_file = StringIO(csv_content)
                    csv_reader = csv.reader(csv_file, dialect=dialect)
                    rows = list(csv_reader)
                except Exception as e:
                    print(f"Error parsing CSV content: {e}")
                    print(f"Falling back to line-by-line parsing")
                    # Fallback mode - split by lines and try to parse each line
                    content_lines = csv_content.strip().split('\n')
                    for line in content_lines:
                        if not line.strip():
                            continue
                        try:
                            csv_reader = csv.reader([line])
                            row_parts = next(csv_reader, [])
                            rows.append(row_parts)
                        except:
                            rows.append([line])
            
            # Validate we have rows
            if not rows:
                print(f"Error: No valid rows found in CSV content")
                print(f"CSV content sample: '{csv_content[:200]}'")
                raise ValueError("Failed to parse CSV content: No valid rows found")
            
            # Skip header if standard CSV
            header_skipped = False
            cards_added = 0
            
            # Store media files that need to be included in the package
            media_files = []
            
            # Allow for various common column names
            front_column_names = ['japanese', 'front', 'word', 'question']
            back_column_names = ['english', 'back', 'answer', 'meaning', 'translation']
            
            # Keep track of rows for debugging
            all_rows = []
            
            for row_index, row in enumerate(rows):
                all_rows.append(row)
                
                # Skip completely empty rows
                if not row or all(not cell.strip() for cell in row):
                    print(f"Skipping empty row at index {row_index}")
                    continue
                    
                if len(row) < 2:
                    print(f"Warning: Row {row_index} has fewer than 2 columns: {row}")
                    continue
                    
                front = row[0].strip()
                back = row[1].strip()
                
                # Skip header row for standard CSV
                if not is_anki_format and not header_skipped and row_index == 0:
                    if (front.lower() in front_column_names or 
                        back.lower() in back_column_names or
                        (len(row) > 2 and row[2].strip().lower() in ['reading', 'pronunciation'])):
                        header_skipped = True
                        print(f"Skipped header row: {row}")
                        continue
                
                if not front:
                    print(f"Warning: Empty 'front' field in row {row_index}: {row}")
                    continue
                    
                # Allow back to be empty for words that are being enriched
                
                # Extract additional fields if available
                reading = ""
                example = ""
                audio_filename = ""
                
                # Reading (column 3 if present)
                if len(row) >= 3 and row[2].strip():
                    reading = row[2].strip()
                
                # Example (column 4 if present)
                if len(row) >= 4 and row[3].strip():
                    example = row[3].strip()
                
                # Process tags - Use column 5 if present, otherwise default tags
                tags = []
                if len(row) >= 5 and row[4].strip():
                    # Split by spaces or commas as standard Anki behavior
                    for tag in row[4].replace(',', ' ').strip().split():
                        # Make sure tags are alphanumeric with underscores
                        clean_tag = ''.join(c if c.isalnum() or c == '_' else '_' for c in tag)
                        if clean_tag:
                            tags.append(clean_tag)
                
                # If no tags but the word is in Japanese, add a default "japanese" tag
                if not tags and any(ord(c) > 127 for c in front):
                    tags.append("japanese")
                
                # Check if we need to generate audio
                # We'll use the EnrichService directly if we have a Japanese term
                if any(ord(c) > 127 for c in front):
                    try:
                        # Import at module level to avoid circular imports
                        import sys
                        import importlib.util
                        
                        # Get the EnrichService instance more reliably
                        if 'app.services.enrich_service' not in sys.modules:
                            # For direct module import
                            try:
                                from app.services.enrich_service import EnrichService
                                enrich_service = EnrichService()
                            except ImportError:
                                # For relative import
                                try:
                                    from ..services.enrich_service import EnrichService
                                    enrich_service = EnrichService()
                                except ImportError:
                                    print("Warning: Could not import EnrichService. Audio generation skipped.")
                                    enrich_service = None
                        else:
                            # Use the already imported module
                            enrich_module = sys.modules['app.services.enrich_service']
                            enrich_service = enrich_module.EnrichService()
                        
                        if enrich_service:
                            # Generate audio file
                            audio_path = enrich_service.generate_audio(front)
                            if audio_path and os.path.exists(audio_path):
                                audio_filename = os.path.basename(audio_path)
                                media_files.append(audio_path)
                                print(f"Added audio file: {audio_path}")
                                # Format audio filename for Anki
                                audio_field = f"[sound:{audio_filename}]"
                            else:
                                audio_field = ""
                    except Exception as audio_error:
                        print(f"Error generating audio for '{front}': {str(audio_error)}")
                        audio_field = ""
                else:
                    audio_field = ""
                
                print(f"Adding note: Front='{front}', Back='{back}', Reading='{reading}', Example='{example}', Audio='{audio_field}', Tags={tags}")
                
                # Generate example sentence audio if we have Japanese characters in the example
                example_audio_field = ""
                if example and any(ord(c) > 127 for c in example):
                    try:
                        if enrich_service:
                            # Generate audio for the example sentence
                            example_audio_path = enrich_service.generate_example_audio(example)
                            if example_audio_path and os.path.exists(example_audio_path):
                                example_audio_filename = os.path.basename(example_audio_path)
                                media_files.append(example_audio_path)
                                print(f"✓ Example audio generated for: '{example}' - File: {example_audio_filename}")
                                # Format example audio for Anki
                                example_audio_field = f"[sound:{example_audio_filename}]"
                            else:
                                print(f"✗ Failed to generate example audio for '{example}'")
                    except Exception as e:
                        print(f"Error generating example audio: {str(e)}")

                try:
                    # Create note with our enhanced model
                    fields = [front, back, reading, example, audio_field, example_audio_field]
                    note = genanki.Note(
                        model=model,
                        fields=fields,
                        tags=tags
                    )
                    anki_deck.add_note(note)
                    cards_added += 1
                except Exception as note_error:
                    print(f"Error adding note: {str(note_error)}. Skipping this card.")
            
            # Add debugging information if no cards were created
            if cards_added == 0:
                print("DEBUG: No cards were created. Showing processed rows:")
                for i, row in enumerate(all_rows):
                    print(f"Row {i}: {row}")
                raise ValueError("No valid cards were created. Please check your CSV format.")
                
            print(f"Successfully added {cards_added} cards to deck '{deck_name}'")
            
            # Create package with media files
            package = genanki.Package([anki_deck])
            
            # Add media files if we have any
            if media_files:
                package.media_files = media_files
                print(f"Added {len(media_files)} audio files to deck")
            return package
            
        except Exception as e:
            import traceback
            print("Error creating Anki package:", str(e))
            traceback.print_exc()
            raise
    
    def create_deck_from_csv_with_mapping(self, file_content: str, deck_name: str, field_mapping: dict = None) -> AnkiDeck:
        """
        Create an Anki deck from CSV content using a field mapping
        
        Args:
            file_content: String content of CSV file
            deck_name: Name for the Anki deck
            field_mapping: Dictionary mapping CSV columns to Anki fields
        
        Returns:
            AnkiDeck object containing cards created from CSV
        """
        # Create base deck object
        deck = AnkiDeck(name=deck_name)
        
        # Default field mapping
        default_mapping = {
            'japanese': 'Japanese',
            'english': 'English Meaning',
            'reading': 'Reading',
            'example': 'Example',
            'tags': 'Tags'
        }
        
        mapping = field_mapping if field_mapping else default_mapping
        
        csv_file = StringIO(file_content)
        
        # Check for Anki format directives
        lines = file_content.strip().split('\n')
        is_anki_format = False
        dialect = 'excel'
        has_header = True
        
        if lines and lines[0].startswith('#separator:'):
            is_anki_format = True
            # Skip Anki metadata lines
            metadata_count = 0
            for line in lines:
                if line.startswith('#'):
                    metadata_count += 1
                else:
                    break
            
            # Use tab as separator for Anki format
            if '#separator:tab' in lines[0].lower():
                dialect = 'excel-tab'
            
            # Check if we have a #columns directive which specifies fields
            for i in range(metadata_count):
                if lines[i].startswith('#columns:'):
                    has_header = False
                    break
            
            # Reconstruct content without metadata for CSV reader
            if metadata_count > 0:
                temp_content = '\n'.join(lines[metadata_count:])
                csv_file = StringIO(temp_content)
        
        # Read CSV content
        csv_reader = csv.reader(csv_file, dialect=dialect)
        
        # Get headers first
        headers = []
        if has_header:
            try:
                headers = next(csv_reader)
            except StopIteration:
                # Empty CSV
                return deck
        
        # Process rows
        for row_index, row in enumerate(csv_reader):
            # Skip empty rows
            if not row or all(not cell.strip() for cell in row):
                continue
            
            # Create new card
            card = AnkiCard(front="", back="")
            
            # Apply field mapping to populate card fields
            for field_key, header_name in mapping.items():
                if not header_name or header_name not in headers:
                    continue
                    
                column_index = headers.index(header_name)
                if 0 <= column_index < len(row):
                    value = row[column_index].strip()
                    
                    # Apply the value to the appropriate card field
                    if field_key == 'japanese':
                        card.front = value
                    elif field_key == 'english':
                        card.back = value
                    elif field_key == 'reading':
                        card.reading = value
                    elif field_key == 'example':
                        card.example = value
                    elif field_key == 'tags':
                        # Split tags on whitespace or commas
                        if value:
                            card.tags = [tag.strip().replace(' ', '_') for tag in value.replace(',', ' ').split()]
            
            # Only add card if it has at least a front field
            if card.front:
                # If no back specified, use the same as front
                if not card.back:
                    card.back = card.front
                
                # Add default tag if needed
                if not card.tags and any(ord(c) > 127 for c in card.front):  # If Japanese characters
                    card.tags = ["japanese"]
                
                deck.cards.append(card)
        
        return deck