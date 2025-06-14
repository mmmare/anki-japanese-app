"""
Enhanced Example Sentence Service
This module provides improved example sentences from multiple online sources
"""
import requests
import time
import random
from typing import Dict, List, Optional, Tuple
import urllib.parse
import json

class EnhancedExampleService:
    """Service for getting high-quality example sentences from multiple online sources"""
    
    def __init__(self):
        """Initialize the enhanced example service"""
        self.sources = {
            'tatoeba': self._get_tatoeba_examples,
            'jisho': self._get_jisho_examples,
            'weblio': self._get_weblio_examples,
        }
        self.cache = {}  # Simple cache to avoid repeated API calls
        
    def find_best_example(self, japanese_word: str, max_examples: int = 3) -> List[Dict[str, str]]:
        """
        Find the best example sentences for a Japanese word from multiple sources
        
        Args:
            japanese_word: Japanese word to find examples for
            max_examples: Maximum number of examples to return
            
        Returns:
            List of example dictionaries with 'japanese', 'english', and 'source' keys
        """
        # Check cache first
        cache_key = f"{japanese_word}_{max_examples}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        all_examples = []
        
        # Try each source in order of preference
        for source_name, source_func in self.sources.items():
            try:
                examples = source_func(japanese_word, max_examples)
                for example in examples:
                    example['source'] = source_name
                    all_examples.append(example)
                
                # If we have enough good examples, we can stop
                if len(all_examples) >= max_examples:
                    break
                    
            except Exception as e:
                print(f"Error getting examples from {source_name}: {str(e)}")
                continue
        
        # Sort by quality and take the best ones
        best_examples = self._rank_examples(all_examples, japanese_word)[:max_examples]
        
        # Cache the results
        self.cache[cache_key] = best_examples
        
        return best_examples
    
    def _get_tatoeba_examples(self, word: str, max_examples: int = 3) -> List[Dict[str, str]]:
        """
        Get example sentences from Tatoeba database
        
        Args:
            word: Japanese word to search for
            max_examples: Maximum number of examples
            
        Returns:
            List of example dictionaries
        """
        examples = []
        
        try:
            # Tatoeba API endpoint
            encoded_word = urllib.parse.quote(word)
            url = f"https://tatoeba.org/en/api_v0/search?from=jpn&to=eng&query={encoded_word}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                for result in data['results'][:max_examples * 2]:  # Get more to filter better ones
                    if 'text' in result and 'translations' in result:
                        japanese_sentence = result['text']
                        
                        # Find English translation from nested structure
                        english_translation = None
                        for translation_group in result['translations']:
                            if isinstance(translation_group, list) and translation_group:
                                # Take the first translation from the first group
                                for translation in translation_group:
                                    if isinstance(translation, dict) and translation.get('lang') == 'eng':
                                        english_translation = translation.get('text', '')
                                        break
                                if english_translation:
                                    break
                            elif isinstance(translation_group, dict) and translation_group.get('lang') == 'eng':
                                # Handle case where translation_group is directly a dict
                                english_translation = translation_group.get('text', '')
                                break
                        
                        if english_translation and self._contains_word(japanese_sentence, word):
                            examples.append({
                                'japanese': japanese_sentence,
                                'english': english_translation,
                                'quality_score': self._calculate_quality_score(japanese_sentence, word)
                            })
                            
                            # Stop if we have enough good examples
                            if len(examples) >= max_examples:
                                break
            
        except Exception as e:
            print(f"Error accessing Tatoeba: {str(e)}")
        
        return examples
    
    def _get_jisho_examples(self, word: str, max_examples: int = 3) -> List[Dict[str, str]]:
        """
        Get example sentences from Jisho (fallback method)
        
        Args:
            word: Japanese word to search for
            max_examples: Maximum number of examples
            
        Returns:
            List of example dictionaries
        """
        examples = []
        
        try:
            # Import here to avoid circular dependencies
            try:
                from jisho_api.word import Word
            except ImportError:
                print("jisho_api not available")
                return examples
            
            response = Word.request(word)
            if response and response.data:
                result = response.data[0]
                
                if hasattr(result, "examples") and result.examples:
                    for example in result.examples[:max_examples]:
                        examples.append({
                            'japanese': example.japanese,
                            'english': example.english,
                            'quality_score': self._calculate_quality_score(example.japanese, word)
                        })
        
        except Exception as e:
            print(f"Error accessing Jisho: {str(e)}")
        
        return examples
    
    def _get_weblio_examples(self, word: str, max_examples: int = 3) -> List[Dict[str, str]]:
        """
        Get example sentences from Weblio (placeholder for now)
        
        Args:
            word: Japanese word to search for
            max_examples: Maximum number of examples
            
        Returns:
            List of example dictionaries
        """
        # Placeholder implementation - would need Weblio API key
        # For now, return empty list
        return []
    
    def _contains_word(self, sentence: str, word: str) -> bool:
        """
        Check if a sentence contains the target word
        
        Args:
            sentence: Japanese sentence to check
            word: Target word to find
            
        Returns:
            True if word is found in sentence
        """
        return word in sentence
    
    def _calculate_quality_score(self, sentence: str, target_word: str) -> float:
        """
        Calculate a quality score for an example sentence
        
        Args:
            sentence: Japanese sentence
            target_word: Target word
            
        Returns:
            Quality score (higher is better)
        """
        score = 0.0
        
        # Length preference - not too short, not too long
        length = len(sentence)
        if 10 <= length <= 50:
            score += 1.0
        elif 5 <= length <= 80:
            score += 0.5
        
        # Contains the exact target word
        if target_word in sentence:
            score += 2.0
        
        # Has appropriate punctuation
        if any(punct in sentence for punct in ['。', '！', '？']):
            score += 0.5
        
        # Contains common particles (indicates natural Japanese)
        particles = ['は', 'が', 'を', 'に', 'で', 'と', 'から', 'まで']
        particle_count = sum(1 for p in particles if p in sentence)
        score += min(particle_count * 0.2, 1.0)
        
        return score
    
    def _rank_examples(self, examples: List[Dict[str, str]], target_word: str) -> List[Dict[str, str]]:
        """
        Rank examples by quality
        
        Args:
            examples: List of example dictionaries
            target_word: Target word for ranking
            
        Returns:
            Sorted list of examples (best first)
        """
        # Sort by quality score (highest first)
        return sorted(examples, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    def get_example_with_fallback(self, word: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get a single best example with fallback compatibility for existing code
        
        Args:
            word: Japanese word to find example for
            
        Returns:
            Tuple of (Japanese sentence, English translation)
        """
        examples = self.find_best_example(word, max_examples=1)
        
        if examples:
            best_example = examples[0]
            return best_example['japanese'], best_example['english']
        
        return None, None
    
    def clear_cache(self):
        """Clear the example cache"""
        self.cache.clear()
