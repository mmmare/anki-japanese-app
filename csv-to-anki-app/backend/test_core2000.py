#!/usr/bin/env python
"""
Core 2000 Style Test

This script tests the Core 2000 style Anki package creation.
It creates a sample Core 2000 style Anki deck and inspects the output.
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

# Sample CSV with Japanese content
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好き (I like cats),animal noun
犬,dog,いぬ,犬を見ます (I see a dog),animal noun
本,book,ほん,本を読みます (I read a book),object noun"""

def inspect_core2000_package(apkg_path):
    """Inspect the contents of a Core 2000 style Anki package"""
    if not os.path.exists(apkg_path):
        print(f"Error: {apkg_path} does not exist")
        return False

    print(f"\n--- Inspecting Core 2000 Style Package: {apkg_path} ---")
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
            
            # Check audio files
            audio_files = [f for f in files if f.isdigit()]  # Audio files are renamed to numbers
            if audio_files:
                print(f"\nFound {len(audio_files)} potential media files in the package")
                # Check media mapping
                media_path = os.path.join(temp_dir, "media")
                if os.path.exists(media_path):
                    with open(media_path, 'r') as f:
                        media_content = f.read()
                        print(f"Media mapping: {media_content}")
            else:
                print("\nNo media files found in the package!")

            # Check database structure - Core 2000 should have two card templates
            db_path = os.path.join(temp_dir, "collection.anki2")
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check card templates
                    print("\nVerifying Core 2000 card templates:")
                    try:
                        cursor.execute("SELECT m.name, t.name FROM models m JOIN templates t ON t.mid = m.id")
                        templates = cursor.fetchall()
                        for model_name, template_name in templates:
                            print(f"  - Model '{model_name}' has template '{template_name}'")
                        
                        if not templates:
                            print("  No templates found in the database")
                    except Exception as e:
                        print(f"  Error querying templates: {e}")
                    
                    # Check note fields
                    print("\nVerifying note field structure:")
                    try:
                        cursor.execute("SELECT id, flds FROM notes LIMIT 1")
                        note = cursor.fetchone()
                        if note:
                            note_id, fields = note
                            field_values = fields.split('\x1f')  # Fields are separated by Unit Separator character
                            print(f"  Note {note_id} field count: {len(field_values)}")
                            print(f"  Fields: {field_values}")
                    except Exception as e:
                        print(f"  Error querying note fields: {e}")
                        
                    conn.close()
                except Exception as e:
                    print(f"Error examining database: {e}")
            else:
                print("\nNo collection database found in the package!")
            
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

def create_test_core2000_package():
    """Create a test Core 2000 style Anki package"""
    print("Creating Core 2000 style Anki package...")
    
    # Create a uniquely named output file in the current directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"core2000_test_{timestamp}.apkg"
    
    try:
        # Create package using our Core 2000 utility
        package = create_core2000_package_from_csv(TEST_CSV, "Core 2000 Style Deck")
        
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
        inspect_core2000_package(output_path)
        
        print(f"\nTest package created at: {os.path.abspath(output_path)}")
        print("To test the Core 2000 style deck:")
        print("1. Import this package into Anki")
        print("2. Open the 'Core 2000 Style Deck'")
        print("3. Note that there are TWO card types (Recognition and Production)")
        print("4. Check that the styling matches Core 2000 format")
        
        return output_path
        
    except Exception as e:
        print(f"Error creating test package: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=== Core 2000 Style Anki Package Test ===\n")
    output_path = create_test_core2000_package()
    
    if output_path and os.path.exists(output_path):
        print(f"\n✅ Test completed successfully. Package: {output_path}")
    else:
        print(f"\n❌ Test failed!")
        sys.exit(1)
