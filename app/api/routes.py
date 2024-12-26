from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..services.news_service import NewsService
from ..services.news_to_ai_service import NewsToAIService
from ..models.schemas import MemeResponse

router = APIRouter()
news_service = NewsService()
news_to_ai_service = NewsToAIService()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/news", response_model=List[dict])
async def get_news():
    """Fetch latest news from the news service"""
    news = await news_service.fetch_news()
    if not news:
        raise HTTPException(status_code=404, detail="No news found")
    return news

@router.get('/memes', response_model=List[MemeResponse])
async def generate_memes():
    """Generate memes from latest news"""
    news_list = await news_service.fetch_news()
    if not news_list:
        raise HTTPException(status_code=404, detail="No news available for meme generation")
        
    try:
        memes = await news_to_ai_service.process_news_batch(
            [news['title'] for news in news_list]
        )
        if not memes:
            raise HTTPException(status_code=404, detail="No memes generated")
        return memes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/meme', response_model=MemeResponse)
async def generate_meme(news: str):
    """Generate meme from news"""
    if not news:
        raise HTTPException(status_code=400, detail="News content is required")
    
    try:
        meme = await news_to_ai_service.generate_meme(news)
        if not meme:
            raise HTTPException(status_code=404, detail="Failed to generate meme")
        return meme
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/version")
async def get_version():
    return {"version": "1.0.0"}