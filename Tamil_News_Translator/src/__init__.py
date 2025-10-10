__version__ = "1.0.0"
__author__ = "Tamil News Translator Project"
__description__ = "A comprehensive Python project for fetching, scraping, and translating news articles to Tamil"

from .main import TamilNewsTranslator
from .news_fetcher import GoogleNewsFetcher, NewsArticle
from .content_scraper import ContentScraper
from .translator import TamilTranslator
from .file_manager import FileManager
from .error_handler import ErrorHandler

__all__ = [
    "TamilNewsTranslator",
    "GoogleNewsFetcher", 
    "NewsArticle",
    "ContentScraper",
    "TamilTranslator", 
    "FileManager",
    "ErrorHandler"
]
