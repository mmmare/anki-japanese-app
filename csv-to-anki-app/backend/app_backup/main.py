from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import deck_router  # Remove the dot to fix import

app = FastAPI(title="CSV to Anki API")

# Configure CORS
origins = [
    "http://localhost:3000",  # React frontend
    "http://localhost:8080",  # Alternative frontend port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(deck_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to CSV to Anki Converter API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}