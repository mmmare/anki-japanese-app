# Field Mapping Feature for Japanese Vocabulary Anki Deck Generator

## Overview
The field mapping feature allows users to upload CSV files with custom column names and map them to the appropriate Anki card fields. This enhances the flexibility of the application, enabling users to use their own CSV formats without having to rename columns.

## Key Features

1. **Automatic Field Detection**:
   - Analyzes CSV content to detect which columns contain Japanese words, English definitions, etc.
   - Uses both header names and content analysis to make intelligent mapping suggestions

2. **Custom Mapping Configuration**:
   - Users can define custom mappings between CSV columns and Anki fields
   - Mapping can be adjusted through a user-friendly interface

3. **Support for Various CSV Formats**:
   - Works with standard CSV files with any column headers
   - Supports tab-separated files and Anki export formats
   - Handles files with or without headers

## Using the Field Mapping Feature

### Backend API Endpoints

- **`POST /api/mapping/analyze`**: Analyze a CSV file and suggest field mappings
  - Input: CSV file upload
  - Output: Headers, sample data, and suggested field mappings

- **`POST /api/mapping/apply`**: Apply a custom field mapping to a session
  - Input: Session ID and JSON mapping object
  - Output: Confirmation message

### Frontend Component

The `FieldMapper` component provides a user interface for:
- Visualizing and editing field mappings
- Displaying sample data from the CSV file
- Previewing how mapped data will appear in Anki cards

### Sample Mapping Object

```json
{
  "japanese": "Term",          // Maps CSV "Term" column to Japanese field
  "english": "Definition",     // Maps CSV "Definition" column to English field
  "reading": "Pronunciation",  // Maps CSV "Pronunciation" column to Reading field
  "example": "Usage",          // Maps CSV "Usage" column to Example field
  "tags": "Category"           // Maps CSV "Category" column to Tags field
}
```

## Testing

Two test scripts demonstrate the field mapping functionality:

1. **`test_field_mapping.py`**: Tests the full API workflow for field mapping
   - Uploads a CSV with custom column names
   - Analyzes the CSV for field mapping suggestions
   - Applies a custom mapping
   - Creates an Anki deck with the custom mapping
   - Downloads the resulting deck

2. **`test_direct_mapping.py`**: Tests the direct mapping functionality
   - Creates an Anki package with field mapping without using the API
   - Demonstrates direct usage of the `create_anki_package_with_mapping` function

## Field Detection Logic

The system detects appropriate fields using:
1. Header name matching against common field names
2. Content analysis (Japanese character detection, kana detection)
3. Positional fallbacks for standard CSV layouts

## Usage Example

1. Upload a CSV file with custom column names
2. System analyzes the file and suggests field mappings
3. User reviews and adjusts mappings if needed
4. Apply the mapping to create an Anki deck with properly mapped fields

## Benefits

- Flexibility to use various CSV formats
- No need to modify source CSV files to match specific formats
- Intelligent suggestions reduce manual mapping effort
- Compatible with existing enrichment and audio features
