#!/usr/bin/env python
"""
Test script to verify deck creation and download functionality is working.
This will:
1. Create a simple CSV file with Japanese words
2. Send a request to create a deck
3. Attempt to download the deck using the returned ID
"""
import os
import requests
import time
import tempfile
import csv

# API base URL
API_BASE_URL = 'http://localhost:8000/api'

# Sample CSV content
SAMPLE_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,犬は可愛いです。(Dogs are cute.),animal
本,book,ほん,本を読みます。(I read a book.),object"""

def test_deck_creation_and_download():
    print("=== Testing Deck Creation and Download Flow ===\n")
    
    # 1. Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(SAMPLE_CSV)
        temp_file_path = temp_file.name
    
    print(f"Created temporary CSV file: {temp_file_path}")
    print(f"CSV content:\n{SAMPLE_CSV}")
    
    try:
        # 2. Upload the CSV file
        print("\nUploading CSV file...")
        with open(temp_file_path, 'rb') as f:
            upload_response = requests.post(
                f"{API_BASE_URL}/deck/upload",
                files={"file": ('japanese_vocab.csv', f, 'text/csv')}
            )
        
        if not upload_response.ok:
            print(f"❌ Failed to upload CSV: {upload_response.status_code} {upload_response.text}")
            return False
        
        # Get session ID from upload
        session_data = upload_response.json()
        session_id = session_data.get("session_id")
        
        if not session_id:
            print("❌ No session ID returned from upload")
            return False
        
        print(f"✅ CSV uploaded successfully. Session ID: {session_id}")
        
        # 3. Create the deck
        print("\nCreating Anki deck...")
        create_data = {
            "session_id": session_id,
            "deck_name": "Test Deck Download",
            "enrich_cards": "true",
            "include_audio": "true",
            "include_examples": "true",
            "include_example_audio": "true",
            "use_core2000": "true"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/deck/create",
            data=create_data
        )
        
        if not create_response.ok:
            print(f"❌ Failed to create deck: {create_response.status_code} {create_response.text}")
            return False
        
        # Extract deck ID from response
        deck_data = create_response.json()
        deck_id = deck_data.get("deck_id")
        
        if not deck_id:
            print("❌ No deck ID returned from create")
            return False
        
        print(f"✅ Deck created successfully. Deck ID: {deck_id}")
        print(f"Deck data: {deck_data}")
        
        # 4. Check if deck exists (HEAD request)
        print("\nChecking if deck exists...")
        check_response = requests.head(f"{API_BASE_URL}/deck/{deck_id}")
        
        if not check_response.ok:
            print(f"❌ Deck not found: {check_response.status_code}")
            return False
        
        print(f"✅ Deck exists and is ready for download")
        
        # 5. Download the deck
        print("\nDownloading Anki deck...")
        download_response = requests.get(
            f"{API_BASE_URL}/deck/download/{deck_id}",
            stream=True  # Important for binary files
        )
        
        if not download_response.ok:
            print(f"❌ Failed to download deck: {download_response.status_code} {download_response.text}")
            return False
        
        # Save the downloaded file
        output_path = "test_deck_download.apkg"
        with open(output_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Verify file was created and has content
        if not os.path.exists(output_path):
            print("❌ Output file was not created")
            return False
            
        file_size = os.path.getsize(output_path)
        print(f"✅ Deck downloaded successfully: {output_path} ({file_size} bytes)")
        
        if file_size < 1000:
            print("⚠️ Warning: File size is suspiciously small")
        
        print("\n=== Test completed successfully ===")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"Cleaned up temporary CSV file")

if __name__ == "__main__":
    test_deck_creation_and_download()
