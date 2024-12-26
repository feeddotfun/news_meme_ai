from setuptools import setup, find_packages

setup(
    name="news-meme-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "httpx",
        "pytest",
        "pytest-asyncio",
    ],
)