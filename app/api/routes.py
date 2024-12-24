from fastapi import APIRouter
from ..services.news_service import NewsService

router = APIRouter()
news_fetcher = NewsService()

@router.get("/news")
async def get_news():
    return await news_fetcher.fetch_news()