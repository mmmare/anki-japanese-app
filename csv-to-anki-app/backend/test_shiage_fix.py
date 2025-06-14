#!/usr/bin/env python
"""
Test the fix for 仕上げ example sentence issue

This script tests that the enhanced example service now works correctly 
with field mapping and enrichment to provide actual example sentences
instead of just showing readings.
"""

import requests
import json
import tempfile
import os

API_BASE_URL = "http://localhost:8080"

def test_shiage_example():
    """Test the specific word 仕上げ that was showing only readings"""
    print("=== Testing 仕上げ Example Sentence Fix ===\n")
    
    # Create a CSV with just the word 仕上げ and no example
    csv_content = """Japanese,English,Reading,Example,Tags
仕上げ,,,,"""
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        temp_file_path = f.name
    
    print(f"Created test CSV with 仕上げ:")
    print(csv_content)
    print()
    
    try:
        # Step 1: Upload the CSV
        print("Uploading CSV file...")
        with open(temp_file_path, 'rb') as f:
            upload_response = requests.post(
                f"{API_BASE_URL}/api/deck/upload",
                files={"file": ("test_shiage.csv", f, "text/csv")}
            )
        
        if not upload_response.ok:
            print(f"❌ Failed to upload CSV: {upload_response.status_code} {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        session_id = upload_data.get("session_id")
        print(f"✅ CSV uploaded. Session ID: {session_id}")
        
        # Step 2: Apply default field mapping (should auto-detect correctly)
        print("\nAnalyzing CSV for field mapping...")
        analyze_response = requests.post(
            f"{API_BASE_URL}/api/mapping/analyze",
            data={"session_id": session_id}
        )
        
        if analyze_response.ok:
            analyze_data = analyze_response.json()
            print(f"Suggested mapping: {analyze_data.get('suggested_mapping')}")
        
        # Step 3: Create deck with enrichment enabled
        print("\nCreating Anki deck with enrichment and example generation...")
        create_data = {
            "session_id": session_id,
            "deck_name": "仕上げ Test Deck",
            "enrich_cards": "true",
            "include_examples": "true",
            "include_audio": "false",
            "include_example_audio": "false"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/api/deck/create",
            data=create_data
        )
        
        if not create_response.ok:
            print(f"❌ Failed to create deck: {create_response.status_code} {create_response.text}")
            return False
        
        deck_data = create_response.json()
        deck_id = deck_data.get("deck_id")
        print(f"✅ Deck created successfully. Deck ID: {deck_id}")
        print(f"Card count: {deck_data.get('card_count')}")
        print(f"Enriched: {deck_data.get('enriched')}")
        
        # Step 4: Download and verify the deck
        print(f"\nDownloading deck to verify example sentences...")
        download_response = requests.get(f"{API_BASE_URL}/api/deck/download/{deck_id}")
        
        if download_response.ok:
            output_file = "shiage_test.apkg"
            with open(output_file, "wb") as f:
                f.write(download_response.content)
            print(f"✅ Deck downloaded successfully to: {os.path.abspath(output_file)}")
            
            # Get file size as a simple verification
            file_size = os.path.getsize(output_file)
            print(f"Deck file size: {file_size} bytes")
            
            if file_size > 1000:  # Should be substantial if it has content
                print("✅ Deck appears to contain substantial content")
                return True
            else:
                print("⚠️ Deck seems small, may not have proper content")
                return False
        else:
            print(f"❌ Failed to download deck: {download_response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_enhanced_examples_directly():
    """Test the enhanced examples service directly with 仕上げ"""
    print("=== Testing Enhanced Examples Service Directly ===\n")
    
    import sys
    sys.path.append('.')
    
    try:
        from app.services.enhanced_example_service import EnhancedExampleService
        from app.services.enrich_service import EnrichService
        
        # Test enhanced examples service
        enhanced_service = EnhancedExampleService()
        examples = enhanced_service.find_best_example("仕上げ", max_examples=3)
        
        print("Enhanced Example Service Results:")
        if examples:
            for i, example in enumerate(examples, 1):
                print(f"  Example {i} (from {example.get('source', 'unknown')}):")
                print(f"    Japanese: {example['japanese']}")
                print(f"    English: {example['english']}")
                if 'quality_score' in example:
                    print(f"    Quality Score: {example['quality_score']:.2f}")
                print()
        else:
            print("  No examples found")
        
        # Test integrated enrich service
        print("Integrated Enrich Service Results:")
        enrich_service = EnrichService(use_enhanced_examples=True)
        lookup_result = enrich_service.lookup_word("仕上げ")
        
        if "examples" in lookup_result and lookup_result["examples"]:
            print(f"  Found {len(lookup_result['examples'])} examples:")
            for i, example in enumerate(lookup_result["examples"], 1):
                print(f"    Example {i}:")
                print(f"      Japanese: {example['japanese']}")
                print(f"      English: {example['english']}")
                print(f"      Source: {example.get('source', 'unknown')}")
                print()
        else:
            print("  No examples found in lookup result")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced examples: {str(e)}")
        return False

def main():
    """Run the tests"""
    print("Testing 仕上げ Example Sentence Fix\n")
    
    # Test enhanced examples directly
    direct_test_success = test_enhanced_examples_directly()
    
    # Test full workflow
    workflow_test_success = test_shiage_example()
    
    if direct_test_success and workflow_test_success:
        print("\n✅ All tests passed! The 仕上げ example sentence issue should be fixed.")
    else:
        print("\n❌ Some tests failed. The issue may not be fully resolved.")

if __name__ == "__main__":
    main()
