#!/usr/bin/env python
"""
Test API for .apkg generation
"""

import requests
import json
import os

# The base URL for our API
BASE_URL = "http://localhost:8003/api/deck"

# Test data
ANKI_FORMAT_CSV = """#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front	Back	Tags
こんにちは	Hello	greeting
ありがとう	Thank you	greeting
さようなら	Goodbye	greeting
はい	Yes	basic
いいえ	No	basic"""

def test_api_apkg():
    """Test the API with Anki tab-separated format to generate .apkg file"""
    print("\n=== Testing API with Anki Format for .apkg Generation ===")
    
    # Step 1: Upload the CSV
    files = {
        'file': ('japanese_anki.csv', ANKI_FORMAT_CSV, 'text/csv')
    }
    
    response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Failed to upload CSV: {response.status_code}")
        print(response.text)
        return
        
    data = response.json()
    print(f"Upload response: {json.dumps(data, indent=2)}")
    
    session_id = data.get("session_id")
    if not session_id:
        print("No session ID returned")
        return
        
    # Step 2: Create the deck
    form_data = {
        'session_id': session_id,
        'deck_name': 'API Generated Deck'
    }
    
    response = requests.post(f"{BASE_URL}/create", data=form_data)
    
    if response.status_code != 201:
        print(f"Failed to create deck: {response.status_code}")
        print(response.text)
        return
        
    data = response.json()
    print(f"Create deck response: {json.dumps(data, indent=2)}")
    
    deck_id = data.get("deck_id")
    if not deck_id:
        print("No deck ID returned")
        return
    
    # Step 3: Download the .apkg file
    download_url = f"{BASE_URL}/download/{deck_id}"
    print(f"Downloading from: {download_url}")
    
    response = requests.get(download_url)
    
    if response.status_code != 200:
        print(f"Download failed: {response.status_code}")
        print(response.text)
        return
    
    # Save the downloaded file
    output_file = "api_output.apkg"
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    file_size = os.path.getsize(output_file)
    print(f"Downloaded file saved to {output_file} ({file_size} bytes)")
    
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")

if __name__ == "__main__":
    test_api_apkg()
