from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Response
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
import tempfile
import json
import csv
from io import StringIO
from datetime import datetime
from ..services.deck_service import DeckService
from ..models import AnkiDeck, AnkiCard

router = APIRouter(prefix="/api/deck", tags=["deck"])
deck_service = DeckService()

# In-memory storage for uploaded files and decks during the session
# In a production environment, this would be replaced with a database
temp_storage = {}

# Store for temporary audio files (in production, use Redis or similar)
preview_audio_files = {}

@router.post("/upload")
async def upload_csv_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Read the file content
    contents = await file.read()
    contents_str = contents.decode("utf-8")
    
    # Generate a unique ID for this upload session
    session_id = f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Store the content in temporary storage
    temp_storage[session_id] = {
        "content": contents_str,
        "filename": file.filename
    }
    
    # Count rows (excluding header)
    row_count = len(contents_str.splitlines()) - 1
    
    # Return basic info about the file
    return {
        "filename": file.filename,
        "row_count": row_count,
        "session_id": session_id,
        "message": "File uploaded successfully"
    }

@router.post("/create")
async def create_anki_deck(
    file: UploadFile = File(None),
    session_id: str = Form(None),
    deck_name: str = Form("Japanese Vocabulary"),
    enrich_cards: bool = Form(False),
    include_audio: bool = Form(False),
    include_examples: bool = Form(False),
    include_example_audio: bool = Form(False),
    use_core2000: bool = Form(False),
    field_mapping: str = Form(None)  # Optional JSON string of field mapping
):
    contents_str = None
    mapping_dict = None
    
    # Get content either from uploaded file or stored session
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        contents = await file.read()
        contents_str = contents.decode("utf-8")
    elif session_id and session_id in temp_storage:
        session_data = temp_storage[session_id]
        contents_str = session_data["content"]
        
        # Check if we have field mapping in the session data
        if "mapping" in session_data:
            mapping_dict = session_data["mapping"]
    else:
        raise HTTPException(status_code=400, detail="Either file or valid session_id must be provided")
    
    # Parse field mapping if provided directly
    if field_mapping:
        try:
            import json
            mapping_dict = json.loads(field_mapping)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid field mapping JSON: {str(e)}")
    
    try:
        # Enrich the content if requested
        if enrich_cards:
            from ..services.enrich_service import EnrichService
            enrich_service = EnrichService()
            
            # Extract Japanese words using field mapping if available
            japanese_words = []
            csv_rows = []
            headers = []
            japanese_column_index = 0  # Default to first column
            
            # Process CSV content
            for i, line in enumerate(contents_str.strip().split("\n")):
                # Skip Anki format directives
                if line.startswith("#"):
                    csv_rows.append(line)
                    continue
                
                # Parse CSV line
                import csv
                from io import StringIO
                
                # Check if it's tab-separated
                dialect = 'excel-tab' if "\t" in line else 'excel'
                row = next(csv.reader(StringIO(line), dialect=dialect))
                
                # Handle header row
                if i == 0:
                    headers = row
                    # Store the header row
                    csv_rows.append(line)
                    
                    # If we have mapping, find the Japanese column index
                    if mapping_dict and 'japanese' in mapping_dict:
                        japanese_field = mapping_dict['japanese']
                        if japanese_field in headers:
                            japanese_column_index = headers.index(japanese_field)
                    continue
                
                # Extract Japanese word from the appropriate column
                japanese_word = ""
                if 0 <= japanese_column_index < len(row):
                    japanese_word = row[japanese_column_index].strip()
                
                if japanese_word:
                    japanese_words.append(japanese_word)
                    
                csv_rows.append(line)
                
            # If we have Japanese words to enrich
            if japanese_words:
                # Create enriched data
                enriched_data = enrich_service.enrich_vocabulary(japanese_words)
                
                # Create new enriched CSV content
                new_csv_rows = []
                
                # Keep any Anki format directives
                for line in csv_rows:
                    if line.startswith("#"):
                        new_csv_rows.append(line)
                        
                # Add header row
                new_csv_rows.append("Japanese,English,Reading,Example,Tags")
                
                # Create enriched rows
                for word_info in enriched_data:
                    japanese = word_info["word"]
                    
                    # Get English meaning
                    english = ""
                    if "meanings" in word_info and word_info["meanings"]:
                        english = "; ".join(word_info["meanings"][:3])  # First 3 meanings
                        
                    # Get reading
                    reading = word_info.get("reading", word_info.get("romaji", ""))
                    
                    # Get example - either use existing example from the original CSV or get from enrichment
                    example = ""
                    
                    # Try to find the original example from the CSV if it exists
                    for orig_row in csv_rows:
                        if not orig_row.startswith("#"):  # Skip metadata
                            try:
                                dialect = 'excel-tab' if "\t" in orig_row else 'excel'
                                orig_fields = next(csv.reader([orig_row], dialect=dialect))
                                # If this is the row for our current word and it has an example
                                if orig_fields[0].strip() == japanese and len(orig_fields) > 3 and orig_fields[3].strip():
                                    example = orig_fields[3].strip()
                                    print(f"✓ Found existing example in CSV for '{japanese}': {example[:30]}...")
                                    break
                            except Exception as e:
                                print(f"Error parsing original row for examples: {e}")
                    
                    # If no example found in original CSV, get from enrichment
                    if not example and include_examples and "examples" in word_info and word_info["examples"]:
                        jp_example = word_info["examples"][0]["japanese"]
                        en_example = word_info["examples"][0]["english"]
                        example = f"{jp_example} ({en_example})"
                        print(f"+ Generated example for '{japanese}': {example}")
                        print(f"  Example source: API enrichment")
                    elif not include_examples:
                        print(f"- Examples disabled for '{japanese}'")
                    elif not example:
                        print(f"! No examples available for '{japanese}' in CSV or from API")
                        
                    # Debug log for example processing
                    if example:
                        print(f"DEBUG EXAMPLE: Word '{japanese}' has example: '{example}'")
                    else:
                        print(f"DEBUG EXAMPLE: Word '{japanese}' has NO example")
                    
                    # Get part of speech for tags
                    tags = []
                    if "parts_of_speech" in word_info and word_info["parts_of_speech"]:
                        for pos in word_info["parts_of_speech"]:
                            clean_tag = pos.lower().replace(' ', '_')
                            if clean_tag not in tags:
                                tags.append(clean_tag)
                                
                    # Default tag
                    if not tags:
                        tags.append("japanese")
                    
                    # Create CSV row
                    tags_str = " ".join(tags)
                    new_csv_rows.append(f"{japanese},{english},{reading},{example},{tags_str}")
                
                # Use the enriched content
                contents_str = "\n".join(new_csv_rows)
        
        # Create the deck using our internal model (for card count)
        deck = deck_service.create_deck_from_csv(contents_str, deck_name)
        
        # Generate Anki package with audio during creation phase
        print("Generating Anki package with audio during creation...")
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create the actual Anki package with audio now instead of during download
            if mapping_dict:
                # Use mapping-aware function if we have a mapping
                from ..services.anki_utils_mapping import create_anki_package_with_mapping
                print(f"Using custom field mapping: {mapping_dict}")
                anki_package = create_anki_package_with_mapping(
                    contents_str,
                    deck_name,
                    field_mapping=mapping_dict,
                    include_example_audio=include_example_audio,
                    enrich_cards=enrich_cards,
                    include_examples=include_examples
                )
            elif use_core2000:
                # Import Core2000 specific creator
                from ..services.anki_utils import create_core2000_package_from_csv
                print("Using Core 2000 style format...")
                print(f"Include example audio flag: {include_example_audio}")
                anki_package = create_core2000_package_from_csv(
                    contents_str, 
                    deck_name, 
                    include_example_audio=include_example_audio
                )
            else:
                # Import our more robust utility
                from ..services.anki_utils import create_anki_package_from_csv
                print(f"Using standard deck format with include_example_audio={include_example_audio}")
                anki_package = create_anki_package_from_csv(
                    contents_str, 
                    deck_name, 
                    include_example_audio=include_example_audio
                )
                
            # Save the package to a temporary file
            temp_file_path = os.path.join(temp_dir, f"{deck_name.replace(' ', '_')}.apkg")
            anki_package.write_to_file(temp_file_path)
            print(f"Created Anki package at: {temp_file_path}")
            
            # Store information for download with a sanitized ID
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            storage_id = f"deck_{timestamp}"
            
            # Store comprehensive information about the deck
            deck_info = {
                "temp_dir": temp_dir,
                "temp_file_path": temp_file_path,
                "name": deck_name,
                "include_audio": include_audio,
                "include_examples": include_examples,
                "include_example_audio": include_example_audio,
                "enriched": enrich_cards,
                "use_core2000": use_core2000,
                "created_at": timestamp,
                "file_size": os.path.getsize(temp_file_path) if os.path.exists(temp_file_path) else 0
            }
            
            # Add to storage with the deck ID as key
            temp_storage[storage_id] = deck_info
            
            # Log for debugging
            print(f"Created new deck with ID: {storage_id}")
            print(f"Current storage keys: {list(temp_storage.keys())}")
        except Exception as e:
            # Clean up in case of error
            shutil.rmtree(temp_dir)
            print(f"ERROR generating Anki package file: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to generate Anki package during creation: {str(e)}")
            
        
        return JSONResponse(
            content={
                "message": "Deck created successfully", 
                "deck_id": storage_id,
                "card_count": len(deck.cards),
                "enriched": enrich_cards,
                "core2000": use_core2000
            }, 
            status_code=201
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create deck: {str(e)}")
    

@router.get("/download/{deck_id}")
async def download_anki_deck(deck_id: str, background_tasks: BackgroundTasks):
    # Debug incoming request information
    print(f"Download request received for deck_id: {deck_id}")
    print(f"Available deck IDs in temp_storage: {list(temp_storage.keys())}")
    
    # Check if the deck exists in storage
    if deck_id not in temp_storage:
        raise HTTPException(status_code=404, detail=f"Deck ID {deck_id} not found in storage")
    
    # Check if the file path is available
    if "temp_file_path" not in temp_storage[deck_id]:
        raise HTTPException(status_code=404, detail=f"Deck file path not found for deck ID {deck_id}")
    
    deck_data = temp_storage[deck_id]
    deck_name = deck_data["name"]
    temp_file_path = deck_data["temp_file_path"]
    temp_dir = deck_data["temp_dir"]
    
    print(f"Serving pre-generated file: {temp_file_path}")
    
    try:
        # Verify the file exists and has content
        if not os.path.exists(temp_file_path):
            raise FileNotFoundError(f"The pre-generated Anki package file doesn't exist: {temp_file_path}")
            
        file_size = os.path.getsize(temp_file_path)
        if file_size < 1000:  # Very small file check
            print(f"WARNING: File size is suspiciously small: {file_size} bytes. This may indicate a problem with deck generation.")
            
        print(f"File exists and has size: {file_size} bytes")
    except Exception as e:
        # Clean up in case of error
        print(f"ERROR serving pre-generated Anki package file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to serve Anki package file: {str(e)}")
    
    # Clean up the temporary directory after the response is sent
    # We use add_task to ensure this happens after the file is served
    background_tasks.add_task(lambda: cleanup_temp_dir(temp_dir))
    
    # Return the pre-generated .apkg file
    return FileResponse(
        path=temp_file_path,
        filename=f"{deck_name.replace(' ', '_')}.apkg",
        media_type="application/octet-stream",
        background=background_tasks
    )

# Helper function for cleanup to avoid closure issues
def cleanup_temp_dir(dir_path):
    try:
        if os.path.exists(dir_path):
            print(f"Cleaning up temporary directory: {dir_path}")
            shutil.rmtree(dir_path)
        else:
            print(f"Directory already removed: {dir_path}")
    except Exception as e:
        print(f"Error cleaning up directory {dir_path}: {str(e)}")
        # We don't want to raise an exception here as it's a background task

@router.head("/{deck_id}")
async def check_deck_exists(deck_id: str):
    print(f"Checking if deck exists: {deck_id}")
    print(f"Available deck IDs: {list(temp_storage.keys())}")
    
    if deck_id not in temp_storage:
        print(f"Deck ID {deck_id} not found in storage")
        raise HTTPException(status_code=404, detail=f"Deck ID {deck_id} not found in storage")
    
    print(f"Deck ID {deck_id} found in storage")
    return Response(status_code=200)
    
@router.get("/session/{session_id}")
async def get_session_details(session_id: str):
    """Get details about an upload session to support progress tracking"""
    if session_id not in temp_storage:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = temp_storage[session_id]
    # Count how many words are in the session
    row_count = 0
    if "content" in session_data:
        content = session_data["content"]
        # Count non-empty, non-comment lines
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                row_count += 1
        
        # Subtract 1 if the first non-comment line might be a header
        first_non_comment_line = next((line for line in content.splitlines() if line.strip() and not line.strip().startswith('#')), "")
        if first_non_comment_line:
            first_field = first_non_comment_line.split(',')[0].lower() if ',' in first_non_comment_line else first_non_comment_line.split('\t')[0].lower()
            if first_field in ["japanese", "front", "word"]:
                row_count = max(0, row_count - 1)
                
    return {
        "session_id": session_id,
        "filename": session_data.get("filename", "Unknown file"),
        "row_count": row_count
    }

# Add the sample cards endpoint after the upload endpoint
@router.post("/preview")
async def preview_anki_cards(
    file: UploadFile = File(None),
    session_id: str = Form(None),
    deck_name: str = Form("Japanese Vocabulary"),
    sample_count: int = Form(5),  # Default to showing 5 sample cards
    enrich_cards: bool = Form(False),
    include_audio: bool = Form(False),
    include_examples: bool = Form(False),
    include_example_audio: bool = Form(False),
    use_core2000: bool = Form(False),
    field_mapping: str = Form(None)  # Optional JSON string of field mapping
):
    """
    Generate a preview of sample cards that would be included in the deck
    without generating the full deck file.
    """
    contents_str = None
    mapping_dict = None
    
    # Get content either from uploaded file or stored session
    if file:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        contents = await file.read()
        contents_str = contents.decode("utf-8")
    elif session_id and session_id in temp_storage:
        session_data = temp_storage[session_id]
        contents_str = session_data["content"]
        
        # Check if we have field mapping in the session data
        if "mapping" in session_data:
            mapping_dict = session_data["mapping"]
    else:
        raise HTTPException(status_code=400, detail="Either file or valid session_id must be provided")
    
    # Parse field mapping if provided directly
    if field_mapping:
        try:
            mapping_dict = json.loads(field_mapping)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid field mapping JSON: {str(e)}")
    
    try:
        # Debug logs
        print(f"Preview request - session_id: {session_id}")
        print(f"Preview request - mapping_dict: {mapping_dict}")
        print(f"Preview request - content length: {len(contents_str) if contents_str else 0}")
        
        # Check if this is an Anki format file
        lines = contents_str.strip().split('\n')
        is_anki_format = False
        
        if lines and lines[0].startswith('#separator:'):
            is_anki_format = True
            print("Detected Anki format file")
            # For Anki format files, create cards directly
            dialect = 'excel'
            if '#separator:tab' in lines[0].lower():
                dialect = 'excel-tab'
                
            # Skip metadata lines
            metadata_count = 0
            for line in lines:
                if line.startswith('#'):
                    metadata_count += 1
                else:
                    break
            
            data_lines = lines[metadata_count:]
            
            # Create a minimal deck for preview
            anki_deck = AnkiDeck(name=deck_name)
            
            # Use csv reader to parse the data
            from io import StringIO
            import csv
            
            csv_reader = csv.reader(StringIO('\n'.join(data_lines)), dialect=dialect)
            has_headers = True
            
            # Check if we should skip headers
            for i in range(metadata_count):
                if lines[i].startswith('#columns:'):
                    print("Found #columns directive, treating first row as data")
                    has_headers = False
                    break
            
            # Process rows
            headers = None
            for row_idx, row in enumerate(csv_reader):
                if not row or len(row) < 2:
                    continue
                    
                if row_idx == 0 and has_headers:
                    headers = row
                    continue
                
                # Create a card with basic front/back info
                if len(row) >= 2:
                    front = row[0].strip() if row[0] else ""
                    back = row[1].strip() if len(row) > 1 and row[1] else ""
                    
                    card = AnkiCard(front=front, back=back)
                    
                    # Handle reading/pronunciation if available (column 3)
                    if len(row) >= 3 and row[2]:
                        card.reading = row[2].strip()
                    
                    # Handle tags if available
                    if len(row) >= 4 and row[3]:
                        tags = row[3].strip()
                        if tags:
                            card.tags = [tag.strip() for tag in tags.split(',')]
                    
                    anki_deck.cards.append(card)
                    
                    # Only get sample_count cards
                    if len(anki_deck.cards) >= sample_count:
                        break
        else:
            # Standard CSV processing
            anki_deck = deck_service.create_deck_from_csv_with_mapping(contents_str, deck_name, mapping_dict)
        
        # Debug logs for created deck
        print(f"Preview deck created - name: {anki_deck.name}, cards: {len(anki_deck.cards)}")
        if len(anki_deck.cards) == 0:
            print(f"WARNING: No cards created from CSV. Content preview: {contents_str[:200]}...")
        
        # Enrich sample cards if requested
        if enrich_cards and anki_deck.cards:
            from ..services.enrich_service import EnrichService
            enrich_service = EnrichService()
            
            # Only enrich up to sample_count cards to save resources
            cards_to_enrich = anki_deck.cards[:min(sample_count, len(anki_deck.cards))]
            
            # Gather Japanese words for batch enrichment
            japanese_words = [card.front for card in cards_to_enrich]
            
            # For each word, enrich the card
            for i, word in enumerate(japanese_words):
                if i >= len(cards_to_enrich):
                    break
                    
                card = cards_to_enrich[i]
                try:
                    # Look up the word
                    lookup_result = enrich_service.lookup_word(word)
                    
                    if lookup_result:
                        # Update card fields based on lookup
                        if "meanings" in lookup_result and lookup_result["meanings"]:
                            # Only update back if it's empty or consists of the same text as front
                            if not card.back or card.back.strip() == card.front.strip():
                                card.back = "; ".join(lookup_result["meanings"][:3])
                        
                        if "reading" in lookup_result and lookup_result["reading"]:
                            if not card.reading:
                                card.reading = lookup_result["reading"]
                        
                        # Add examples if requested
                        if include_examples and "examples" in lookup_result and lookup_result["examples"]:
                            card.example = lookup_result["examples"][0]["text"] if lookup_result["examples"] else ""
                    
                    # Generate audio for preview if requested
                    if include_audio:
                        try:
                            audio_path = enrich_service.generate_audio(word)
                            if audio_path and os.path.exists(audio_path):
                                # Store the audio file path for preview serving
                                card.audio = f"/api/deck/preview-audio/{os.path.basename(audio_path)}"
                        except Exception as audio_error:
                            print(f"Error generating preview audio for '{word}': {str(audio_error)}")
                    
                    # Generate example audio for preview if requested
                    if include_example_audio and card.example:
                        try:
                            example_audio_path = enrich_service.generate_example_audio(card.example)
                            if example_audio_path and os.path.exists(example_audio_path):
                                # Store the example audio file path for preview serving
                                card.example_audio = f"/api/deck/preview-audio/{os.path.basename(example_audio_path)}"
                        except Exception as example_audio_error:
                            print(f"Error generating preview example audio for '{card.example}': {str(example_audio_error)}")
                            
                except Exception as e:
                    print(f"Error enriching sample card for word {word}: {str(e)}")
        
        # Return only the requested number of sample cards
        sample_cards = anki_deck.cards[:min(sample_count, len(anki_deck.cards))]
        
        # Return the sample cards
        return {
            "deck_name": anki_deck.name,
            "sample_count": len(sample_cards),
            "total_cards": len(anki_deck.cards),
            "sample_cards": sample_cards
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")

@router.get("/preview-audio/{filename}")
async def serve_preview_audio(filename: str):
    """Serve audio files generated for preview purposes"""
    try:
        # Look for the audio file in the enrich service temp directory
        from ..services.enrich_service import EnrichService
        enrich_service = EnrichService()
        audio_path = os.path.join(enrich_service.temp_dir, filename)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=audio_path,
            filename=filename,
            media_type="audio/mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving audio: {str(e)}")