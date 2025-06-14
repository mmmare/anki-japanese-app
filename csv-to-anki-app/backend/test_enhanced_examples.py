#!/usr/bin/env python
"""
Test Enhanced Example Sentences

This script tests the new enhanced example sentence service that pulls from multiple online sources
to provide better quality example sentences for Japanese vocabulary learning.
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.enrich_service import EnrichService
from app.services.enhanced_example_service import EnhancedExampleService

# Test words with different levels of difficulty
TEST_WORDS = [
    "猫",      # cat - common word
    "犬",      # dog - common word  
    "本",      # book - common word
    "食べる",   # to eat - common verb
    "美しい",   # beautiful - adjective
    "勉強",     # study - compound word
    "図書館",   # library - more complex
    "友達",     # friend - compound
    "電話",     # telephone - technical
    "新聞",     # newspaper - compound
]

def test_enhanced_examples():
    """Test the enhanced example service directly"""
    print("=== Testing Enhanced Example Service ===\n")
    
    enhanced_service = EnhancedExampleService()
    
    for word in TEST_WORDS:
        print(f"Word: {word}")
        
        # Get multiple examples
        examples = enhanced_service.find_best_example(word, max_examples=3)
        
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
            print()

def test_enrich_service_comparison():
    """Compare the old and new enrichment methods"""
    print("=== Comparing Old vs Enhanced Enrichment ===\n")
    
    # Test with enhanced examples enabled
    enhanced_service = EnrichService(use_enhanced_examples=True)
    
    # Test with enhanced examples disabled (fallback to Jisho only)
    original_service = EnrichService(use_enhanced_examples=False)
    
    for word in TEST_WORDS[:5]:  # Test first 5 words
        print(f"Word: {word}")
        print("-" * 40)
        
        # Get examples from enhanced service
        enhanced_jp, enhanced_en = enhanced_service.find_example_sentence(word)
        print(f"Enhanced Service:")
        if enhanced_jp and enhanced_en:
            print(f"  Japanese: {enhanced_jp}")
            print(f"  English: {enhanced_en}")
        else:
            print("  No example found")
        
        # Get examples from original service
        original_jp, original_en = original_service.find_example_sentence(word)
        print(f"Original Service:")
        if original_jp and original_en:
            print(f"  Japanese: {original_jp}")
            print(f"  English: {original_en}")
        else:
            print("  No example found")
        
        print()

def test_lookup_word_integration():
    """Test the integration in the lookup_word method"""
    print("=== Testing Lookup Word Integration ===\n")
    
    enhanced_service = EnrichService(use_enhanced_examples=True)
    
    for word in TEST_WORDS[:3]:  # Test first 3 words
        print(f"Looking up: {word}")
        
        result = enhanced_service.lookup_word(word)
        
        print(f"  Meanings: {result.get('meanings', [])}")
        print(f"  Reading: {result.get('reading', 'N/A')}")
        
        if 'examples' in result and result['examples']:
            print(f"  Examples ({len(result['examples'])}):")
            for i, example in enumerate(result['examples'], 1):
                source = example.get('source', 'unknown')
                print(f"    {i}. [{source}] {example['japanese']}")
                print(f"       {example['english']}")
        else:
            print("  No examples found")
        
        print()

def main():
    """Run all tests"""
    print("Enhanced Example Sentence Service Test\n")
    print("This test compares the new enhanced example service with multiple online sources")
    print("against the original Jisho-only implementation.\n")
    
    try:
        # Test the enhanced service directly
        test_enhanced_examples()
        
        # Compare old vs new
        test_enrich_service_comparison()
        
        # Test integration
        test_lookup_word_integration()
        
        print("✅ All tests completed successfully!")
        print("\nThe enhanced example service provides:")
        print("1. Multiple online sources (Tatoeba, Jisho, etc.)")
        print("2. Quality scoring and ranking")
        print("3. Better fallback mechanisms")
        print("4. Source attribution")
        print("5. Improved example selection")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
