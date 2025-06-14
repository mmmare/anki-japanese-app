#!/usr/bin/env python
"""
Standard Format Example Audio Test

This script tests the addition of example sentence audio to the standard Anki format.
It creates a sample Anki package with example audio enabled and verifies that the audio
files are correctly included in the package.
"""

import os
import sys
import tempfile
import zipfile
import sqlite3
import json
import datetime
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_anki_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal
本,book,ほん,この本は面白いです。(This book is interesting.),object"""

def create_test_standard_package():
    """Create a test standard Anki package with example audio"""
    print("Creating standard Anki package with example audio...")
    
    # Current timestamp for unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"standard_example_audio_{timestamp}.apkg"
    
    try:
        # Create the package with example audio enabled
        package = create_anki_package_from_csv(
            TEST_CSV, 
            "Standard Example Audio Test",
            include_example_audio=True
        )
        
        # Check for media files before writing
        if hasattr(package, 'media_files') and package.media_files:
            print(f"\nPackage has {len(package.media_files)} media files:")
            
            # Count vocabulary and example audio files
            vocab_files = [f for f in package.media_files if 'example_' not in os.path.basename(f)]
            example_files = [f for f in package.media_files if 'example_' in os.path.basename(f)]
            
            print(f"  - Vocabulary audio files: {len(vocab_files)}")
            for media_file in vocab_files:
                if os.path.exists(media_file):
                    print(f"    {os.path.basename(media_file)} ({os.path.getsize(media_file)} bytes)")
                else:
                    print(f"    {os.path.basename(media_file)} [FILE NOT FOUND]")
            
            print(f"  - Example audio files: {len(example_files)}")
            for media_file in example_files:
                if os.path.exists(media_file):
                    print(f"    {os.path.basename(media_file)} ({os.path.getsize(media_file)} bytes)")
                else:
                    print(f"    {os.path.basename(media_file)} [FILE NOT FOUND]")
        else:
            print("Warning: Package has no media files!")
        
        # Write the package
        package.write_to_file(output_path)
        print(f"\nPackage written to: {output_path}")
        
        # Examine the package
        examine_package(output_path)
        
        return output_path
        
    except Exception as e:
        print(f"Error creating package: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

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
        
        # Examine media files and mapping
        media_mapping = {}
        media_file = os.path.join(temp_dir, 'media')
        if os.path.exists(media_file):
            print("\nMedia mapping file exists")
            try:
                with open(media_file, 'r') as f:
                    media_mapping = json.load(f)
                print(f"Media mapping contains {len(media_mapping)} entries")
                
                # Count example audio files in mapping
                example_audio_count = sum(1 for filename in media_mapping.values() if filename.startswith('example_'))
                print(f"Found {example_audio_count} example audio files in mapping")
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
            
            # Check for model with ExampleAudio field
            cursor.execute("SELECT models FROM col")
            models_json = cursor.fetchone()[0]
            models = json.loads(models_json)
            
            found_model_with_example_audio = False
            for model_id, model in models.items():
                fields = [field["name"] for field in model.get("flds", [])]
                if "ExampleAudio" in fields:
                    found_model_with_example_audio = True
                    print(f"Found model with ExampleAudio field: {model.get('name', 'Unnamed')}")
                    print(f"Fields: {fields}")
            
            if not found_model_with_example_audio:
                print("No model with ExampleAudio field found!")
            
            # Check notes for ExampleAudio field
            cursor.execute("SELECT id, flds FROM notes")
            notes = cursor.fetchall()
            
            example_audio_count = 0
            for note_id, fields in notes:
                field_values = fields.split("\x1f")  # Fields are separated by Unit Separator character
                
                if len(field_values) >= 6:  # Should have 6 fields including ExampleAudio
                    example_audio_field = field_values[5]
                    if example_audio_field and "[sound:" in example_audio_field:
                        example_audio_count += 1
                        print(f"Note {note_id} has example audio: {example_audio_field}")
            
            print(f"\nFound {example_audio_count} notes with example audio references")
            
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
    print("=== Standard Format Example Audio Test ===\n")
    
    # Create and examine test package
    output_path = create_test_standard_package()
    
    if output_path and os.path.exists(output_path):
        print(f"\n✅ Test completed successfully. Package saved to: {output_path}")
        print("Import this package into Anki to verify that example sentences and audio display correctly")
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)
