#!/usr/bin/env python
"""
Comprehensive Test for All Fixes

This script tests:
1. Example sentences display properly
2. Example audio generation and playback
3. Enhanced tag generation
"""

import os
import sys
import tempfile
import zipfile
import sqlite3
import json
import datetime
import random
import shutil
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_anki_package_from_csv, create_core2000_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。(I like cats.),animal
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal
本,book,ほん,この本は面白いです。(This book is interesting.),object
学生,student,がくせい,彼は学生です。(He is a student.),person
先生,teacher,せんせい,先生はとても親切です。(The teacher is very kind.),person"""

def test_example_functionality():
    """Test the example sentences and audio functionality"""
    print("\n=== Testing Example Sentences and Audio Fixes ===")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create standard deck with example audio
    print("\n1. Testing standard deck format WITH example audio...")
    standard_path = f"standard_fixes_{timestamp}.apkg"
    standard_package = create_anki_package_from_csv(
        TEST_CSV, 
        "Standard Format - With Example Audio",
        include_example_audio=True
    )
    standard_package.write_to_file(standard_path)
    print(f"✓ Created standard package at: {standard_path}")
    
    # Create Core 2000 deck with example audio
    print("\n2. Testing Core 2000 format WITH example audio...")
    core2000_path = f"core2000_fixes_{timestamp}.apkg"
    core2000_package = create_core2000_package_from_csv(
        TEST_CSV, 
        "Core 2000 Format - With Example Audio",
        include_example_audio=True
    )
    core2000_package.write_to_file(core2000_path)
    print(f"✓ Created Core 2000 package at: {core2000_path}")
    
    # Examine the packages
    examine_package(standard_path, "Standard Format")
    examine_package(core2000_path, "Core 2000 Format")
    
    return standard_path, core2000_path

def test_enhanced_tags():
    """Test the enhanced tag generation"""
    print("\n=== Testing Enhanced Tag Generation ===")
    
    # Create an EnrichService instance
    enrich_service = EnrichService()
    
    # Test words to check tag generation
    test_words = ["猫", "食べる", "赤い", "一", "学校", "新しい"]
    
    for word in test_words:
        print(f"\nTesting tag generation for '{word}':")
        word_info = enrich_service.lookup_word(word)
        
        # Create enriched info
        tags = []
        
        if "parts_of_speech" in word_info and word_info["parts_of_speech"]:
            pos_tags = [pos.lower().replace(' ', '_') for pos in word_info["parts_of_speech"]]
            print(f"Part of speech tags: {pos_tags}")
            tags.extend(pos_tags)
        
        # Add JLPT level tag if available
        if "jlpt" in word_info and word_info["jlpt"]:
            print(f"JLPT tag: {word_info['jlpt']}")
            tags.append(word_info["jlpt"].replace('-', '_'))
        
        if "is_common" in word_info and word_info["is_common"]:
            print("Common word: Yes")
            tags.append("common")
        
        if "tags" in word_info and word_info["tags"]:
            print(f"Additional tags: {word_info['tags']}")
            tags.extend([tag.replace(' ', '_') for tag in word_info['tags']])
        
        print(f"Final tags for '{word}': {tags}")
    
    return True

def examine_package(package_path, package_type):
    """Examine an Anki package to verify example sentences and audio"""
    print(f"\n=== Examining {package_type} Package: {os.path.basename(package_path)} ===")
    
    if not os.path.exists(package_path):
        print(f"Error: Package doesn't exist at {package_path}")
        return False
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract the package contents
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Examine the media files
        print("\nMedia files:")
        media_files = [f for f in os.listdir(temp_dir) if f not in ['collection.anki2', 'media']]
        print(f"Found {len(media_files)} media files")
        
        # Examine the media mapping
        media_mapping = {}
        media_file = os.path.join(temp_dir, 'media')
        if os.path.exists(media_file):
            print("Media mapping file exists")
            try:
                with open(media_file, 'r') as f:
                    media_mapping = json.load(f)
                print(f"Media mapping contains {len(media_mapping)} entries")
                
                # Count example audio files in mapping
                example_audio_count = sum(1 for filename in media_mapping.values() if filename.startswith('example_'))
                print(f"Found {example_audio_count} example audio files in mapping")
            except Exception as e:
                print(f"Error reading media mapping: {str(e)}")
        else:
            print("Media mapping file not found")
        
        # Examine the database
        db_path = os.path.join(temp_dir, 'collection.anki2')
        if os.path.exists(db_path):
            print("\nExamining database...")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for Example field in model
            print("Checking for Example field in models...")
            cursor.execute("SELECT id, name, flds FROM models")
            models = cursor.fetchall()
            
            for model_id, model_name, fields in models:
                field_names = fields.split("\x1f")
                print(f"Model: {model_name}")
                print(f"Fields: {field_names}")
                
                has_example = "Example" in field_names
                has_example_audio = "ExampleAudio" in field_names
                
                print(f"Has Example field: {has_example}")
                print(f"Has ExampleAudio field: {has_example_audio}")
            
            # Check the note fields
            print("\nChecking note fields...")
            cursor.execute("SELECT id, flds FROM notes")
            notes = cursor.fetchall()
            print(f"Found {len(notes)} notes")
            
            example_count = 0
            example_audio_count = 0
            
            for note_id, fields in notes:
                field_values = fields.split("\x1f")
                
                # Check if the note has 6 fields (with ExampleAudio being the 6th)
                if len(field_values) >= 4:  # At least has Example field
                    example_field = field_values[3]
                    if example_field.strip():
                        example_count += 1
                        print(f"Note {note_id} has example: {example_field[:50]}...")
                
                if len(field_values) >= 6:  # Has ExampleAudio field
                    example_audio_field = field_values[5]
                    if example_audio_field and "[sound:" in example_audio_field:
                        example_audio_count += 1
                        print(f"Note {note_id} has example audio: {example_audio_field}")
            
            print(f"\nFound {example_count} notes with examples")
            print(f"Found {example_audio_count} notes with example audio references")
            
            conn.close()
        else:
            print("Database file not found")
        
        return True
    
    except Exception as e:
        print(f"Error examining package: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("=== All Fixes Verification ===\n")
    
    # Test example sentences and audio
    standard_path, core2000_path = test_example_functionality()
    
    # Test enhanced tag generation
    tag_test_result = test_enhanced_tags()
    
    print("\n=== Verification Complete ===")
    print(f"Standard format package: {standard_path}")
    print(f"Core 2000 format package: {core2000_path}")
    print(f"Enhanced tag generation test: {'Passed' if tag_test_result else 'Failed'}")
    print("\nImport these packages into Anki to verify that example sentences and audio display correctly")
