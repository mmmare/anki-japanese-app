#!/usr/bin/env python
"""
Example Sentence Fix Verification Test

This script tests the fixes for example sentences and audio in Anki decks.
It creates two test decks - one with example audio enabled and one with it disabled,
then verifies that the audio files and references are correctly included.
"""

import os
import sys
import tempfile
import zipfile
import sqlite3
import json
import datetime
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_core2000_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal
本,book,ほん,この本は面白いです。(This book is interesting.),object"""

def create_test_decks():
    """Create two test decks - one with example audio enabled and one disabled"""
    print("=== Creating Test Anki Decks ===")
    
    # Current timestamp for unique filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a deck with example audio enabled
    print("\nCreating Core 2000 package WITH example audio...")
    enabled_path = f"example_audio_enabled_{timestamp}.apkg"
    enabled_package = create_core2000_package_from_csv(
        TEST_CSV, 
        "Example Audio Enabled",
        include_example_audio=True
    )
    enabled_package.write_to_file(enabled_path)
    print(f"✓ Created package at: {enabled_path}")
    
    # Create a deck with example audio disabled
    print("\nCreating Core 2000 package WITHOUT example audio...")
    disabled_path = f"example_audio_disabled_{timestamp}.apkg"
    disabled_package = create_core2000_package_from_csv(
        TEST_CSV, 
        "Example Audio Disabled",
        include_example_audio=False
    )
    disabled_package.write_to_file(disabled_path)
    print(f"✓ Created package at: {disabled_path}")
    
    return enabled_path, disabled_path

def examine_package(package_path):
    """Examine an Anki package to verify example sentences and audio"""
    print(f"\n=== Examining Package: {os.path.basename(package_path)} ===")
    
    if not os.path.exists(package_path):
        print(f"Error: Package doesn't exist at {package_path}")
        return False
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract the package contents
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Examine the media files
        print("\nMedia files:")
        media_files = [f for f in os.listdir(temp_dir) if f not in ['collection.anki2', 'media']]
        print(f"Found {len(media_files)} media files")
        
        # Count example audio files
        example_audio_files = [f for f in media_files if f.isdigit()]
        print(f"Found {len(example_audio_files)} potential audio files")
        
        # Examine the media mapping
        media_mapping = {}
        media_file = os.path.join(temp_dir, 'media')
        if os.path.exists(media_file):
            print("Media mapping file exists")
            try:
                with open(media_file, 'r') as f:
                    media_mapping = json.load(f)
                print(f"Media mapping contains {len(media_mapping)} entries")
                
                # Count example audio files in mapping
                example_audio_count = sum(1 for filename in media_mapping.values() if filename.startswith('example_'))
                print(f"Found {example_audio_count} example audio files in mapping")
                
                # Show example audio entries
                if example_audio_count > 0:
                    print("\nExample audio entries:")
                    for key, value in media_mapping.items():
                        if value.startswith('example_'):
                            print(f"  {key} -> {value}")
            except Exception as e:
                print(f"Error reading media mapping: {str(e)}")
        else:
            print("Media mapping file not found")
        
        # Examine the database
        db_path = os.path.join(temp_dir, 'collection.anki2')
        if os.path.exists(db_path):
            print("\nExamining database...")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check the note fields
            cursor.execute("SELECT id, flds FROM notes")
            notes = cursor.fetchall()
            print(f"Found {len(notes)} notes")
            
            example_audio_count = 0
            for note_id, fields in notes:
                field_values = fields.split("\x1f")  # Fields are separated by Unit Separator character
                
                if len(field_values) >= 6:  # Core 2000 format has 6 fields
                    example_audio_field = field_values[5]
                    if example_audio_field and "[sound:" in example_audio_field:
                        example_audio_count += 1
            
            print(f"Found {example_audio_count} notes with example audio references")
            
            conn.close()
        else:
            print("Database file not found")
        
        return True
    
    except Exception as e:
        print(f"Error examining package: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=== Example Sentence and Audio Fix Verification ===\n")
    
    # Create test decks
    enabled_path, disabled_path = create_test_decks()
    
    # Examine the enabled package
    print("\n--- Package WITH Example Audio ---")
    if os.path.exists(enabled_path):
        examine_package(enabled_path)
    else:
        print("Error: Enabled package not created")
    
    # Examine the disabled package
    print("\n--- Package WITHOUT Example Audio ---")
    if os.path.exists(disabled_path):
        examine_package(disabled_path)
    else:
        print("Error: Disabled package not created")
    
    print("\n=== Verification Complete ===")
    print(f"Package with example audio: {enabled_path}")
    print(f"Package without example audio: {disabled_path}")
    print("\nImport these packages into Anki to verify that example sentences and audio display correctly")
