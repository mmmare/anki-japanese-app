#!/usr/bin/env python
"""
CSV Example Sentence Debug Tool

This script helps debug CSV files that are having issues with example sentences.
It validates the CSV format and checks if example sentences are properly formatted.
"""

import sys
import csv
import os
from io import StringIO
import argparse
import colorama
from colorama import Fore, Style

# Initialize colorama for colored output
colorama.init(autoreset=True)

def detect_dialect(content):
    """Detect if the file is tab-separated or comma-separated"""
    if content.strip().startswith("#separator:tab"):
        return 'excel-tab'
    elif "\t" in content.split("\n")[0]:
        return 'excel-tab'
    else:
        return 'excel'

def check_csv_format(filepath):
    """Check the CSV format and identify potential issues"""
    print(f"\n{Fore.CYAN}Checking CSV file: {filepath}{Style.RESET_ALL}")
    
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
        return False
    
    # Detect dialect
    dialect = detect_dialect(content)
    print(f"Detected format: {Fore.GREEN}{dialect}{Style.RESET_ALL}")
    
    # Parse the CSV
    csv_rows = []
    lines = content.strip().split('\n')
    metadata_lines = [line for line in lines if line.startswith('#')]
    
    for meta in metadata_lines:
        print(f"{Fore.BLUE}Metadata: {meta}{Style.RESET_ALL}")
    
    # Skip metadata lines
    content_lines = [line for line in lines if not line.startswith('#')]
    
    # Parse first line to check for header
    if content_lines:
        first_row = []
        try:
            if dialect == 'excel-tab':
                # Tab-separated
                first_row = content_lines[0].split('\t')
            else:
                # Comma-separated
                first_row = next(csv.reader([content_lines[0]]))
            
            # Check if this looks like a header
            has_header = any(field.lower() in ['japanese', 'word', 'front'] for field in first_row)
            if has_header:
                print(f"{Fore.GREEN}Header detected: {' | '.join(first_row)}{Style.RESET_ALL}")
                start_idx = 1
            else:
                print(f"{Fore.YELLOW}No header detected. First row: {' | '.join(first_row)}{Style.RESET_ALL}")
                start_idx = 0
                
            # Check if there's an example column
            if len(first_row) >= 4:
                if has_header:
                    example_column_name = first_row[3]
                    print(f"{Fore.GREEN}Found example column: {example_column_name}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Assuming column 4 contains examples{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}CSV doesn't have enough columns for examples (needs at least 4){Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Error parsing CSV header: {e}{Style.RESET_ALL}")
            return False
            
    # Parse actual rows
    print(f"\n{Fore.CYAN}Checking example sentences:{Style.RESET_ALL}")
    row_count = 0
    examples_found = 0
    rows_with_examples = []
    
    for i in range(start_idx, len(content_lines)):
        try:
            if dialect == 'excel-tab':
                row = content_lines[i].split('\t')
            else:
                row = next(csv.reader([content_lines[i]]))
                
            row_count += 1
            japanese_word = row[0].strip() if row and len(row) > 0 else ""
            
            # Check for example sentences
            if len(row) > 3:
                example = row[3].strip()
                if example:
                    examples_found += 1
                    rows_with_examples.append({
                        "word": japanese_word,
                        "example": example[:50] + "..." if len(example) > 50 else example
                    })
            
        except Exception as e:
            print(f"{Fore.RED}Error parsing row {i+1}: {e}{Style.RESET_ALL}")
            print(f"Problematic row: {content_lines[i]}")
            
    print(f"\nFound {Fore.GREEN}{row_count}{Style.RESET_ALL} vocabulary entries")
    print(f"Found {Fore.GREEN}{examples_found}{Style.RESET_ALL} entries with example sentences")
    print(f"Example sentence coverage: {Fore.GREEN}{(examples_found / row_count * 100) if row_count else 0:.1f}%{Style.RESET_ALL}")
    
    # Show some example sentences
    if rows_with_examples:
        print(f"\n{Fore.CYAN}Sample example sentences:{Style.RESET_ALL}")
        for i, item in enumerate(rows_with_examples[:5]):  # Show up to 5 examples
            print(f"{i+1}. {Fore.YELLOW}{item['word']}{Style.RESET_ALL}: {item['example']}")
            
        # Check the format of example sentences
        print(f"\n{Fore.CYAN}Checking example sentence format:{Style.RESET_ALL}")
        jp_example_count = 0
        jp_en_example_count = 0
        
        for item in rows_with_examples:
            example = item['example']
            # Check if example has Japanese characters
            has_jp = any(ord(c) > 127 for c in example)
            # Check if example has format "Japanese (English)"
            has_jp_en_format = '(' in example and ')' in example
            
            if has_jp and has_jp_en_format:
                jp_en_example_count += 1
            elif has_jp:
                jp_example_count += 1
                
        print(f"Examples with Japanese text: {Fore.GREEN}{jp_example_count + jp_en_example_count}{Style.RESET_ALL}")
        print(f"Examples with Japanese (English) format: {Fore.GREEN}{jp_en_example_count}{Style.RESET_ALL}")
        
        if jp_en_example_count > 0:
            print(f"\n{Fore.GREEN}✓ Your CSV contains properly formatted example sentences.{Style.RESET_ALL}")
        elif jp_example_count > 0:
            print(f"\n{Fore.YELLOW}⚠ Your examples have Japanese text but may not have English translations in parentheses.{Style.RESET_ALL}")
            print(f"  Recommended format: \"Japanese sentence (English translation)\"")
        else:
            print(f"\n{Fore.RED}✗ No properly formatted Japanese example sentences found.{Style.RESET_ALL}")
            print(f"  Recommended format: \"Japanese sentence (English translation)\"")
                
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug CSV files for example sentences")
    parser.add_argument('file', help='Path to the CSV file to check')
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"{Fore.RED}Error: File '{args.file}' not found{Style.RESET_ALL}")
        sys.exit(1)
        
    if check_csv_format(args.file):
        print(f"\n{Fore.GREEN}CSV file processed successfully{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}Issues found with CSV file{Style.RESET_ALL}")
        sys.exit(1)
