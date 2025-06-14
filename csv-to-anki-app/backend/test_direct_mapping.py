#!/usr/bin/env python
"""
Test script to verify that field mappings are correctly passed to anki_utils_mapping.

This test runs a direct function call to test the mapping-aware Anki package generator.
"""
import os
import sys
import tempfile
from pathlib import Path
import json

# Add app directory to path so we can import the services
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

# Import the necessary services
try:
    from services.anki_utils_mapping import create_anki_package_with_mapping
    from services.field_mapping_service import FieldMappingService
except ImportError as e:
    print(f"Error importing services: {e}")
    sys.exit(1)

# CSV with custom column headers
CUSTOM_CSV = """Term,Definition,Pronunciation,Usage,Category
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,犬は可愛いです。(Dogs are cute.),animal
本,book,ほん,本を読みます。(I read a book.),object
学生,student,がくせい,彼は学生です。(He is a student.),person
先生,teacher,せんせい,先生は親切です。(The teacher is kind.),person"""

def test_direct_mapping():
    print("\n=== Testing Direct Field Mapping with Anki Package Generator ===\n")
    
    try:
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary CSV file
            csv_path = os.path.join(temp_dir, "custom_vocab.csv")
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(CUSTOM_CSV)
            
            # Set up field mapping
            mapping = {
                "japanese": "Term",
                "english": "Definition",
                "reading": "Pronunciation",
                "example": "Usage",
                "tags": "Category"
            }
            
            # Output file path for the Anki package
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "mapping_direct_test.apkg"
            )
            
            print(f"CSV path: {csv_path}")
            print(f"Output path: {output_path}")
            print(f"Using mapping: {json.dumps(mapping, indent=2)}")
            
            # Read the CSV content
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
                
            # Create the Anki package with mapping
            result = create_anki_package_with_mapping(
                csv_content=csv_content,
                deck_name="Direct Mapping Test",
                field_mapping=mapping,
                include_example_audio=True
            )
            
            # Export the package
            if result:
                result.write_to_file(output_path)
            
            if result and os.path.exists(output_path):
                print(f"\n✅ Successfully created Anki package with field mapping at: {output_path}")
                print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")
                return True
            else:
                print("\n❌ Failed to create Anki package with field mapping")
                return False
                
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    if test_direct_mapping():
        print("\n✅ Direct mapping test completed successfully")
    else:
        print("\n❌ Direct mapping test failed")
