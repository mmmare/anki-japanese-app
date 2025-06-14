#!/usr/bin/env python
"""
Core 2000 Example Sentence Audio Test

This script tests the Core 2000 format with example sentence audio functionality.
It creates a sample Core 2000 style Anki deck with audio for both vocabulary words
and example sentences.
"""

import os
import sys
import tempfile
import zipfile
import random
import datetime
import sqlite3
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_core2000_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。可愛いですね。(I like cats. They're cute.),animal noun
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal noun
本,book,ほん,この本は面白いです。(This book is interesting.),object noun"""

def inspect_core2000_example_audio(apkg_path):
    """Inspect the contents of a Core 2000 style Anki package with example audio"""
    if not os.path.exists(apkg_path):
        print(f"Error: {apkg_path} does not exist")
        return False

    print(f"\n--- Inspecting Core 2000 Style Package with Example Audio: {apkg_path} ---")
    print(f"File size: {os.path.getsize(apkg_path)} bytes")
    
    # Extract to a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Anki packages are just zip files
        with zipfile.ZipFile(apkg_path, 'r') as z:
            print("\nContents of the .apkg file:")
            files = z.namelist()
            for f in files:
                info = z.getinfo(f)
                print(f"  - {f} ({info.file_size} bytes)")
            
            # Extract files
            z.extractall(temp_dir)
            
            # Check for audio files (both vocabulary and example)
            audio_files = [f for f in files if f.endswith('.mp3')]
            if audio_files:
                print(f"\nFound {len(audio_files)} audio files in the package:")
                
                # Separate vocabulary and example audio files
                vocab_audio = [f for f in audio_files if not f.startswith('example_')]
                example_audio = [f for f in audio_files if f.startswith('example_')]
                
                print(f"  - Vocabulary audio files: {len(vocab_audio)}")
                for audio in vocab_audio:
                    audio_path = os.path.join(temp_dir, audio)
                    print(f"     {audio} ({os.path.getsize(audio_path)} bytes)")
                    
                print(f"  - Example sentence audio files: {len(example_audio)}")
                for audio in example_audio:
                    audio_path = os.path.join(temp_dir, audio)
                    print(f"     {audio} ({os.path.getsize(audio_path)} bytes)")
            else:
                print("\nNo audio files found in the package!")

            # Examine the database to verify the example audio is properly referenced
            db_path = os.path.join(temp_dir, "collection.anki2")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check model fields
                print("\nChecking model fields:")
                cursor.execute("SELECT models FROM col")
                models_json = cursor.fetchone()[0]
                import json
                models = json.loads(models_json)
                
                core2000_model = None
                for model_id, model in models.items():
                    if "Core 2000" in model["name"]:
                        core2000_model = model
                        break
                        
                if core2000_model:
                    fields = [field["name"] for field in core2000_model["flds"]]
                    print(f"  Core 2000 model fields: {fields}")
                    
                    if "ExampleAudio" in fields:
                        print("  ✓ ExampleAudio field found in model")
                    else:
                        print("  ✗ ExampleAudio field not found in model")
                else:
                    print("  ✗ Core 2000 model not found")
                
                # Check notes for sound references in ExampleAudio field
                print("\nChecking notes for example audio references:")
                cursor.execute("SELECT id, flds FROM notes")
                notes = cursor.fetchall()
                
                example_audio_refs = 0
                for note_id, fields in notes:
                    field_values = fields.split("\x1f")  # Fields are separated by Unit Separator character
                    if len(field_values) >= 6:  # Check if we have at least 6 fields including ExampleAudio
                        example_audio_field = field_values[5]
                        if example_audio_field and "[sound:" in example_audio_field:
                            example_audio_refs += 1
                            print(f"  Note {note_id} contains example audio reference: {example_audio_field}")
                
                print(f"\n  Found {example_audio_refs} notes with example audio references")
                
                conn.close()
        
        return True
    except Exception as e:
        print(f"Error inspecting Core 2000 package: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

def create_test_core2000_example_audio_package():
    """Create a test Core 2000 style Anki package with example audio"""
    print("Creating test Core 2000 package with example sentence audio...")
    
    # Create a uniquely named output file in the current directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"core2000_example_audio_test_{timestamp}.apkg"
    
    try:
        # Create package using our Core 2000 utility
        package = create_core2000_package_from_csv(TEST_CSV, "Core 2000 Example Audio Test")
        
        # Check media files before writing
        if hasattr(package, 'media_files') and package.media_files:
            print(f"Package has {len(package.media_files)} media files:")
            
            vocab_files = [f for f in package.media_files if 'example_' not in os.path.basename(f)]
            example_files = [f for f in package.media_files if 'example_' in os.path.basename(f)]
            
            print(f"  - Vocabulary audio files: {len(vocab_files)}")
            for media_file in vocab_files:
                if os.path.exists(media_file):
                    print(f"    {os.path.basename(media_file)} ({os.path.getsize(media_file)} bytes)")
                else:
                    print(f"    {os.path.basename(media_file)} [FILE NOT FOUND]")
            
            print(f"  - Example sentence audio files: {len(example_files)}")
            for media_file in example_files:
                if os.path.exists(media_file):
                    print(f"    {os.path.basename(media_file)} ({os.path.getsize(media_file)} bytes)")
                else:
                    print(f"    {os.path.basename(media_file)} [FILE NOT FOUND]")
        else:
            print("Warning: Package has no media files!")
            
        # Write the package
        package.write_to_file(output_path)
        
        # Inspect the created package
        inspect_core2000_example_audio(output_path)
        
        print(f"\nTest package created at: {os.path.abspath(output_path)}")
        print("To test Core 2000 with example sentence audio:")
        print("1. Import this package into Anki")
        print("2. Open the 'Core 2000 Example Audio Test' deck")
        print("3. Review cards to hear both word and example sentence audio")
        print("4. Check that example sentences have their own audio buttons")
        
        return output_path
        
    except Exception as e:
        print(f"Error creating test package: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=== Core 2000 Example Sentence Audio Test ===\n")
    output_path = create_test_core2000_example_audio_package()
    
    if output_path and os.path.exists(output_path):
        print(f"\n✅ Test completed successfully. Package: {output_path}")
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)
