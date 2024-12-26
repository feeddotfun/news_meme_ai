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

## License

[MIT License](LICENSE)