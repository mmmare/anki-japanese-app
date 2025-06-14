# Japanese Vocabulary CSV to Anki Deck Generator - Updates

## Fixed Issues
The CSV parsing problem has been resolved, particularly for CSV files with Anki format directives (`#separator:tab`) that contain commas within fields. The application can now correctly handle:

1. Standard comma-separated CSV files
2. Anki-format tab-separated files 
3. Files with commas within data fields
4. Mixed formats with special characters

## Key Improvements

### 1. Improved CSV Parsing Logic
- Added robust parsing for tab-separated files that contain commas within fields
- Implemented custom parser that correctly handles quoted fields in tab-separated data
- Added fallback mechanisms when standard CSV parsing fails

### 2. Better Error Handling
- Added detailed error messages with diagnostic information
- Created fallback mechanisms when primary parsing fails
- Implemented detailed logging of problematic CSV formats

### 3. Enhanced Testing and Debugging
- Added comprehensive test cases for various CSV formats
- Created debugging utility for CSV parsing issues
- Added sample files for different formats for testing purposes

### 4. Enrichment Service Improvements
- Enhanced the EnrichService to properly handle commas in generated data
- Added proper CSV escaping for generated fields
- Added support for generating both tab-separated and comma-separated formats

## Usage Recommendations
For best results with Japanese vocabulary containing special characters:

1. Use the Anki tab-separated format (`#separator:tab`) for best compatibility
2. For fields containing commas, ensure they are properly quoted with double quotes
3. When generating enriched data with example sentences, the system will now properly handle the commas in the generated content

## Testing
All formats have been tested and verified to work correctly. You can use the `debug_anki.py` script to troubleshoot any issues with your specific CSV files:

```bash
python debug_anki.py your_csv_file.csv
```

This will provide detailed information about the CSV parsing process and help identify any issues.

## Example Sentence Audio Feature

A new feature has been added to provide audio playback for example sentences in Core2000 format decks:

### Implementation Details
1. **New UI Controls**
   - Added a dedicated toggle for example audio (visible when Core2000 and example sentences are enabled)
   - Audio for example sentences can now be enabled/disabled independently

2. **Backend Changes**
   - Modified the Core2000 package creation to include example audio based on user preference
   - Added parameter passing throughout the application flow
   - Enhanced example sentence audio generation with error handling

3. **Testing**
   - Created a dedicated test script (`test_example_audio_flag.py`) to verify the feature
   - The test confirms that example audio is only included when specifically enabled

### How to Use
1. Upload your CSV file with Japanese vocabulary and example sentences
2. Enable the Core2000 format toggle
3. Enable the "Include example sentences" toggle
4. The "Include example audio" toggle will appear, allowing you to control whether example sentences have audio
5. When reviewing cards in Anki, example sentences will have their own audio controls when this feature is enabled

This feature enhances the learning experience by allowing users to hear both vocabulary words and complete sentences, improving pronunciation and listening comprehension.
