# Example Sentence Troubleshooting Guide

If you're having trouble with example sentences not appearing in your Anki deck, this guide will help you troubleshoot the issues.

## CSV Format Requirements

For example sentences to work properly:

1. Your CSV file should have at least 4 columns:
   - Column 1: Japanese word
   - Column 2: English meaning
   - Column 3: Reading (optional)
   - Column 4: Example sentence
   - Column 5: Tags (optional)

2. Example sentences should be in the format:
   - `Japanese sentence (English translation)`
   - Example: `これは本です。(This is a book.)`

## Diagnosing Issues

### Use the Debug Tool

We've included a debugging tool that can help identify issues with your CSV file:

```bash
cd /Users/michaelmarre/Dev/python/anki-generator/csv-to-anki-app/backend
python debug_csv_examples.py path/to/your/file.csv
```

This tool will:
- Verify your CSV format
- Check if example sentences are present
- Validate the example sentence format
- Provide recommendations for fixing issues

### Common Issues and Solutions

1. **No examples appearing at all:**
   - Make sure you've enabled "Include example sentences" in the UI
   - Ensure your CSV has at least 4 columns (Japanese, English, Reading, Example)
   - Check that the examples are in column 4

2. **Examples appearing without audio:**
   - For Core2000 format, make sure "Include example audio" is toggled on
   - Ensure your examples contain Japanese text (not just English)

3. **Some examples missing:**
   - If your CSV doesn't have examples for every word, the system will try to generate them
   - Some words might not have examples available in the dictionary API

4. **Wrong examples showing:**
   - Make sure your CSV's first column exactly matches the word in the example
   - Check that there are no extra spaces or characters in your Japanese words

## CSV Example

Here's a properly formatted CSV example:

```
Japanese,English,Reading,Example,Tags
猫,cat,ねこ,私は猫が好きです。(I like cats.),animal
犬,dog,いぬ,彼は犬を散歩させています。(He is walking the dog.),animal
本,book,ほん,この本は面白いです。(This book is interesting.),object
```

## Additional Tips

- If you're using Anki format with tab separators:
  ```
  #separator:tab
  Japanese	English	Reading	Example	Tags
  ```

- Double-check character encoding (should be UTF-8)

- For best results, include both Japanese and English in the example field

If you continue to have issues, please run the debug tool and share the results with our support team.
