# Japanese Vocabulary Anki Deck Generator

A modern web application for creating enriched Anki flashcard decks from Japanese vocabulary. Features a responsive React frontend with Chakra UI and a powerful FastAPI backend with automatic enrichment capabilities.

🚀 **Now with automated CI/CD deployment!** Every code update is automatically tested and deployed.

## Features

- **CSV to Anki Conversion**: Easily upload CSV files with Japanese vocabulary and convert them to Anki decks
- **Multiple CSV Formats**: Supports both standard CSV and Anki-compatible tab-separated formats
- **Anki Standard Compatibility**: Creates .apkg files that can be directly imported into Anki
- **Tag Support**: Supports adding tags to your flashcards (use underscores instead of spaces in tags)

### NEW! Japanese Vocabulary Enrichment
- **Automatic Translations**: Find English meanings for Japanese words
- **Readings & Romaji**: Get hiragana/katakana readings and romaji transliterations
- **Audio Pronunciation**: Japanese text-to-speech included in flashcards
- **Example Sentences**: Sample sentences showing word usage in context
- **Part of Speech Tagging**: Automatically tag words as nouns, verbs, etc.

- **Modern UI**: Clean and responsive interface built with Chakra UI
- **Session Management**: Maintains your session data between uploads and downloads
- **Progress Indicators**: Visual feedback during deck creation and download

![Japanese Anki Deck Generator](https://img.shields.io/badge/Japanese-Anki_Deck_Generator-brightgreen)
![React](https://img.shields.io/badge/frontend-React-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![Chakra UI](https://img.shields.io/badge/UI-Chakra-teal)

## Project Structure

```
csv-to-anki-app
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routers
│   │   │   ├── __init__.py
│   │   │   ├── deck_router.py
│   │   │   └── enrich_router.py  # Handles Japanese vocabulary enrichment
│   │   └── services
│   │       ├── __init__.py
│   │       ├── deck_service.py
│   │       └── enrich_service.py  # Japanese translations, audio, examples
│   ├── requirements.txt
│   ├── test_enrichment.py  # Test script for enrichment features
│   └── README.md
├── frontend
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   ├── components
│   │   │   ├── CsvUpload.tsx
│   │   │   ├── AnkiControls.tsx
│   │   │   └── JapaneseWordLookup.tsx  # Interactive word lookup component
│   │   ├── context
│   │   │   └── SessionContext.tsx
│   │   ├── services
│   │   │   └── api.ts
│   │   └── types
│   │       └── index.ts
│   ├── package.json
│   └── tsconfig.json
│   └── README.md
└── README.md
```

## Backend

The backend is built using FastAPI and provides the following functionalities:

- **API Endpoints**: 
  - Upload CSV files containing Japanese words.
  - Create and manage Anki decks.
  
- **Services**: 
  - Handles the business logic for processing CSV files and creating Anki decks.

- **Models**: 
  - Defines the data structures used in the application.

### Setup Instructions

#### Option 1: Using the run script (recommended)

The easiest way to run both backend and frontend is with the provided run script:

```bash
./run.sh
```

This script will:
- Create a Python virtual environment if needed
- Install all required dependencies
- Start the FastAPI backend on port 8000
- Start the React frontend on port 3000

## CSV File Formats

The application now supports two CSV formats:

### Standard CSV Format

```csv
Japanese,English,Tags
こんにちは,Hello,greeting
ありがとう,Thank you,greeting
さようなら,Goodbye,greeting
```

### Anki-compatible Format (Tab-separated)

```
#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front	Back	Tags
こんにちは	Hello	greeting
ありがとう	Thank you	greeting
さようなら	Goodbye	greeting
```

**Important Notes:**
- For standard CSV, the header is optional but recommended
- The Tags column is optional in both formats
- Tags should not contain spaces - use underscores instead (e.g., `noun_animal`)
- Multiple tags should be separate words (e.g., "noun animal")
- The Anki-compatible format can be imported directly into Anki if needed

#### Option 2: Manual setup

**Backend:**
1. Navigate to the `backend` directory
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

**Frontend:**
1. Navigate to the `frontend` directory
2. Install the required dependencies:
   ```bash
   npm install
   ```
3. Start the React application:
   ```bash
   npm start
   ```

## Usage

1. Open the frontend application in your web browser (http://localhost:3000).
2. Upload a CSV file containing Japanese vocabulary:
   - You can drag and drop a file or click to browse
   - Use the "Try with sample data" button to test the application with provided sample data
   - Your CSV can be either standard CSV or Anki tab-separated format
3. Click "Upload and Create Anki Deck" to process the file
4. On the deck controls page:
   - Click "Generate Anki Deck" to create your deck
   - Once the deck is created, click "Download Deck" to get the deck file
5. Import the downloaded file into Anki:
   - Open Anki on your computer
   - Click File → Import
   - Select the downloaded file
   - Your Japanese vocabulary deck is ready to use!

### Example CSV Formats

#### Standard CSV:
```csv
Japanese,English,Tags
こんにちは,Hello,greeting
ありがとう,Thank you,greeting
水,Water,noun
猫,Cat,noun_animal
```

#### Anki Format:
```
#separator:tab
#html:true
#deck:Japanese Vocabulary Deck
#columns:Front	Back	Tags
こんにちは	Hello	greeting
ありがとう	Thank you	greeting
水	Water	noun
猫	Cat	noun_animal
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.
