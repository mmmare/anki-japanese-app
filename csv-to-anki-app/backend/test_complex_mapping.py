#!/usr/bin/env python
"""
Test script to demonstrate field mapping with a complex CSV format.

This script will:
1. Create a CSV file with an unusual format and structure
2. Process it through the field mapping API
3. Create an Anki deck with the appropriate mappings
"""
import os
import requests
import time
import tempfile
import csv
import json

# API base URL
API_BASE_URL = 'http://localhost:8080/api'

# Complex CSV with mixed column order and non-standard names
COMPLEX_CSV = """表現,意味,そのほか,読み方,例
法律,law,N1,ほうりつ,"法律を勉強しています。(I'm studying law.)"
辞書,dictionary,N3,じしょ,"辞書で調べてください。(Please look it up in a dictionary.)"
大学,university,N5,だいがく,"大学に行きます。(I go to university.)"
国際,international,N3,こくさい,"国際関係を学びたいです。(I want to study international relations.)"
市民,citizen,N2,しみん,"市民として投票は重要です。(Voting is important as a citizen.)"
"""

def test_complex_mapping():
    """Test field mapping with a complex CSV format"""
    print("\n=== Testing Field Mapping with Complex CSV Format ===\n")
    
    # 1. Create a temporary CSV file with complex format
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(COMPLEX_CSV)
        temp_file_path = temp_file.name
    
    print(f"Created temporary CSV file: {temp_file_path}")
    print(f"CSV content (complex format):\n{COMPLEX_CSV}")
    
    try:
        # 2. Upload the CSV file
        print("\nUploading complex CSV file...")
        with open(temp_file_path, 'rb') as f:
            upload_response = requests.post(
                f"{API_BASE_URL}/deck/upload",
                files={"file": ('complex_japanese_vocab.csv', f, 'text/csv')}
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
        print("\nAnalyzing complex CSV for field mapping suggestions...")
        with open(temp_file_path, 'rb') as f:
            analyze_response = requests.post(
                f"{API_BASE_URL}/mapping/analyze",
                files={"file": ('complex_japanese_vocab.csv', f, 'text/csv')}
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
        print(f"Sample Data: {json.dumps(sample_data[0] if sample_data else {}, ensure_ascii=False, indent=2)}")
        print(f"Suggested Mapping: {json.dumps(suggested_mapping, ensure_ascii=False, indent=2)}")
        
        # 4. Apply a custom field mapping
        print("\nApplying custom field mapping for complex format...")
        
        # Our custom mapping for the complex CSV
        # Format: {anki_field: csv_column}
        custom_mapping = {
            "japanese": "表現",     # "表現" (expression) maps to Japanese field
            "english": "意味",      # "意味" (meaning) maps to English field
            "reading": "読み方",     # "読み方" (reading) maps to Reading field
            "example": "例",        # "例" (example) maps to Example field
            "tags": "そのほか"       # "そのほか" (other) maps to Tags field
        }
        
        print(f"Custom Mapping: {json.dumps(custom_mapping, ensure_ascii=False, indent=2)}")
        
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
        
        print("✅ Complex field mapping applied successfully")
        
        # 5. Create the deck with the custom mapping
        print("\nCreating Anki deck with complex field mapping...")
        create_data = {
            "session_id": session_id,
            "deck_name": "Complex Mapping Test",
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
        print("\nDownloading complex mapping Anki deck...")
        download_response = requests.get(
            f"{API_BASE_URL}/deck/download/{deck_id}",
            stream=True
        )
        
        if not download_response.ok:
            print(f"❌ Failed to download deck: {download_response.status_code}")
            return False
        
        # Save the downloaded file
        download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "complex_mapping_test.apkg")
        with open(download_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Deck downloaded successfully to: {download_path}")
        print("\n=== Complex Field Mapping Test Complete ===")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    if test_complex_mapping():
        print("\n✅ Complex field mapping test completed successfully")
    else:
        print("\n❌ Complex field mapping test failed")
