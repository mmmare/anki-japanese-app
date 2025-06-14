"""
Vocabulary Enrichment Service
This module adds English translations, example sentences, and audio for Japanese vocabulary
"""
import os
import re
import json
import tempfile
from typing import Dict, List, Optional, Tuple
import requests
from gtts import gTTS
from jisho_api.word import Word
from pykakasi import kakasi
from .enhanced_example_service import EnhancedExampleService

class EnrichService:
    """Service for enriching Japanese vocabulary with translations, examples, and audio"""
    
    def __init__(self, use_enhanced_examples: bool = True):
        """Initialize the enrichment service with necessary resources"""
        self.kakasi = kakasi()
        self.temp_dir = tempfile.mkdtemp()
        self.use_enhanced_examples = use_enhanced_examples
        
        # Initialize enhanced example service if enabled
        if self.use_enhanced_examples:
            self.enhanced_example_service = EnhancedExampleService()
        else:
            self.enhanced_example_service = None
        
    def lookup_word(self, japanese_word: str) -> Dict:
        """
        Look up Japanese word using Jisho API
        
        Args:
            japanese_word: Japanese word to look up
            
        Returns:
            Dictionary with translation information
        """
        try:
            response = Word.request(japanese_word)
            if response and response.data:
                # Get the first (most relevant) result
                result = response.data[0]
                
                # Extract relevant information
                info = {
                    "word": japanese_word,
                    "reading": result.japanese[0].reading if result.japanese[0].reading else "",
                    "meanings": [],
                    "parts_of_speech": [],
                    "examples": [],
                    "tags": [],
                    "is_common": result.is_common if hasattr(result, "is_common") else False,
                    "jlpt": result.jlpt[0] if hasattr(result, "jlpt") and result.jlpt else None,
                    "frequency": None  # Will estimate this later
                }
                
                # Calculate a rough frequency rank based on results order
                # This is just an approximation since Jisho API doesn't provide true frequency
                if hasattr(result, "jlpt") and result.jlpt:
                    level = result.jlpt[0]
                    if level == "jlpt-n5":
                        info["frequency"] = 500  # Most common words
                    elif level == "jlpt-n4":
                        info["frequency"] = 1000
                    elif level == "jlpt-n3":
                        info["frequency"] = 3000
                    elif level == "jlpt-n2":
                        info["frequency"] = 6000
                    elif level == "jlpt-n1":
                        info["frequency"] = 10000
                
                # Get English meanings and other metadata with sense grouping
                senses_info = []
                for sense_idx, sense in enumerate(result.senses):
                    sense_data = {
                        "id": sense_idx,
                        "meanings": sense.english_definitions,
                        "parts_of_speech": sense.parts_of_speech if sense.parts_of_speech else [],
                        "tags": sense.tags if hasattr(sense, "tags") and sense.tags else [],
                        "see_also": sense.see_also if hasattr(sense, "see_also") and sense.see_also else [],
                        "info": sense.info if hasattr(sense, "info") and sense.info else [],
                        "restrictions": sense.restrictions if hasattr(sense, "restrictions") and sense.restrictions else []
                    }
                    senses_info.append(sense_data)
                    
                    # Also add to flat lists for backwards compatibility
                    info["meanings"].extend(sense.english_definitions)
                    if sense.parts_of_speech:
                        info["parts_of_speech"].extend(sense.parts_of_speech)
                    
                    # Get tags from the senses if available
                    if hasattr(sense, "tags") and sense.tags:
                        info["tags"].extend(sense.tags)
                
                # Add structured senses information
                info["senses"] = senses_info
                
                # Get example sentences - use enhanced service if available
                if self.use_enhanced_examples and self.enhanced_example_service:
                    try:
                        enhanced_examples = self.enhanced_example_service.find_best_example(japanese_word, max_examples=3)
                        for enhanced_example in enhanced_examples:
                            info["examples"].append({
                                "japanese": enhanced_example["japanese"],
                                "english": enhanced_example["english"],
                                "source": enhanced_example.get("source", "enhanced")
                            })
                    except Exception as e:
                        print(f"Enhanced examples failed, falling back to Jisho: {str(e)}")
                        # Fallback to Jisho examples
                        if hasattr(result, "examples") and result.examples:
                            for example in result.examples[:3]:
                                info["examples"].append({
                                    "japanese": example.japanese,
                                    "english": example.english,
                                    "source": "jisho"
                                })
                else:
                    # Use original Jisho examples
                    if hasattr(result, "examples") and result.examples:
                        for example in result.examples[:3]:  # Limit to first 3 examples
                            info["examples"].append({
                                "japanese": example.japanese,
                                "english": example.english,
                                "source": "jisho"
                            })
                
                return info
            else:
                return {"word": japanese_word, "error": "Word not found"}
        except Exception as e:
            print(f"Error looking up word '{japanese_word}': {str(e)}")
            return {"word": japanese_word, "error": str(e)}
    
    def generate_audio(self, japanese_word: str) -> str:
        """
        Generate audio file for Japanese word
        
        Args:
            japanese_word: Japanese word to generate audio for
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Create a more robust filename for Anki compatibility
            # Replace non-ASCII chars with their hex codes to ensure uniqueness
            safe_name = ""
            for char in japanese_word:
                if ord(char) < 128 and char.isalnum():
                    safe_name += char
                else:
                    safe_name += f"_{ord(char):x}"
            
            # Ensure filename is not too long
            if len(safe_name) > 40:
                safe_name = safe_name[:40]
                
            # Add a random component to avoid collisions
            import random
            safe_name += f"_{random.randint(1000, 9999)}"
            
            filename = os.path.join(self.temp_dir, f"{safe_name}.mp3")
            
            # Generate audio using gTTS (Google Text-to-Speech)
            tts = gTTS(japanese_word, lang='ja')
            tts.save(filename)
            
            print(f"Generated audio for '{japanese_word}' at {filename}")
            return filename
        except Exception as e:
            print(f"Error generating audio for '{japanese_word}': {str(e)}")
            return ""
    
    def generate_example_audio(self, example_text: str) -> str:
        """
        Generate audio for a Japanese example sentence
        
        Args:
            example_text: Japanese example sentence to convert to audio
            
        Returns:
            Path to the generated audio file
        """
        print(f"=== GENERATING EXAMPLE AUDIO ===")
        print(f"Input example text: '{example_text}'")
        
        try:
            # Extract just the Japanese part if there's an English translation in parentheses
            japanese_part = example_text
            
            # Handle different formats of example sentences
            if '(' in example_text:
                # Format: "猫が好きです。(I like cats.)"
                japanese_part = example_text.split('(')[0].strip()
                print(f"Extracted Japanese part from parentheses format: '{japanese_part}'")
            elif ' - ' in example_text:
                # Format: "猫が好きです。 - I like cats."
                japanese_part = example_text.split(' - ')[0].strip()
                print(f"Extracted Japanese part from dash format: '{japanese_part}'")
            elif example_text.count('\n') == 1:
                # Format with newline separating Japanese and English
                japanese_part = example_text.split('\n')[0].strip()
                print(f"Extracted Japanese part from newline format: '{japanese_part}'")
                
            # Validate there's actually Japanese text to generate audio for
            if not japanese_part:
                print(f"⚠️ Empty example text after extraction")
                return ""
                
            # Check for Japanese characters - require at least one
            has_japanese = any(ord(c) > 127 for c in japanese_part)
            print(f"Has Japanese characters: {has_japanese}")
            
            if not has_japanese:
                print(f"⚠️ No Japanese characters found in example: '{japanese_part}'")
                return ""
            
            # Create a more robust filename for Anki compatibility
            # Use 'example_' prefix to distinguish from word audio files
            safe_name = "example_"
            for char in japanese_part[:20]:  # Just first 20 chars for filename
                if ord(char) < 128 and char.isalnum():
                    safe_name += char
                else:
                    safe_name += f"_{ord(char):x}"
            
            # Add a random component to avoid collisions
            import random
            safe_name += f"_{random.randint(1000, 9999)}"
            
            filename = os.path.join(self.temp_dir, f"{safe_name}.mp3")
            print(f"Audio will be saved to: {filename}")
            
            # Generate audio using gTTS (Google Text-to-Speech)
            print(f"Generating audio for Japanese text: '{japanese_part}'")
            tts = gTTS(japanese_part, lang='ja')
            tts.save(filename)
            
            # Verify the file was created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"✓ Successfully generated example audio: '{japanese_part}' at {filename} ({file_size} bytes)")
                return filename
            else:
                print(f"✗ Failed to generate example audio file at {filename}")
                return ""
        except Exception as e:
            print(f"Error generating example audio: {str(e)}")
            return ""
            
    def get_romaji(self, japanese_text: str) -> str:
        """
        Convert Japanese text to romaji
        
        Args:
            japanese_text: Japanese text to convert
            
        Returns:
            Romaji representation of the text
        """
        try:
            result = self.kakasi.convert(japanese_text)
            romaji_parts = [item['hepburn'] for item in result]
            return ' '.join(romaji_parts)
        except Exception as e:
            print(f"Error converting to romaji '{japanese_text}': {str(e)}")
            return japanese_text
    
    def enrich_vocabulary(self, words: List[str]) -> List[Dict]:
        """
        Enrich a list of Japanese words with translations, examples, and audio
        
        Args:
            words: List of Japanese words
            
        Returns:
            List of enriched word information
        """
        enriched_words = []
        
        for word in words:
            if not word.strip():
                continue
                
            # Basic info
            word_info = {"word": word}
            
            # Add romaji reading
            word_info["romaji"] = self.get_romaji(word)
            
            # Add dictionary lookup info
            lookup_info = self.lookup_word(word)
            word_info.update(lookup_info)
            
            # Generate audio file
            audio_path = self.generate_audio(word)
            if audio_path:
                word_info["audio_path"] = audio_path
            
            enriched_words.append(word_info)
        
        return enriched_words
    
    def find_example_sentence(self, word: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Find an example sentence using the word from enhanced sources
        
        Args:
            word: Japanese word to find examples for
            
        Returns:
            Tuple of (Japanese sentence, English translation)
        """
        try:
            # Use enhanced example service if available
            if self.use_enhanced_examples and self.enhanced_example_service:
                print(f"Using enhanced example service for word: {word}")
                return self.enhanced_example_service.get_example_with_fallback(word)
            
            # Fallback to original Jisho-only method
            print(f"Using fallback Jisho method for word: {word}")
            lookup_info = self.lookup_word(word)
            if "examples" in lookup_info and lookup_info["examples"]:
                example = lookup_info["examples"][0]
                return example["japanese"], example["english"]
            return None, None
        except Exception as e:
            print(f"Error finding example for '{word}': {str(e)}")
            return None, None
    
    def create_enriched_csv(self, words: List[str], include_examples: bool = True, 
                          include_audio: bool = True, format_type: str = "standard") -> str:
        """
        Create enriched CSV content from list of Japanese words
        
        Args:
            words: List of Japanese words
            include_examples: Whether to include example sentences
            include_audio: Whether to include audio references
            format_type: Format type ("standard" or "anki_tab")
            
        Returns:
            CSV content with enriched vocabulary
        """
        enriched_words = self.enrich_vocabulary(words)
        
        # Determine separator based on format type
        separator = '\t' if format_type == "anki_tab" else ','
        
        # Create CSV content with proper header 
        if format_type == "anki_tab":
            csv_rows = ["#separator:tab", "#html:true", f"Japanese{separator}English{separator}Reading{separator}Example{separator}Tags"]
        else:
            csv_rows = [f"Japanese{separator}English{separator}Reading{separator}Example{separator}Tags"]
        
        for word_info in enriched_words:
            japanese = word_info["word"]
            
            # Get English meaning
            english = ""
            if "meanings" in word_info and word_info["meanings"]:
                english = "; ".join(word_info["meanings"][:3])  # First 3 meanings
                # Escape commas and quotes in meanings to prevent CSV breakage
                english = english.replace('"', '""')
                if ',' in english:
                    english = f'"{english}"'
                
            # Get reading
            reading = word_info.get("reading", word_info.get("romaji", ""))
            if ',' in reading:
                reading = reading.replace('"', '""')
                reading = f'"{reading}"'
            
            # Get example
            example = ""
            if include_examples and "examples" in word_info and word_info["examples"]:
                jp_example = word_info["examples"][0]["japanese"]
                en_example = word_info["examples"][0]["english"]
                example = f"{jp_example} ({en_example})"
                # Escape commas and quotes in examples to prevent CSV breakage
                example = example.replace('"', '""')
                if ',' in example:
                    example = f'"{example}"'
            
            # Get part of speech and other useful tags
            tags = []
            
            # Add part of speech tags
            if "parts_of_speech" in word_info and word_info["parts_of_speech"]:
                for pos in word_info["parts_of_speech"]:
                    clean_tag = pos.lower().replace(' ', '_')
                    clean_tag = clean_tag.replace(',', '')  # Remove commas from tags
                    if clean_tag not in tags:
                        tags.append(clean_tag)
            
            # Add JLPT level tag if we can guess it based on word frequency/usage
            # This is a simple heuristic - you might replace with actual JLPT data
            if "frequency" in word_info and word_info["frequency"]:
                freq = word_info["frequency"]
                if freq <= 500:
                    tags.append("jlpt_n5")
                elif freq <= 1000:
                    tags.append("jlpt_n4")
                elif freq <= 3000:
                    tags.append("jlpt_n3")
                elif freq <= 6000:
                    tags.append("jlpt_n2")
                else:
                    tags.append("jlpt_n1")
            
            # Add tag for common words
            if "is_common" in word_info and word_info["is_common"]:
                tags.append("common")
            
            # Add tag for word length
            word_length = len(word_info["word"])
            if word_length == 1:
                tags.append("single_character")
            elif word_length == 2:
                tags.append("two_characters")
            elif word_length >= 6:
                tags.append("long_word")
            
            # Add tags based on meaning categories (if we can identify them)
            english_meanings = " ".join(word_info.get("meanings", []))
            
            if any(term in english_meanings.lower() for term in ["food", "eat", "drink", "meal", "fruit", "vegetable"]):
                tags.append("food")
            
            if any(term in english_meanings.lower() for term in ["color", "colour", "red", "blue", "green", "yellow"]):
                tags.append("color")
                
            if any(term in english_meanings.lower() for term in ["number", "count", "one", "two", "three", "first", "second"]):
                tags.append("number")
            
            # Create CSV row - using proper CSV writing to handle special characters
            from io import StringIO
            import csv
            output = StringIO()
            csv_writer = csv.writer(output)
            csv_writer.writerow([japanese, english, reading, example, " ".join(tags)])
            csv_row = output.getvalue().strip()
            csv_rows.append(csv_row)
        
        return "\n".join(csv_rows)
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        try:
            # Check if the directory still exists and if it's empty
            if os.path.exists(self.temp_dir) and not os.listdir(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temp directory: {self.temp_dir}")
            else:
                print(f"Not cleaning temp directory {self.temp_dir} - it's either not empty or already removed")
        except Exception as e:
            print(f"Error cleaning up temp directory: {str(e)}")
            
    def get_temp_dir(self):
        """Get the temporary directory path"""
        return self.temp_dir
