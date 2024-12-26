from fastapi import APIRouter

from ..services.news_service import NewsService
from ..services.news_to_ai_service import NewsToAIService
router = APIRouter()
news_fetcher = NewsService()
news_to_ai = NewsToAIService()



@router.get("/news")
async def get_news():
    return await news_fetcher.fetch_news()


@router.get('/ai')
async def generate_meme_from_ai():
    news_list = await news_fetcher.fetch_news()
    titles = [news['title'] for news in news_list]
    memes = await news_to_ai.process_news_batch(titles)
    return memes