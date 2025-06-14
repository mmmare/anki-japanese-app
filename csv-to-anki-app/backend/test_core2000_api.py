#!/usr/bin/env python
"""
Core2000 Anki Format Test Script

This script tests the Core2000 format Anki deck generation with the web API.
"""

import requests
import json
import sys
import os
import tempfile
import zipfile
import sqlite3

# Configuration
BASE_URL = "http://localhost:8000"
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "core2000_sample.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "core2000_test_api.apkg")

def test_core2000_api():
    """Test Core2000 format using the API"""
    print("Testing Core2000 format with the API...")
    
    # Read the test CSV file
    if not os.path.exists(CSV_PATH):
        print(f"Error: Test CSV file not found at {CSV_PATH}")
        return False
        
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        csv_content = f.read()
        
    # Step 1: Upload the CSV content
    print("\nStep 1: Uploading CSV file...")
    files = {'file': ('core2000_test.csv', csv_content.encode('utf-8'), 'text/csv')}
    
    try:
        upload_response = requests.post(f"{BASE_URL}/api/deck/upload", files=files)
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        
        print(f"Upload successful: {upload_data}")
        session_id = upload_data.get('session_id')
        
        if not session_id:
            print("Error: No session ID in response")
            return False
    except Exception as e:
        print(f"Error uploading CSV: {e}")
        return False
    
    # Step 2: Create deck with Core2000 format
    print("\nStep 2: Creating Core2000 format deck...")
    
    form_data = {
        'session_id': session_id,
        'deck_name': 'Core2000 API Test',
        'enrich_cards': 'true',  # Enable enrichment to ensure all fields are filled
        'include_audio': 'true',  # Include audio for complete test
        'include_examples': 'true',  # Include examples for complete test
        'use_core2000': 'true'  # Enable Core2000 format
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/api/deck/create", data=form_data)
        create_response.raise_for_status()
        create_data = create_response.json()
        
        print(f"Deck creation successful: {create_data}")
        deck_id = create_data.get('deck_id')
        
        if not deck_id:
            print("Error: No deck ID in response")
            return False
    except Exception as e:
        print(f"Error creating deck: {e}")
        return False
    
    # Step 3: Download the Core2000 format deck
    print("\nStep 3: Downloading Core2000 format deck...")
    
    try:
        download_response = requests.get(f"{BASE_URL}/api/deck/download/{deck_id}")
        download_response.raise_for_status()
        
        # Save the downloaded file
        with open(OUTPUT_PATH, 'wb') as f:
            f.write(download_response.content)
        
        print(f"Deck downloaded successfully to {OUTPUT_PATH}")
        
        # Verify the downloaded file
        if os.path.exists(OUTPUT_PATH):
            file_size = os.path.getsize(OUTPUT_PATH)
            print(f"File size: {file_size} bytes")
            
            if file_size < 1000:
                print("Warning: File size is suspiciously small")
                return False
                
            # Analyze the .apkg file to verify Core2000 format
            analyze_apkg(OUTPUT_PATH)
            
            return True
        else:
            print("Error: Downloaded file not found")
            return False
    except Exception as e:
        print(f"Error downloading deck: {e}")
        return False

def analyze_apkg(apkg_path):
    """Analyze an Anki package file to verify Core2000 format"""
    print("\nAnalyzing Core2000 Anki package...")
    
    if not os.path.exists(apkg_path):
        print(f"Error: {apkg_path} does not exist")
        return False
        
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract the .apkg file (it's just a zip file)
        with zipfile.ZipFile(apkg_path, 'r') as z:
            print("\nContents of the .apkg file:")
            files = z.namelist()
            for f in files:
                info = z.getinfo(f)
                print(f"  - {f} ({info.file_size} bytes)")
                
            # Extract to temp directory
            z.extractall(temp_dir)
            
        # Check if collection.anki2 exists (SQLite database with deck info)
        db_path = os.path.join(temp_dir, "collection.anki2")
        if not os.path.exists(db_path):
            print("Error: collection.anki2 not found in package")
            return False
            
        # Connect to the SQLite database and check for Core2000 model
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for Core2000 model
        cursor.execute("SELECT models FROM col")
        models_json = cursor.fetchone()[0]
        models = json.loads(models_json)
        
        found_core2000 = False
        for model_id, model in models.items():
            if "Core 2000" in model.get("name", ""):
                found_core2000 = True
                print("\nFound Core 2000 model:")
                print(f"  - Name: {model.get('name')}")
                print(f"  - Fields: {[f.get('name') for f in model.get('flds', [])]}")
                
                # Check for the two card templates
                templates = model.get('tmpls', [])
                print(f"  - Card templates: {len(templates)}")
                for tmpl in templates:
                    print(f"    * {tmpl.get('name')}")
                
                # Check CSS styling
                css = model.get('css', '')
                print(f"  - CSS styling length: {len(css)} characters")
                if "japanese" in css.lower() and "reading" in css.lower():
                    print("  - Found Japanese styling in CSS")
                
        if not found_core2000:
            print("Error: No Core2000 model found in the package")
            return False
            
        # Check for notes
        cursor.execute("SELECT count(*) FROM notes")
        note_count = cursor.fetchone()[0]
        print(f"\nTotal notes in deck: {note_count}")
        
        # Check for cards (should be twice the number of notes for Core2000)
        cursor.execute("SELECT count(*) FROM cards")
        card_count = cursor.fetchone()[0]
        print(f"Total cards in deck: {card_count}")
        
        if card_count > 0 and card_count >= note_count:
            print("\nCard to note ratio analysis:")
            print(f"  - Cards per note: {card_count/note_count:.1f}")
            if card_count >= note_count * 1.5:
                print("  - ✓ Card count suggests multiple templates per note (Core2000 format)")
            else:
                print("  - ⚠ Card count suggests single template per note (not Core2000 format)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error analyzing .apkg file: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=== Core 2000 API Integration Test ===\n")
    success = test_core2000_api()
    
    if success:
        print("\n✅ Core2000 API integration test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Core2000 API integration test failed!")
        sys.exit(1)
