# <div align="center"><img src="assets/logo.svg" width="200" height="200" alt="feed.fun"></div>

# Feed.fun AI API

Feed.fun is an innovative platform that revolutionizes meme coin creation by combining community-driven content with AI-powered news integration.

## Features

- Real-time news monitoring
- AI-powered meme generation

## Development

### Prerequisites

- Python 3.9 or higher
- Poetry for dependency management

### Setup

1. Clone the repository
```bash
git clone https://github.com/feeddotfun/news_meme_ai.git
cd news_meme_ai
```

2. Install dependencies
```bash
poetry install
```

3. Run tests
```bash
poetry run pytest
```

## API Documentation

### Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/version` - API version
- `GET /api/v1/news` - Get latest crypto news
- `GET /api/v1/memes` - Generate memes from news
- `GET /api/v1/meme?news={news}` - Generate meme from specific news

### Sample Response

Here's an example of what you get when calling `/api/v1/memes`:

```json
[
  {
    "news": "Bitget announces token merger, BGB price increases amid market-wide declines",
    "meme": "MergeMaster (FUSE) sparking synergy in a fragmented world ⚡🕸️💻 🚀",
    "ticker": "FUSE",
    "name": "MergeMaster",
    "image": "https://i.ibb.co/XLG70hn/6af7541403a7.jpg",
    "timestamp": "2024-12-26 14:21:23"
  },
  {
    "news": "Vitalik Buterin Makes Big Crypto Donation As 'Adoptive Father'",
    "meme": "VitaPapa (DADO) spreading love coins like a paternal blockchain wizard ⚡📈❤️😊",
    "ticker": "DADO",
    "name": "VitaPapa",
    "image": "https://i.ibb.co/SV4PLm9/a2240f09c109.jpg",
    "timestamp": "2024-12-26 14:21:48"
  }
]
```

Each meme response includes:
- Original news article
- Generated meme name and ticker
- Creative catchphrase with emojis
- AI-generated meme image
- Timestamp of generation

### Response Format

```typescript
interface MemeResponse {
  news: string;        // Original news article
  meme: string;        // Generated catchphrase
  ticker: string;      // 3-6 character ticker symbol
  name: string;        // Generated meme coin name
  image: string;       // URL to generated meme image
  timestamp: string;   // ISO format timestamp
}
```
