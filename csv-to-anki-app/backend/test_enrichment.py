"""
Test script for the Japanese vocabulary enrichment functionality
"""
import os
import sys
import json
from app.services.enrich_service import EnrichService

# Test words
TEST_WORDS = ["猫", "犬", "家", "食べる", "行く", "日本語"]

def test_lookup():
    """Test looking up a single word"""
    print("Testing word lookup...")
    enrich_service = EnrichService()
    
    for word in TEST_WORDS:
        print(f"\nLooking up: {word}")
        result = enrich_service.lookup_word(word)
        print(json.dumps(result, indent=2, ensure_ascii=False))

def test_romaji():
    """Test romaji conversion"""
    print("\nTesting romaji conversion...")
    enrich_service = EnrichService()
    
    for word in TEST_WORDS:
        romaji = enrich_service.get_romaji(word)
        print(f"{word} -> {romaji}")

def test_audio():
    """Test audio generation"""
    print("\nTesting audio generation...")
    enrich_service = EnrichService()
    
    for word in TEST_WORDS:
        print(f"Generating audio for: {word}")
        audio_path = enrich_service.generate_audio(word)
        if audio_path and os.path.exists(audio_path):
            size_kb = os.path.getsize(audio_path) / 1024
            print(f"  Success! File created at: {audio_path} ({size_kb:.1f} KB)")
        else:
            print(f"  Failed to generate audio for {word}")

def test_enrichment():
    """Test the full enrichment process"""
    print("\nTesting full enrichment process...")
    enrich_service = EnrichService()
    
    enriched_words = enrich_service.enrich_vocabulary(TEST_WORDS)
    print(f"Enriched {len(enriched_words)} words")
    
    # Print the first result in full
    if enriched_words:
        print("\nSample enriched word:")
        print(json.dumps(enriched_words[0], indent=2, ensure_ascii=False))
    
    # Generate CSV
    csv_content = enrich_service.create_enriched_csv(TEST_WORDS)
    print("\nGenerated CSV content:")
    print(csv_content)

def main():
    """Run all tests"""
    print("===== Japanese Vocabulary Enrichment Tests =====\n")
    
    # Run individual tests
    test_lookup()
    test_romaji()
    test_audio()
    test_enrichment()
    
    print("\nAll tests completed!")
    enrich_service = EnrichService()
    enrich_service.cleanup()

if __name__ == "__main__":
    main()
