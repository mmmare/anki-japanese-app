#!/usr/bin/env python
"""
Example Audio Flag Test

This script tests the Core 2000 format with the example audio flag functionality.
It creates two test decks - one with example audio enabled and one with it disabled.
"""

import os
import tempfile
import datetime
import zipfile
from app.services.anki_utils import create_core2000_package_from_csv

# Sample CSV with Japanese content and example sentences
TEST_CSV = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです。可愛いですね。(I like cats. They're cute.),animal noun
犬,dog,いぬ,私は犬と散歩します。(I walk with my dog.),animal noun
本,book,ほん,この本は面白いです。(This book is interesting.),object noun"""

def test_example_audio_flag():
    """Test the example audio flag by creating decks with it on and off"""
    print("\n=== Testing Example Audio Flag Functionality ===")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test with example audio enabled
    print("\n[1] Creating deck with example audio ENABLED...")
    output_with_audio = f"example_audio_enabled_{timestamp}.apkg"
    package_with_audio = create_core2000_package_from_csv(TEST_CSV, "Example Audio Test - Enabled", include_example_audio=True)
    package_with_audio.write_to_file(output_with_audio)
    
    # Test with example audio disabled
    print("\n[2] Creating deck with example audio DISABLED...")
    output_without_audio = f"example_audio_disabled_{timestamp}.apkg"
    package_without_audio = create_core2000_package_from_csv(TEST_CSV, "Example Audio Test - Disabled", include_example_audio=False)
    package_without_audio.write_to_file(output_without_audio)
    
    # Verify the differences between the two packages
    print("\n[3] Comparing the two packages...")
    
    # Extract both files to temporary directories
    temp_dir_with_audio = tempfile.mkdtemp()
    temp_dir_without_audio = tempfile.mkdtemp()
    
    with zipfile.ZipFile(output_with_audio, 'r') as z:
        z.extractall(temp_dir_with_audio)
        
    with zipfile.ZipFile(output_without_audio, 'r') as z:
        z.extractall(temp_dir_without_audio)
    
    # Count MP3 files in both directories
    mp3_files_with_audio = [f for f in os.listdir(temp_dir_with_audio) if f.endswith('.mp3')]
    mp3_files_without_audio = [f for f in os.listdir(temp_dir_without_audio) if f.endswith('.mp3')]
    
    example_audio_files = [f for f in mp3_files_with_audio if f.startswith('example_')]
    
    print(f"Total audio files in enabled deck: {len(mp3_files_with_audio)}")
    print(f"Total audio files in disabled deck: {len(mp3_files_without_audio)}")
    print(f"Example sentence audio files in enabled deck: {len(example_audio_files)}")
    print(f"Example sentence audio files in disabled deck: {len([f for f in mp3_files_without_audio if f.startswith('example_')])}")
    
    # Check if files contain ExampleAudio field with content
    print("\n[4] Checking SQLite database for ExampleAudio field content...")
    
    import sqlite3
    
    # Check enabled deck
    conn_enabled = sqlite3.connect(os.path.join(temp_dir_with_audio, "collection.anki2"))
    cursor_enabled = conn_enabled.cursor()
    cursor_enabled.execute("SELECT id, flds FROM notes")
    notes_enabled = cursor_enabled.fetchall()
    
    example_audio_count_enabled = sum(1 for _, fields in notes_enabled 
                                   if fields.split("\x1f")[5].strip() and "[sound:" in fields.split("\x1f")[5])
    
    conn_enabled.close()
    
    # Check disabled deck
    conn_disabled = sqlite3.connect(os.path.join(temp_dir_without_audio, "collection.anki2"))
    cursor_disabled = conn_disabled.cursor()
    cursor_disabled.execute("SELECT id, flds FROM notes")
    notes_disabled = cursor_disabled.fetchall()
    
    example_audio_count_disabled = sum(1 for _, fields in notes_disabled 
                                    if fields.split("\x1f")[5].strip() and "[sound:" in fields.split("\x1f")[5])
    
    conn_disabled.close()
    
    print(f"Notes with example audio content in enabled deck: {example_audio_count_enabled}")
    print(f"Notes with example audio content in disabled deck: {example_audio_count_disabled}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir_with_audio)
    shutil.rmtree(temp_dir_without_audio)
    
    print(f"\nTest packages created: \n- {output_with_audio} (with example audio)\n- {output_without_audio} (without example audio)")
    
    # Final verification
    if example_audio_count_enabled > 0 and example_audio_count_disabled == 0:
        print("\n✅ TEST PASSED: Example audio flag is working correctly!")
        return True
    else:
        print("\n❌ TEST FAILED: Example audio flag is not working as expected.")
        return False

if __name__ == "__main__":
    test_example_audio_flag()
