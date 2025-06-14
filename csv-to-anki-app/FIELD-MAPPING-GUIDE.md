# Field Mapping Guide

## About Field Mapping

Field mapping allows you to customize which columns in your CSV files correspond to which fields in your Anki cards. This is especially useful when:

- Your CSV file uses different column headers than the standard format
- You want to import CSV files from various sources with different formats
- You need to include additional fields like readings, example sentences, or tags

## Standard Field Mapping

By default, the CSV to Anki converter expects a CSV file with these columns:

1. **Japanese Word/Expression** - The Japanese vocabulary term
2. **English Translation** - The English meaning or definition
3. **Reading** (optional) - The reading/pronunciation in hiragana or katakana
4. **Example Sentence** (optional) - A sample sentence using the word
5. **Tags** (optional) - Tags for organizing your cards

## Using the Field Mapping Feature

After uploading your CSV file, you'll be taken to the Field Mapping page where you can:

1. **View Suggested Mappings** - The system will automatically try to detect appropriate field mappings based on your CSV headers and content.

2. **Customize Mappings** - Use the dropdown menus to select which CSV column should map to each Anki field.

3. **Preview Sample Data** - See how your data will appear based on the current mapping.

4. **Apply Custom Mapping** - Save your custom field mapping settings.

5. **Reset to Default** - Clear all mappings if needed.

## Required Fields

The following fields are required for proper deck creation:

- **Japanese Word/Expression** - Required to create a vocabulary card
- **English Translation** - Required for the definition/meaning

Other fields (reading, example sentence, tags) are optional but recommended for more comprehensive cards.

## CSV Format Tips

- Column headers can be in any language (English, Japanese, etc.)
- The system can recognize headers like:
  - Japanese field: "japanese", "word", "front", "kanji", "日本語", "vocabulary", "expression"
  - English field: "english", "meaning", "translation", "back", "definition", "英語"
  - Reading field: "reading", "pronunciation", "kana", "hiragana", "yomigana", "読み方"
  - Example field: "example", "sentence", "usage", "context", "例文", "example sentence"
  - Tags field: "tag", "tags", "category", "categories", "group"
  
- If your CSV doesn't have column headers, the system will label them as "Column 1", "Column 2", etc., and you can map them manually.

## Best Practices

1. **Consistent Headers** - Use consistent column headers across your CSV files for easier mapping.
2. **Check Sample Data** - Always review the sample data preview to ensure your mapping is correct.
3. **Required Fields** - Make sure to map at least the Japanese word and English translation fields.
4. **Save Your Mapping** - Once you've created a good mapping, it will be saved in your browser for future use with similar CSV files.

## Troubleshooting

If you encounter issues with field mapping:

- Ensure your CSV file is properly formatted with consistent delimiters (commas or tabs)
- Check that required fields are properly mapped
- Verify that the encoding of your CSV file is UTF-8 to support Japanese characters
- Try resetting to the suggested mapping if your custom mapping isn't working
- If all else fails, simplify your CSV to include just the required columns (Japanese and English)

## Example

**CSV with custom headers:**

```
Term,Definition,Pronunciation,SampleUsage,Categories
猫,cat,ねこ,私は猫が好きです。,noun_animal
車,car,くるま,新しい車を買いました。,noun_object
```

**Mapping setup:**
- Japanese Word → "Term"
- English Meaning → "Definition"
- Reading → "Pronunciation"
- Example Sentence → "SampleUsage"
- Tags → "Categories"

This mapping will correctly associate each column with the appropriate Anki card field.