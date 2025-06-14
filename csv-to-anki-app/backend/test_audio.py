#!/usr/bin/env python
"""
Test script to verify audio generation and inclusion in Anki packages
"""
import os
import sys
import tempfile
import genanki
from app.services.enrich_service import EnrichService
from app.services.anki_utils import create_anki_package_from_csv

# Simple CSV with Japanese words for testing
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好き (I like cats),animal
犬,dog,いぬ,犬を見ます (I see a dog),animal
本,book,ほん,本を読みます (I read a book),object"""

def test_audio_generation():
    """Test direct audio generation with EnrichService"""
    print("Testing EnrichService audio generation...")
    
    enrich_service = EnrichService()
    
    # Generate audio for a Japanese word
    japanese_word = "猫"
    audio_path = enrich_service.generate_audio(japanese_word)
    
    if audio_path and os.path.exists(audio_path):
        print(f"✓ Successfully generated audio: {audio_path}")
        print(f"  File size: {os.path.getsize(audio_path)} bytes")
    else:
        print(f"✗ Failed to generate audio for '{japanese_word}'")
        return False
    
    # Clean up
    try:
        os.remove(audio_path)
        print("✓ Successfully cleaned up audio file")
    except:
        print("✗ Failed to clean up audio file")
    
    return True

def test_anki_package_with_audio():
    """Test creating an Anki package with audio"""
    print("\nTesting Anki package creation with audio...")
    
    # Create a temp directory for the output
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "test_audio.apkg")
    
    try:
        # Create an Anki package
        package = create_anki_package_from_csv(TEST_CSV, "Audio Test Deck")
        
        # Check if media files are included
        if hasattr(package, 'media_files') and package.media_files:
            print(f"✓ Package has {len(package.media_files)} media files:")
            for media_file in package.media_files:
                print(f"  - {media_file}")
        else:
            print("✗ Package does not have media files")
        
        # Write to file
        package.write_to_file(output_path)
        
        if os.path.exists(output_path):
            print(f"✓ Successfully created Anki package: {output_path}")
            print(f"  File size: {os.path.getsize(output_path)} bytes")
        else:
            print(f"✗ Failed to create Anki package")
            return False
            
        print("\nImportant: To verify audio is working correctly:")
        print("1. Import the generated test_audio.apkg into Anki")
        print("2. Check if audio plays when you click on the cards")
        print("3. If you still have issues, verify that Anki can play audio in general")
        
        return True
    
    except Exception as e:
        print(f"✗ Error creating Anki package: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Audio Testing for Anki Packages ===\n")
    
    # Test audio generation
    if not test_audio_generation():
        print("Audio generation test failed!")
        sys.exit(1)
    
    # Test Anki package with audio
    if not test_anki_package_with_audio():
        print("Anki package with audio test failed!")
        sys.exit(1)
        
    print("\n=== All audio tests passed! ===")
