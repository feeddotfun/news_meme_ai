from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..services.news_service import NewsService
from ..services.news_to_ai_service import NewsToAIService
from ..models.schemas import MemeResponse

router = APIRouter()
news_service = NewsService()
news_to_ai_service = NewsToAIService()

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy"}

# News endpoints
@router.get("/news", response_model=List[dict])
async def get_news():
    """
    Fetch latest news from the news service
    """
    try:
        news = await news_service.fetch_news()
        if not news:
            raise HTTPException(status_code=404, detail="No news found")
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Meme generation endpoints
@router.get('/memes', response_model=List[MemeResponse])
async def generate_memes():
    """
    Generate memes from latest news
    """
    try:
        news_list = await news_service.fetch_news()
        if not news_list:
            raise HTTPException(status_code=404, detail="No news available for meme generation")
            
        titles = [news['title'] for news in news_list]
        memes = await news_to_ai_service.process_news_batch(titles)
        
        if not memes:
            raise HTTPException(status_code=500, detail="Failed to generate memes")
            
        return memes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Version endpoint for deployment tracking
@router.get("/version")
async def get_version():
    return {"version": "1.0.0"}