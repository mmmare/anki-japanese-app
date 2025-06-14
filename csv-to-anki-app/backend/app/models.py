from pydantic import BaseModel
from typing import List, Optional

class AnkiCard(BaseModel):
    front: str
    back: str
    reading: Optional[str] = ""
    example: Optional[str] = ""
    audio: Optional[str] = ""
    tags: List[str] = []
    
class AnkiDeck(BaseModel):
    name: str
    cards: List[AnkiCard] = []
    description: Optional[str] = None
    is_enriched: bool = False

class CsvUploadResponse(BaseModel):
    filename: str
    row_count: int
    message: str