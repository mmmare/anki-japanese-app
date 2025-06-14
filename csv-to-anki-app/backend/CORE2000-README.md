# Core2000 Format for Anki Japanese Learning

This README explains the Core2000 format for learning Japanese vocabulary with Anki flashcards and how to use the provided tools to create Core2000-styled decks.

## What is Core2000?

Core2000 is a popular format for Japanese vocabulary learning that:

1. Contains the ~2000 most common Japanese words
2. Uses a specific formatting style optimized for Japanese learning
3. Features both Recognition (Japanese → English) and Production (English → Japanese) card types
4. Has a consistent style with clear Japanese fonts, color coding, and formatting

## Core2000 Format Features

The Core2000 format provided in this tool has the following features:

### Field Structure

- **Japanese**: The Japanese word/expression written in kanji (when applicable)
- **Reading**: The reading in hiragana/katakana
- **English**: The English translation/meaning
- **Example**: Example sentence in Japanese (with English translation)
- **Audio**: Audio pronunciation of the Japanese word
- **ExampleAudio**: Audio pronunciation of the example sentence

### Card Types

1. **Recognition Cards (Japanese → English)**
   - Front: Japanese word with optional audio
   - Back: Reading, English meaning, and example sentence

2. **Production Cards (English → Japanese)**
   - Front: English meaning
   - Back: Japanese word, reading, audio pronunciation, and example sentence

### Styling

- Large, clear Japanese text for the main vocabulary
- Blue-colored readings to distinguish them from the main word
- Green-colored English translations
- Example sentences with left border styling
- Properly sized fonts for different information types

## Creating Core2000 Style Anki Decks

### Method 1: Command Line Tool

Use the `create_core2000_deck.py` script to generate a Core2000 format deck:

```bash
cd /path/to/anki-generator/csv-to-anki-app/backend
python create_core2000_deck.py path/to/your/vocabulary.csv
```

Optional arguments:
- `-o, --output`: Specify the output .apkg file path
- `-n, --name`: Specify a custom name for the deck

### Method 2: Sample Data

Try the included sample data:

```bash
cd /path/to/anki-generator/csv-to-anki-app/backend
python create_core2000_deck.py data/core2000_sample.csv
```

## CSV Format for Core2000

Your CSV file should have the following format:

```
#separator:tab
#html:true
Japanese    English    Reading    Example    Tags
猫          cat        ねこ        猫が可愛い... animal noun
...
```

Fields:
1. **Japanese**: The Japanese vocabulary term (required)
2. **English**: The English meaning (required)
3. **Reading**: Hiragana/katakana reading (recommended)
4. **Example**: Example sentence (optional)
5. **Tags**: Tags for organization (optional)

For non-tab separated formats, a regular CSV with the same columns is also supported:

```csv
Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が可愛い...,animal noun
...
```

## Integrating with the Web Application

The Core2000 format is now fully integrated into the web application. To use it:

1. Upload your CSV file with Japanese vocabulary data
2. Navigate to the deck creation options
3. Toggle on the "Use Core 2000 format (Recognition + Production cards)" switch
4. Optional: Enable additional enrichments like translations and audio
5. Click "Generate Anki Deck" to create your Core2000 style deck

When the Core2000 format is enabled, each vocabulary entry will generate both Recognition (JP→EN) and Production (EN→JP) cards with the special Core2000 styling.

### Example Sentence Audio

The Core2000 format includes support for example sentence audio in addition to vocabulary word audio:

- When example sentences are enabled, you can also enable example audio
- Example audio is generated for the Japanese part of each example sentence
- Audio controls will appear next to example sentences in your Anki cards
- Example audio can be toggled on/off independently from vocabulary audio

## Tips for Effective Learning

1. **Start with Recognition**: Begin with the Japanese → English cards until you're comfortable with recognizing the vocabulary
2. **Progress to Production**: Once familiar, switch to the English → Japanese cards to practice recall
3. **Use Audio**: The audio feature helps with pronunciation - listen before answering
4. **Listen to Example Sentences**: Each example sentence has its own audio - listen to hear natural usage
5. **Review Example Sentences**: The example sentences provide context for how words are used

## Customizing the Core2000 Format

If you want to customize the Core2000 format, you can modify:

- `/app/services/anki_utils.py`: The `create_core2000_package_from_csv()` function contains the template definitions
- `/backend/core2000_format.py`: Contains standalone functions for creating Core2000 style decks

## Troubleshooting

If you encounter any issues:

1. Make sure your CSV file has the correct format
2. Check that the Japanese text is properly encoded in UTF-8
3. For audio issues, ensure that the audio generation service is properly configured
4. If card formatting looks incorrect in Anki, check for HTML syntax errors in your CSV file
