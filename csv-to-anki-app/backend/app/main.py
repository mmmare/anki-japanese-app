from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# Use relative imports instead of absolute
from .routers import deck_router, enrich_router, mapping_router

app = FastAPI(title="CSV to Anki API")

# Configure CORS
origins = [
    "http://localhost:3000",  # React frontend
    "http://localhost:8080",  # Alternative frontend port
    "http://127.0.0.1:3000",  # React frontend with IP
    "http://127.0.0.1:8080",  # Alternative frontend with IP
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
app.include_router(enrich_router.router)
app.include_router(mapping_router.router)

@app.get("/")
def root():
    return {"message": "Hello from CSV to Anki Converter"}

@app.get("/health")
def health():
    return {"status": "ok"}
