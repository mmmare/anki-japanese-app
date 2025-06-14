#!/usr/bin/env python
"""
Test Example Sentence Extraction and Audio Generation

This script tests the extraction of example sentences from CSV files
and the generation of audio for those example sentences.
"""

import os
import sys
import tempfile
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_core2000_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal
本,book,ほん,この本は面白いです。(This book is interesting.),object"""

def test_example_sentence_extraction():
    """Test example sentence extraction from CSV"""
    print("=== Testing Example Sentence Extraction ===")
    
    # Create a CSV reader to parse the test data
    import csv
    from io import StringIO
    
    reader = csv.reader(StringIO(TEST_CSV))
    next(reader)  # Skip the header
    
    # Process the rows to extract example sentences
    for i, row in enumerate(reader):
        japanese = row[0].strip()
        english = row[1].strip()
        reading = row[2].strip()
        example = row[3].strip() if len(row) > 3 else ""
        
        print(f"Word {i+1}: {japanese}")
        print(f"  Example: {example}")
        
        if "(" in example:
            japanese_part = example.split("(")[0].strip()
            english_part = example.split("(")[1].rstrip(")").strip()
            print(f"  Japanese part: {japanese_part}")
            print(f"  English part: {english_part}")
        else:
            print("  No English translation in parentheses")

def test_example_audio_generation():
    """Test example audio generation"""
    print("\n=== Testing Example Audio Generation ===")
    
    enrich_service = EnrichService()
    
    # Example sentences to test
    examples = [
        "猫が好きです。(I like cats.)",
        "私は犬と散歩します。(I walk with my dog.)",
        "この本は面白いです。(This book is interesting.)",
        "日本語の勉強は楽しいです。",  # No English translation
        "",  # Empty example
        "Hello, world!"  # No Japanese characters
    ]
    
    for i, example in enumerate(examples):
        print(f"\nExample {i+1}: '{example}'")
        
        audio_path = enrich_service.generate_example_audio(example)
        
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"  Success! Audio generated at: {audio_path} ({file_size} bytes)")
        else:
            print(f"  Failed to generate audio")

def test_anki_package_with_examples():
    """Test creating an Anki package with example sentences and audio"""
    print("\n=== Testing Anki Package Creation with Examples ===")
    
    # Create a temporary file to write the package
    temp_file = tempfile.NamedTemporaryFile(suffix='.apkg', delete=False)
    temp_file.close()
    output_path = temp_file.name
    
    # Create the Anki package with example sentences and audio
    try:
        print("Creating Core 2000 package with example audio...")
        package = create_core2000_package_from_csv(TEST_CSV, "Example Sentence Test", include_example_audio=True)
        
        # Save the package
        package.write_to_file(output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✓ Successfully created Anki package: {output_path} ({file_size} bytes)")
            return output_path
        else:
            print(f"\n✗ Failed to create Anki package")
            return None
            
    except Exception as e:
        print(f"\n✗ Error creating Anki package: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=== Example Sentence and Audio Testing ===\n")
    
    # Test example sentence extraction
    test_example_sentence_extraction()
    
    # Test example audio generation
    test_example_audio_generation()
    
    # Test Anki package creation with examples
    output_path = test_anki_package_with_examples()
    
    if output_path and os.path.exists(output_path):
        print(f"\n✅ All tests completed. Anki package saved to: {output_path}")
        print("Import this package into Anki to verify example sentences and audio are working.")
    else:
        print(f"\n❌ Tests failed!")
        sys.exit(1)
