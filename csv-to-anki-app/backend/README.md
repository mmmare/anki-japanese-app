# CSV to Anki App Backend

This is the backend service for the CSV to Anki application, built using FastAPI. The backend is responsible for processing CSV files containing Japanese words and creating Anki decks from them.

## Features

- Upload CSV files containing Japanese words.
- Create and manage Anki decks.
- RESTful API for frontend interaction.

## Project Structure

- `app/`: Contains the main application code.
  - `__init__.py`: Initializes the app package.
  - `main.py`: Entry point of the FastAPI application.
  - `models.py`: Defines data models for Anki decks and cards.
  - `routers/`: Contains route definitions.
    - `__init__.py`: Initializes the routers package.
    - `deck_router.py`: Defines routes related to Anki decks.
  - `services/`: Contains business logic for deck creation and manipulation.
    - `__init__.py`: Initializes the services package.
    - `deck_service.py`: Handles CSV processing and deck management.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd csv-to-anki-app/backend
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To start the FastAPI application, run:
```
uvicorn app.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- `POST /upload`: Upload a CSV file to create an Anki deck.
- `GET /decks`: Retrieve a list of Anki decks.
- `GET /decks/{deck_id}`: Retrieve details of a specific Anki deck.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.