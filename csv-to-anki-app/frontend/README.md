# CSV to Anki App - Frontend

This is the frontend part of the CSV to Anki application, built using React. The application allows users to upload a CSV file containing Japanese words and create Anki decks from that data.

## Getting Started

To get started with the frontend application, follow these steps:

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd csv-to-anki-app/frontend
   ```

2. **Install dependencies**:
   Make sure you have Node.js installed. Then run:
   ```
   npm install
   ```

3. **Run the application**:
   Start the development server with:
   ```
   npm start
   ```
   This will open the application in your default web browser at `http://localhost:3000`.

## Features

- Upload CSV files containing Japanese words.
- Create Anki decks based on the uploaded data.
- User-friendly interface for managing decks.

## Components

- **CsvUpload**: A component for uploading CSV files.
- **AnkiControls**: A component for controlling the Anki deck creation process.

## API Integration

The frontend communicates with the backend FastAPI application to handle CSV uploads and Anki deck creation. Ensure the backend is running before using the frontend.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.