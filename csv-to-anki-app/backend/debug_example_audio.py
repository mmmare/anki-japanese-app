#!/usr/bin/env python
"""
Debug Example Sentences and Audio in Anki Decks

This script tests the example sentences and audio in generated Anki decks by:
1. Creating a deck with example sentences and audio
2. Examining the generated .apkg file
3. Verifying that example sentences and audio are included
"""

import os
import sys
import tempfile
import zipfile
import sqlite3
import json
import re
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_core2000_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal
本,book,ほん,この本は面白いです。(This book is interesting.),object"""

def create_test_deck():
    """Create a test Anki deck with example sentences and audio"""
    print("=== Creating Test Anki Deck ===")
    
    # Create a temporary file for the package
    temp_file = tempfile.NamedTemporaryFile(suffix='.apkg', delete=False)
    temp_file.close()
    output_path = temp_file.name
    
    try:
        # Create a Core 2000 package with example audio enabled
        print("Creating Core 2000 package with example sentences and audio...")
        package = create_core2000_package_from_csv(TEST_CSV, "Example Debug Test", include_example_audio=True)
        
        # Save the package
        package.write_to_file(output_path)
        print(f"Saved package to {output_path}")
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"Package size: {file_size} bytes")
            return output_path
        else:
            print("Failed to create package")
            return None
    except Exception as e:
        print(f"Error creating deck: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def examine_anki_package(package_path):
    """Examine the contents of an Anki package"""
    print("\n=== Examining Anki Package Contents ===")
    
    if not os.path.exists(package_path):
        print(f"Package file does not exist: {package_path}")
        return False
        
    # Create a temporary directory to extract the package
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract the package
        print(f"Extracting package to {temp_dir}...")
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
        # List the extracted files
        files = os.listdir(temp_dir)
        print("Package contents:")
        for file in files:
            file_path = os.path.join(temp_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file} ({file_size} bytes)")
            
        # Look for media files
        media_file = os.path.join(temp_dir, 'media')
        if os.path.exists(media_file):
            print("\nExamining media file...")
            with open(media_file, 'r') as f:
                media_json = json.load(f)
                print(f"Media files: {len(media_json)}")
                
                # Count and categorize media files
                audio_files = [f for f in media_json.values() if f.endswith('.mp3')]
                example_audio_files = [f for f in audio_files if f.startswith('example_')]
                vocab_audio_files = [f for f in audio_files if not f.startswith('example_')]
                
                print(f"  - Total audio files: {len(audio_files)}")
                print(f"  - Vocabulary audio files: {len(vocab_audio_files)}")
                print(f"  - Example audio files: {len(example_audio_files)}")
                
                if example_audio_files:
                    print("\nExample audio files:")
                    for file in example_audio_files:
                        print(f"  - {file}")
        
        # Open and examine the SQLite database
        db_path = os.path.join(temp_dir, 'collection.anki2')
        if os.path.exists(db_path):
            print("\nExamining Anki database...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all notes
            cursor.execute("SELECT id, flds FROM notes")
            notes = cursor.fetchall()
            
            print(f"Found {len(notes)} notes in database")
            
            # Analyze each note
            for i, note in enumerate(notes):
                note_id, fields = note
                fields_list = fields.split("\x1f")  # Split by the field separator
                
                print(f"\nNote {i+1}:")
                
                # Print the fields based on our Core 2000 model
                if len(fields_list) >= 6:
                    print(f"  - Japanese: {fields_list[0]}")
                    print(f"  - Reading: {fields_list[1]}")
                    print(f"  - English: {fields_list[2]}")
                    print(f"  - Example: {fields_list[3]}")
                    print(f"  - Audio: {fields_list[4]}")
                    print(f"  - Example Audio: {fields_list[5]}")
                    
                    # Check for audio tags
                    if "[sound:" in fields_list[5]:
                        print(f"  ✅ Note has example audio tag: {fields_list[5]}")
                        
                        # Extract the filename
                        audio_filename = re.search(r'\[sound:(.*?)\]', fields_list[5])
                        if audio_filename:
                            filename = audio_filename.group(1)
                            print(f"  ✅ Example audio filename: {filename}")
                            
                            # Check if this file should exist in the media mapping
                            audio_id = None
                            for k, v in media_json.items():
                                if v == filename:
                                    audio_id = k
                                    break
                                    
                            if audio_id:
                                print(f"  ✅ Found in media mapping as file: {audio_id}")
                                
                                # Check if the file actually exists in the package
                                if os.path.exists(os.path.join(temp_dir, audio_id)):
                                    audio_size = os.path.getsize(os.path.join(temp_dir, audio_id))
                                    print(f"  ✅ Audio file exists in package: {audio_id} ({audio_size} bytes)")
                                else:
                                    print(f"  ❌ Audio file not found in package: {audio_id}")
                            else:
                                print(f"  ❌ Audio file not found in media mapping: {filename}")
                    else:
                        print(f"  ❌ Note does not have example audio tag")
                else:
                    print(f"  Note has {len(fields_list)} fields (expected 6)")
                    print(f"  Fields: {fields_list}")
            
            conn.close()
        
        return True
    except Exception as e:
        print(f"Error examining package: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=== Example Sentence and Audio Debug ===\n")
    
    # Create a test deck
    output_path = create_test_deck()
    
    if output_path and os.path.exists(output_path):
        # Examine the package
        examine_anki_package(output_path)
        print(f"\n✅ Debug completed. Test package saved to: {output_path}")
    else:
        print(f"\n❌ Failed to create test package")
        sys.exit(1)
