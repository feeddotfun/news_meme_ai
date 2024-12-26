from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict

class MemeResponse(BaseModel):
    news: str
    meme: str
    ticker: str
    name: str
    image: str
    timestamp: str