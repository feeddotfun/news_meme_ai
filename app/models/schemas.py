from pydantic import BaseModel
from typing import Optional, Dict

class NewsResponse(BaseModel):
    title: str
    source: Optional[Dict] = None
    published_at: Optional[str] = None

class MemeResponse(BaseModel):
    news: str
    meme: str
    ticker: str
    name: str
    timestamp: str