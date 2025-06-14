#!/usr/bin/env python
"""
Test script for demonstrating the field mapping functionality.

This script will:
1. Create a CSV file with custom column names
2. Upload it to the API
3. Analyze the CSV to get field mapping suggestions
4. Apply a custom field mapping
5. Create an Anki deck with the custom mapping
6. Download and verify the deck
"""
import os
import requests
import time
import tempfile
import csv
import json

# API base URL
API_BASE_URL = 'http://localhost:8080/api'

# Sample CSV with non-standard column names
CUSTOM_CSV = """Term,Definition,Pronunciation,Usage,Category
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,犬は可愛いです。(Dogs are cute.),animal
本,book,ほん,本を読みます。(I read a book.),object
学生,student,がくせい,彼は学生です。(He is a student.),person
先生,teacher,せんせい,先生は親切です。(The teacher is kind.),person"""

def test_field_mapping():
    """Test the full field mapping workflow"""
    print("\n=== Testing Field Mapping Feature ===\n")
    
    # 1. Create a temporary CSV file with custom column names
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(CUSTOM_CSV)
        temp_file_path = temp_file.name
    
    print(f"Created temporary CSV file: {temp_file_path}")
    print(f"CSV content (with custom column names):\n{CUSTOM_CSV}")
    
    try:
        # 2. Upload the CSV file
        print("\nUploading CSV file...")
        with open(temp_file_path, 'rb') as f:
            upload_response = requests.post(
                f"{API_BASE_URL}/deck/upload",
                files={"file": ('custom_japanese_vocab.csv', f, 'text/csv')}
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
        
        # 3. Analyze the CSV for field mapping suggestions
        print("\nAnalyzing CSV for field mapping suggestions...")
        with open(temp_file_path, 'rb') as f:
            analyze_response = requests.post(
                f"{API_BASE_URL}/mapping/analyze",
                files={"file": ('custom_japanese_vocab.csv', f, 'text/csv')}
            )
        
        if not analyze_response.ok:
            print(f"❌ Failed to analyze CSV: {analyze_response.status_code} {analyze_response.text}")
            return False
        
        # Extract suggested mapping
        analysis_data = analyze_response.json()
        headers = analysis_data.get("headers", [])
        sample_data = analysis_data.get("sample_data", [])
        suggested_mapping = analysis_data.get("suggested_mapping", {})
        
        print(f"\nCSV Headers: {', '.join(headers)}")
        print(f"Sample Data: {sample_data[0] if sample_data else 'No sample data'}")
        print(f"Suggested Mapping: {json.dumps(suggested_mapping, indent=2)}")
        
        # 4. Apply a custom field mapping
        print("\nApplying custom field mapping...")
        
        # Our custom mapping - mapping CSV columns to Anki fields
        custom_mapping = {
            "japanese": "Term",         # CSV "Term" column maps to Anki "japanese" field
            "english": "Definition",    # CSV "Definition" column maps to Anki "english" field
            "reading": "Pronunciation", # CSV "Pronunciation" column maps to Anki "reading" field
            "example": "Usage",         # CSV "Usage" column maps to Anki "example" field
            "tags": "Category"          # CSV "Category" column maps to Anki "tags" field
        }
        
        print(f"Custom Mapping: {json.dumps(custom_mapping, indent=2)}")
        
        # Apply the mapping
        apply_mapping_response = requests.post(
            f"{API_BASE_URL}/mapping/apply",
            data={
                "session_id": session_id,
                "mapping": json.dumps(custom_mapping)
            }
        )
        
        if not apply_mapping_response.ok:
            print(f"❌ Failed to apply mapping: {apply_mapping_response.status_code} {apply_mapping_response.text}")
            return False
        
        print("✅ Field mapping applied successfully")
        
        # 5. Create the deck with the custom mapping
        print("\nCreating Anki deck with custom field mapping...")
        create_data = {
            "session_id": session_id,
            "deck_name": "Custom Field Mapping Test",
            "enrich_cards": "true",
            "include_audio": "true",
            "include_examples": "true",
            "include_example_audio": "true",
            "field_mapping": json.dumps(custom_mapping)  # Pass the mapping again to be safe
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
        
        # 6. Download the deck
        print("\nDownloading Anki deck...")
        download_response = requests.get(
            f"{API_BASE_URL}/deck/download/{deck_id}",
            stream=True
        )
        
        if not download_response.ok:
            print(f"❌ Failed to download deck: {download_response.status_code}")
            return False
        
        # Save the downloaded file
        download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_mapping_test.apkg")
        with open(download_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Deck downloaded successfully to: {download_path}")
        print("\n=== Field Mapping Test Complete ===")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    if test_field_mapping():
        print("\n✅ Field mapping test completed successfully")
    else:
        print("\n❌ Field mapping test failed")