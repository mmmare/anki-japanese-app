"""
Router for vocabulary enrichment endpoints
"""
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import os
import tempfile
import csv
from io import StringIO
from typing import List, Dict, Optional
import json
import shutil
import uuid

from ..services.enrich_service import EnrichService

router = APIRouter(prefix="/api/enrich", tags=["enrich"])
enrich_service = EnrichService()

# Import temp_storage from deck_router to maintain consistency
from .deck_router import temp_storage

@router.post("/lookup")
async def lookup_japanese_word(word: str = Form(...)):
    """Look up a single Japanese word and return enriched information"""
    try:
        result = enrich_service.lookup_word(word)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error looking up word: {str(e)}")

@router.post("/translate-list")
async def translate_word_list(words: List[str]):
    """Translate a list of Japanese words"""
    try:
        enriched_words = enrich_service.enrich_vocabulary(words)
        return {"enriched_words": enriched_words}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating words: {str(e)}")

@router.post("/upload-and-enrich")
async def upload_and_enrich_vocabulary(
    file: UploadFile = File(...),
    include_examples: bool = Form(True),
    include_audio: bool = Form(True),
    background_tasks: BackgroundTasks = None
):
    """Upload a list of Japanese words and get enriched data"""
    if not file.filename.endswith(('.txt', '.csv')):
        raise HTTPException(status_code=400, detail="Only .txt or .csv files are allowed")
    
    try:
        # Read content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Process the file content to extract words
        japanese_words = []
        
        # Handle CSV files
        if file.filename.endswith('.csv'):
            csv_reader = csv.reader(StringIO(text_content))
            for row in csv_reader:
                if row and len(row) > 0:
                    japanese_words.append(row[0].strip())
        else:
            # Handle plain text files (one word per line)
            for line in text_content.split('\n'):
                word = line.strip()
                if word:
                    japanese_words.append(word)
        
        # Skip header row if it looks like one
        if japanese_words and japanese_words[0].lower() in ['japanese', 'word', 'front']:
            japanese_words = japanese_words[1:]
        
        # Limit the number of words processed
        if len(japanese_words) > 100:
            japanese_words = japanese_words[:100]
            
        # Create enriched data
        enriched_data = enrich_service.enrich_vocabulary(japanese_words)
        
        # Create a new CSV file
        temp_dir = tempfile.mkdtemp()
        output_filename = f"enriched_{file.filename.split('.')[0]}.csv"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Create the CSV content
        csv_content = enrich_service.create_enriched_csv(
            japanese_words, 
            include_examples=include_examples, 
            include_audio=include_audio
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Clean up the temporary directory after response is sent
        if background_tasks:
            background_tasks.add_task(shutil.rmtree, temp_dir)
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="text/csv",
            background=background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/enrich-word")
async def enrich_single_word(
    word: str = Form(...),
    generate_audio: bool = Form(False),
    background_tasks: BackgroundTasks = None
):
    """Enrich a single Japanese word with translations, examples and audio"""
    try:
        enriched_data = enrich_service.lookup_word(word)
        
        # Generate audio if requested
        if generate_audio:
            audio_path = enrich_service.generate_audio(word)
            if audio_path and os.path.exists(audio_path):
                enriched_data["audio_available"] = True
                return FileResponse(
                    path=audio_path,
                    filename=f"{word}.mp3",
                    media_type="audio/mp3",
                    background=background_tasks
                )
            else:
                enriched_data["audio_available"] = False
        
        return enriched_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enriching word: {str(e)}")

@router.get("/audio/{word}")
async def get_word_audio(word: str, background_tasks: BackgroundTasks):
    """Generate and return audio for a Japanese word"""
    try:
        audio_path = enrich_service.generate_audio(word)
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio generation failed")
        
        # Clean up the file after it's sent
        background_tasks.add_task(os.unlink, audio_path)
        
        return FileResponse(
            path=audio_path,
            filename=f"{word}.mp3",
            media_type="audio/mp3",
            background=background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@router.post("/collection/add-word")
async def add_word_to_collection(
    collection_id: Optional[str] = Form(None),
    word: str = Form(...),
    reading: Optional[str] = Form(None),
    meanings: Optional[str] = Form(None),
    parts_of_speech: Optional[str] = Form(None),
    examples: Optional[str] = Form(None),
    selected_sense_ids: Optional[str] = Form(None)  # New parameter for selected senses
):
    """Add a word to a collection for later deck creation"""
    try:
        if not collection_id:
            collection_id = str(uuid.uuid4())
        
        # Parse JSON strings if provided
        meanings_list = json.loads(meanings) if meanings else []
        parts_of_speech_list = json.loads(parts_of_speech) if parts_of_speech else []
        examples_list = json.loads(examples) if examples else []
        selected_sense_ids_list = json.loads(selected_sense_ids) if selected_sense_ids else None
        
        # Create word data structure
        word_data = {
            "word": word,
            "reading": reading,
            "meanings": meanings_list,
            "parts_of_speech": parts_of_speech_list,
            "examples": examples_list,
            "selected_sense_ids": selected_sense_ids_list,  # Store selected sense IDs
            "added_at": datetime.now().isoformat()
        }
        
        # Get or create collection
        collection = temp_storage.get(collection_id, {"words": []})
        
        # Check if word already exists
        existing_word = next((w for w in collection.get("words", []) if w["word"] == word), None)
        if existing_word:
            return {
                "collection_id": collection_id,
                "message": "Word already exists in collection",
                "word_count": len(collection.get("words", []))
            }
        
        # Add word to collection
        if "words" not in collection:
            collection["words"] = []
        collection["words"].append(word_data)
        
        # Save collection
        temp_storage[collection_id] = collection
        
        return {
            "collection_id": collection_id,
            "message": "Word added to collection",
            "word_count": len(collection["words"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding word to collection: {str(e)}")

@router.get("/collection/{collection_id}")
async def get_collection(collection_id: str):
    """Get collection details and word list"""
    try:
        collection = temp_storage.get(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return {
            "collection_id": collection_id,
            "words": collection.get("words", []),
            "word_count": len(collection.get("words", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving collection: {str(e)}")

@router.delete("/collection/{collection_id}/word")
async def remove_word_from_collection(collection_id: str, word: str = Form(...)):
    """Remove a word from collection"""
    try:
        collection = temp_storage.get(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        # Remove word from collection
        words = collection.get("words", [])
        collection["words"] = [w for w in words if w["word"] != word]
        
        # Save updated collection
        temp_storage[collection_id] = collection
        
        return {
            "collection_id": collection_id,
            "message": "Word removed from collection",
            "word_count": len(collection["words"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing word from collection: {str(e)}")

@router.post("/collection/{collection_id}/create-deck")
async def create_deck_from_collection(
    collection_id: str,
    deck_name: str = Form("Japanese Vocabulary"),
    include_audio: bool = Form(False),
    include_examples: bool = Form(False),
    include_example_audio: bool = Form(False),
    background_tasks: BackgroundTasks = None
):
    """Create an Anki deck from a word collection"""
    try:
        collection = temp_storage.get(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        words = collection.get("words", [])
        if not words:
            raise HTTPException(status_code=400, detail="Collection is empty")
        
        # Convert collection to CSV format
        csv_content = StringIO()
        writer = csv.writer(csv_content)
        
        # Write header
        headers = ["Japanese", "Reading", "English", "Part of Speech"]
        if include_examples:
            headers.extend(["Example Japanese", "Example English"])
        writer.writerow(headers)
        
        # Write word data
        for word_data in words:
            row = [
                word_data.get("word", ""),
                word_data.get("reading", ""),
                "; ".join(word_data.get("meanings", [])),
                "; ".join(word_data.get("parts_of_speech", []))
            ]
            
            if include_examples and word_data.get("examples"):
                examples = word_data.get("examples", [])
                if examples:
                    example = examples[0]  # Use first example
                    row.extend([
                        example.get("japanese", ""),
                        example.get("english", "")
                    ])
                else:
                    row.extend(["", ""])
            
            writer.writerow(row)
        
        # Get CSV content as string
        csv_content_str = csv_content.getvalue()
        
        # Create deck using the CSV content string
        from ..services.deck_service import DeckService
        deck_service = DeckService()
        
        # Create deck model from CSV content
        deck = deck_service.create_deck_from_csv(csv_content_str, deck_name)
        
        # Create temporary directory for the deck file
        temp_dir = tempfile.mkdtemp()
        deck_path = os.path.join(temp_dir, f"{deck_name.replace(' ', '_')}.apkg")
        
        try:
            # Create Anki package using the same utilities as deck_router
            if include_audio or include_example_audio:
                # Use the full-featured utility for audio
                from ..services.anki_utils import create_anki_package_from_csv
                anki_package = create_anki_package_from_csv(
                    csv_content_str, 
                    deck_name, 
                    include_example_audio=include_example_audio
                )
            else:
                # Use basic deck service for simple decks
                anki_package = deck_service.create_anki_package(deck)
                
            # Write the package to file
            anki_package.write_to_file(deck_path)
            
        except Exception as e:
            # Clean up on error
            shutil.rmtree(temp_dir)
            raise Exception(f"Failed to create Anki package: {str(e)}")
        
        # Schedule cleanup after file is served
        if background_tasks:
            background_tasks.add_task(shutil.rmtree, temp_dir)
        
        return FileResponse(
            deck_path,
            media_type='application/octet-stream',
            filename=f"{deck_name.replace(' ', '_')}.apkg",
            background=background_tasks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating deck from collection: {str(e)}")
