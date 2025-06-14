#!/usr/bin/env python
"""
Test API calls for our Anki deck generator
"""

import requests
import json
import sys
import time

# The base URL for our API
BASE_URL = "http://localhost:8002/api/deck"

# Test data in both formats
STANDARD_CSV = """Japanese,English,Tags
こんにちは,Hello,greeting
ありがとう,Thank you,greeting
さようなら,Goodbye,greeting
はい,Yes,basic
いいえ,No,basic"""

ANKI_FORMAT_CSV = """#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front\tBack\tTags
こんにちは\tHello\tgreeting
ありがとう\tThank you\tgreeting
さようなら\tGoodbye\tgreeting
はい\tYes\tbasic
いいえ\tNo\tbasic"""

def test_standard_csv():
    """Test the API with standard CSV format"""
    print("\n=== Testing with Standard CSV Format ===")
    
    # Step 1: Upload the CSV
    files = {
        'file': ('japanese_vocab.csv', STANDARD_CSV, 'text/csv')
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
        'deck_name': 'Test Standard CSV Deck'
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
        
    # Step 3: Download the deck (we'll just check the endpoint works)
    print(f"Download URL: {BASE_URL}/download/{deck_id}")
    response = requests.head(f"{BASE_URL}/{deck_id}")
    
    if response.status_code == 200:
        print("Download endpoint is accessible")
    else:
        print(f"Download endpoint check failed: {response.status_code}")
    
def test_anki_format_csv():
    """Test the API with Anki-compatible tab-separated format"""
    print("\n=== Testing with Anki Tab-Separated Format ===")
    
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
        'deck_name': 'Test Anki Format Deck'
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
        
    # Step 3: Download the deck (we'll just check the endpoint works)
    print(f"Download URL: {BASE_URL}/download/{deck_id}")
    response = requests.head(f"{BASE_URL}/{deck_id}")
    
    if response.status_code == 200:
        print("Download endpoint is accessible")
    else:
        print(f"Download endpoint check failed: {response.status_code}")

if __name__ == "__main__":
    test_standard_csv()
    test_anki_format_csv()
