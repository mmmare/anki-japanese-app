"""
Field Mapping Service

This service handles CSV field detection and mapping to Anki fields.
"""
import csv
from io import StringIO
from typing import Dict, List, Tuple, Optional

class FieldMappingService:
    """Service for analyzing CSV files and suggesting field mappings"""
    
    # Standard field names for Japanese Anki cards
    JAPANESE_FIELD_NAMES = ['japanese', 'word', 'front', 'kanji', '日本語', 'vocabulary', 'expression']
    ENGLISH_FIELD_NAMES = ['english', 'meaning', 'translation', 'back', 'definition', '英語']
    READING_FIELD_NAMES = ['reading', 'pronunciation', 'kana', 'hiragana', 'yomigana', '読み方']
    EXAMPLE_FIELD_NAMES = ['example', 'sentence', 'usage', 'context', '例文', 'example sentence']
    TAG_FIELD_NAMES = ['tag', 'tags', 'category', 'categories', 'group']
    
    def analyze_csv_content(self, csv_content: str) -> Tuple[List[str], List[Dict], Dict[str, str]]:
        """
        Analyze CSV content to detect fields and suggest mappings
        
        Args:
            csv_content: The CSV file content as a string
            
        Returns:
            Tuple of (header_row, sample_data, suggested_mapping)
        """
        # Handle Anki format with directives
        lines = csv_content.strip().split('\n')
        if not lines:
            return [], [], {}
            
        start_line = 0
        dialect = 'excel'
        
        # Skip Anki directives if present
        if lines and lines[0].startswith('#'):
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    start_line = i + 1
                    if '#separator:tab' in line.lower():
                        dialect = 'excel-tab'
                else:
                    break
        
        try:
            # Try to detect dialect automatically for non-standard CSVs
            if start_line == 0:
                sample = '\n'.join(lines[:min(20, len(lines))])
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    print("Auto-detected CSV dialect")
                except:
                    print("Using default CSV dialect")
                    pass
            
            # Parse CSV to get headers and sample data
            csv_reader = csv.reader(StringIO('\n'.join(lines[start_line:])), dialect)
            
            # For large files, don't load everything into memory
            rows = []
            for i, row in enumerate(csv_reader):
                rows.append(row)
                if i >= 10:  # Only need header + sample rows
                    break
            
            if not rows:
                return [], [], {}
                
            headers = rows[0]
            
            # Handle case where CSV might have unusual formatting
            if len(headers) <= 1 and len(rows) > 1 and len(rows[1]) > 1:
                # First row might not be headers, use column indices as headers
                headers = [f"Column {i+1}" for i in range(len(rows[0]))]
                data_rows = rows[:5]  # Use all rows as data
            else:
                data_rows = rows[1:6] if len(rows) > 1 else []  # Get up to 5 sample rows
                
        except Exception as e:
            print(f"CSV parsing error: {str(e)}")
            return [], [], {}
        
        # Convert data rows to dicts for easier processing
        sample_data = []
        for row in data_rows:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i]
                else:
                    row_dict[header] = ''
            sample_data.append(row_dict)
            
        # Create suggested mapping
        suggested_mapping = self._suggest_field_mapping(headers, sample_data)
        
        return headers, sample_data, suggested_mapping

    def _suggest_field_mapping(self, headers: List[str], sample_data: List[Dict]) -> Dict[str, str]:
        """
        Suggest mapping from CSV headers to Anki fields
        
        Args:
            headers: List of CSV headers
            sample_data: List of dictionaries containing sample data
            
        Returns:
            Dictionary mapping Anki fields to CSV headers
        """
        mapping = {}
        
        # Initialize with empty mappings
        anki_fields = {
            'japanese': None,
            'english': None, 
            'reading': None,
            'example': None,
            'tags': None
        }
        
        # Helper function to detect Japanese characters
        def has_japanese_chars(text):
            return any(ord(c) > 0x3000 for c in text)
            
        # Step 1: Try to map based on header names
        for header in headers:
            header_lower = header.lower().strip()
            
            if header_lower in self.JAPANESE_FIELD_NAMES and not anki_fields['japanese']:
                anki_fields['japanese'] = header
                
            elif header_lower in self.ENGLISH_FIELD_NAMES and not anki_fields['english']:
                anki_fields['english'] = header
                
            elif header_lower in self.READING_FIELD_NAMES and not anki_fields['reading']:
                anki_fields['reading'] = header
                
            elif header_lower in self.EXAMPLE_FIELD_NAMES and not anki_fields['example']:
                anki_fields['example'] = header
                
            elif header_lower in self.TAG_FIELD_NAMES and not anki_fields['tags']:
                anki_fields['tags'] = header
        
        # Step 2: Try to detect fields based on content if headers weren't enough
        if sample_data:
            # For each column, analyze the content to guess what it might be
            for header in headers:
                # Skip already mapped fields
                if header in anki_fields.values():
                    continue
                    
                # Check content of this column in sample rows
                japanese_count = 0
                english_count = 0
                reading_kana_count = 0
                
                for row in sample_data:
                    if header in row:
                        value = row[header]
                        
                        # Count rows with Japanese characters
                        if has_japanese_chars(value):
                            japanese_count += 1
                            
                            # If it looks like a reading (mostly kana)
                            if all(0x3040 <= ord(c) <= 0x309F or 0x30A0 <= ord(c) <= 0x30FF or c.isspace() 
                                  for c in value if ord(c) > 127):
                                reading_kana_count += 1
                        
                        # Count rows that look like English definitions
                        elif value and all(ord(c) < 0x3000 for c in value):
                            english_count += 1
                
                # Make guesses based on content analysis
                if not anki_fields['japanese'] and japanese_count >= len(sample_data) * 0.7 and reading_kana_count < japanese_count:
                    anki_fields['japanese'] = header
                    
                elif not anki_fields['english'] and english_count >= len(sample_data) * 0.7:
                    anki_fields['english'] = header
                    
                elif not anki_fields['reading'] and reading_kana_count >= len(sample_data) * 0.7:
                    anki_fields['reading'] = header
        
        # Step 3: Use positional defaults if nothing else worked
        if not anki_fields['japanese'] and len(headers) > 0:
            anki_fields['japanese'] = headers[0]  # First column is typically Japanese
            
        if not anki_fields['english'] and len(headers) > 1:
            anki_fields['english'] = headers[1]  # Second column is typically English
            
        if not anki_fields['reading'] and len(headers) > 2:
            anki_fields['reading'] = headers[2]  # Third column is often reading
            
        if not anki_fields['example'] and len(headers) > 3:
            anki_fields['example'] = headers[3]  # Fourth column might be example
            
        if not anki_fields['tags'] and len(headers) > 4:
            anki_fields['tags'] = headers[4]  # Fifth column could be tags
            
        # Remove None values for cleaner output
        return {k: v for k, v in anki_fields.items() if v is not None}
