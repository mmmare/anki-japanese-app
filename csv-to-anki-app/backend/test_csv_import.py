#!/usr/bin/env python
"""
Test script to verify CSV parsing for different formats
"""

import csv
from io import StringIO
import sys

def test_csv_processing():
    """Test both standard CSV and Anki tab-separated formats"""
    
    # Test 1: Standard CSV
    standard_csv = """Japanese,English,Tags
こんにちは,Hello,greeting
ありがとう,Thank you,greeting
さようなら,Goodbye,greeting"""

    # Test 2: Anki-compatible tab-separated format
    anki_format = """#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front\tBack\tTags
こんにちは\tHello\tgreeting
ありがとう\tThank you\tgreeting
さようなら\tGoodbye\tgreeting"""

    print("=== Testing Standard CSV Format ===")
    process_csv(standard_csv)
    
    print("\n=== Testing Anki Tab-Separated Format ===")
    process_anki_format(anki_format)

def process_csv(file_content):
    """Process standard CSV format"""
    csv_file = StringIO(file_content)
    csv_reader = csv.reader(csv_file)
    
    for i, row in enumerate(csv_reader):
        if i == 0:  # Header row
            print(f"Header: {', '.join(row)}")
        else:
            if len(row) >= 2:
                front = row[0].strip()
                back = row[1].strip()
                tags = row[2].strip() if len(row) >= 3 else ""
                print(f"Card {i}: Front='{front}', Back='{back}', Tags='{tags}'")

def process_anki_format(file_content):
    """Process Anki tab-separated format"""
    lines = file_content.strip().split('\n')        # Check for Anki format directives
    is_anki_format = False
    dialect = 'excel'
    has_header = True
    
    if lines and lines[0].startswith('#separator:'):
        is_anki_format = True
        print("Detected Anki format with directives")
        
        # Count metadata lines to skip
        metadata_count = 0
        for line in lines:
            if line.startswith('#'):
                metadata_count += 1
                print(f"Metadata: {line}")
                # Check if we have a #columns directive which specifies fields
                if line.startswith('#columns:'):
                    has_header = False
                    print("Detected #columns directive, treating all rows as data (no header)")
            else:
                break
        
        # Use tab as separator for Anki format
        if '#separator:tab' in lines[0].lower():
            dialect = 'excel-tab'
            print("Using tab separator")
            
        print(f"Has header row: {has_header}")
        
        # Reconstruct content without metadata for CSV reader
        if metadata_count > 0:
            temp_content = '\n'.join(lines[metadata_count:])
            csv_file = StringIO(temp_content)
            
            csv_reader = csv.reader(csv_file, dialect=dialect)
            
            header_skipped = not has_header  # Skip header only if we don't have #columns directive
            
            for i, row in enumerate(csv_reader):
                if not header_skipped and i == 0:
                    print(f"Header: {', '.join(row)}")
                    header_skipped = True
                else:
                    if len(row) >= 2:
                        front = row[0].strip()
                        back = row[1].strip()
                        tags = row[2].strip() if len(row) >= 3 else ""
                        print(f"Card {i if has_header else i+1}: Front='{front}', Back='{back}', Tags='{tags}'")

if __name__ == "__main__":
    test_csv_processing()
