from typing import List, Dict
import httpx
from app.config.settings import settings

class NewsService:
    def __init__(self):
        self.base_url = settings.NEWS_BASE_URL
        self.api_key = settings.NEWS_API_KEY

    # API prepare params
    def _get_params(self) -> dict:
        return {
            "auth_token": self.api_key,
            "public": "true",
            # "filter": "hot",
            # "currencies": "BTC,ETH,USDT,BNB,SOL"
            "region": "en"
        }
    
    # Check if news is valid
    def _is_valid_news(self, title: str, existing_titles: List[str]) -> bool:
        if not title or len(title) < 15:
            return False
            
        if title.lower() in [t.lower() for t in existing_titles]:
            return False
            
        spam_words = ['sponsored', 'partner', 'press release', 'promoted']
        if any(spam in title.lower() for spam in spam_words):
            return False
            
        return True
    
    # Fetch news from API
    async def fetch_news(self) -> List[Dict[str, str]]:
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(
                    self.base_url,
                    params=self._get_params()
                )
                response.raise_for_status()
                data = response.json()

                news_list = []
                seen_titles = []

                for item in data['results'][:10]:  # First 10 items
                    title = item.get('title', '').strip()
                    
                    if self._is_valid_news(title, seen_titles):
                        news_list.append({
                            "title": title,
                            "source": item.get('source', {}).get('title', 'unknown')
                        })
                        seen_titles.append(title)

                        if len(news_list) >= 5:  # 5 news items
                            break

                return news_list if news_list else self._get_backup_news()

        except Exception as e:
            print(f"News fetch error: {str(e)}")