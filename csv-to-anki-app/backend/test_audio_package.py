#!/usr/bin/env python
"""
Advanced Anki Audio Test

This script creates a special test Anki deck with audio and prints detailed information
about how the audio files are packaged and embedded into the Anki deck.

It helps diagnose issues with audio not playing in Anki.
"""

import os
import sys
import tempfile
import zipfile
import random
import datetime
import sqlite3
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_anki_package_from_csv

# Sample CSV with Japanese content
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好き (I like cats),animal
犬,dog,いぬ,犬を見ます (I see a dog),animal
本,book,ほん,本を読みます (I read a book),object"""

def inspect_apkg_file(apkg_path):
    """Inspect the contents of an Anki .apkg file to verify audio files are included correctly"""
    if not os.path.exists(apkg_path):
        print(f"Error: {apkg_path} does not exist")
        return False

    print(f"\n--- Inspecting Anki package: {apkg_path} ---")
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
            
            # Audio files should be at the root level
            audio_files = [f for f in files if f.endswith('.mp3')]
            if audio_files:
                print(f"\nFound {len(audio_files)} audio files in the package:")
                for audio in audio_files:
                    audio_path = os.path.join(temp_dir, audio)
                    print(f"  - {audio} ({os.path.getsize(audio_path)} bytes)")
            else:
                print("\nNo audio files found in the package!")

            # Check if media file is referenced in the database
            db_path = os.path.join(temp_dir, "collection.anki2")
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Get notes with sound references
                    print("\nChecking note fields for sound references...")
                    cursor.execute("SELECT id, flds FROM notes")
                    notes = cursor.fetchall()
                    
                    sound_refs_found = False
                    for note_id, fields in notes:
                        if "[sound:" in fields:
                            print(f"  Note {note_id} contains sound reference: {fields[:80]}...")
                            sound_refs_found = True
                    
                    if not sound_refs_found:
                        print("  No sound references found in notes!")
                    
                    conn.close()
                except Exception as e:
                    print(f"Error examining database: {e}")
            else:
                print("\nNo collection database found in the package!")
                
        print("\nVerifying card templates for audio playback:")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, qfmt, afmt FROM templates")
            templates = cursor.fetchall()
            
            for template_id, name, qfmt, afmt in templates:
                print(f"\nTemplate: {name} (ID: {template_id})")
                print("Question format contains audio placeholder:", "[sound:" in qfmt or "{{Audio}}" in qfmt)
                if "{{Audio}}" in qfmt:
                    print("  - Found {{Audio}} reference in question format")
                if "[sound:" in qfmt:
                    print("  - Found [sound:...] tag in question format")
                
                print("Answer format contains audio placeholder:", "[sound:" in afmt or "{{Audio}}" in afmt)
                if "{{Audio}}" in afmt:
                    print("  - Found {{Audio}} reference in answer format")
                if "[sound:" in afmt:
                    print("  - Found [sound:...] tag in answer format")
            
            conn.close()
        except Exception as e:
            print(f"Error checking templates: {e}")
            
        return True
        
    except Exception as e:
        print(f"Error examining .apkg file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up - comment this out if you need to keep the extracted files
        import shutil
        shutil.rmtree(temp_dir)

def create_test_audio_package():
    """Create a test Anki deck with audio files"""
    print("Creating test Anki package with audio...")
    
    # Create a uniquely named output file in the current directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"audio_test_{timestamp}.apkg"
    
    try:
        # Create package using our utility
        package = create_anki_package_from_csv(TEST_CSV, "Audio Test Deck")
        
        # Check media files before writing
        if hasattr(package, 'media_files') and package.media_files:
            print(f"Package has {len(package.media_files)} media files:")
            for media_file in package.media_files:
                if os.path.exists(media_file):
                    print(f"  - {media_file} ({os.path.getsize(media_file)} bytes)")
                else:
                    print(f"  - {media_file} [FILE NOT FOUND]")
        else:
            print("Warning: Package has no media files!")
            
        # Write the package
        package.write_to_file(output_path)
        
        # Inspect the created package
        inspect_apkg_file(output_path)
        
        print(f"\nTest package created at: {os.path.abspath(output_path)}")
        print("To test audio:")
        print("1. Import this package into Anki")
        print("2. Open the 'Audio Test Deck'")
        print("3. Check if you can hear audio when reviewing cards")
        
        return output_path
        
    except Exception as e:
        print(f"Error creating test package: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=== Anki Audio Package Test ===\n")
    output_path = create_test_audio_package()
    
    if output_path and os.path.exists(output_path):
        print(f"\n✅ Test completed successfully. Package: {output_path}")
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)
