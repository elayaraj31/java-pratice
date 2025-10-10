
import time
from typing import Dict, List, Optional
from datetime import datetime

import feedparser
from googlenewsdecoder import gnewsdecoder

from config import GOOGLE_NEWS_URLS, RATE_LIMIT_CONFIG, PROCESSING_LIMITS
from error_handler import ErrorHandler, NetworkErrorHandler, handle_exceptions, rate_limit


class NewsArticle:
    """Data class for news articles"""
    
    def __init__(self, title: str, link: str, published: str, description: str, source: str = ""):
        self.title = title
        self.link = link
        self.published = published
        self.description = description
        self.source = source
        self.original_url = None
        self.full_content = None
        self.translated_title = None
        self.translated_content = None
        
    def to_dict(self) -> Dict:
        """Convert article to dictionary"""
        return {
            "title": self.title,
            "link": self.link,
            "original_url": self.original_url,
            "published": self.published,
            "description": self.description,
            "source": self.source,
            "full_content": self.full_content,
            "translated_title": self.translated_title,
            "translated_content": self.translated_content,
            "processed_at": datetime.now().isoformat()
        }


class GoogleNewsFetcher:
    """Fetches news articles from Google News RSS feeds"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.network_handler = NetworkErrorHandler(self.error_handler)
        self.session = self.network_handler.create_session_with_retries()
        
    @handle_exceptions("fetch_rss_feed")
    @rate_limit(calls_per_minute=RATE_LIMIT_CONFIG["requests_per_minute"])
    def fetch_rss_feed(self, rss_url: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse RSS feed from Google News"""
        try:
            self.error_handler.log_info(f"Fetching RSS feed: {rss_url}", "fetch_rss_feed")
            
            # Use feedparser to get the RSS feed
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                self.error_handler.log_warning(f"RSS feed has parsing issues: {feed.bozo_exception}", "fetch_rss_feed")
            
            if not feed.entries:
                self.error_handler.log_warning("No entries found in RSS feed", "fetch_rss_feed")
                return None
                
            self.error_handler.log_info(f"Successfully fetched {len(feed.entries)} articles", "fetch_rss_feed")
            time.sleep(RATE_LIMIT_CONFIG["google_news_delay"])
            
            return feed
            
        except Exception as e:
            self.error_handler.log_error(e, "fetch_rss_feed")
            return None
    
    @handle_exceptions("decode_google_news_url")
    def decode_google_news_url(self, google_url: str) -> Optional[str]:
        """Decode Google News URL to get original article URL"""
        try:
            self.error_handler.log_info(f"Decoding Google News URL", "decode_google_news_url")
            
            # Use googlenewsdecoder to get the original URL
            decoded_result = gnewsdecoder(google_url, interval=1)
            
            if decoded_result.get("status"):
                original_url = decoded_result["decoded_url"]
                self.error_handler.log_info(f"Successfully decoded URL", "decode_google_news_url")
                return original_url
            else:
                self.error_handler.log_warning(f"Failed to decode URL: {decoded_result.get('message', 'Unknown error')}", "decode_google_news_url")
                return None
                
        except Exception as e:
            self.error_handler.log_error(e, f"decode_google_news_url: {google_url}")
            return None
    
    @handle_exceptions("parse_rss_entries")
    def parse_rss_entries(self, feed: feedparser.FeedParserDict) -> List[NewsArticle]:
        """Parse RSS feed entries into NewsArticle objects"""
        articles = []
        
        try:
            for entry in feed.entries[:PROCESSING_LIMITS["max_articles_per_run"]]:
                # Extract basic information
                title = entry.get('title', 'No title')
                link = entry.get('link', '')
                published = entry.get('published', '')
                description = entry.get('description', entry.get('summary', ''))
                
                # Extract source from title (Google News format: "Title - Source")
                source = ""
                if " - " in title:
                    title_parts = title.split(" - ")
                    if len(title_parts) > 1:
                        title = " - ".join(title_parts[:-1])
                        source = title_parts[-1]
                
                # Create NewsArticle object
                article = NewsArticle(
                    title=title,
                    link=link,
                    published=published,
                    description=description,
                    source=source
                )
                
                # Decode Google News URL to get original URL
                if link:
                    original_url = self.decode_google_news_url(link)
                    article.original_url = original_url or link
                
                articles.append(article)
                
            self.error_handler.log_info(f"Parsed {len(articles)} articles", "parse_rss_entries")
            
        except Exception as e:
            self.error_handler.log_error(e, "parse_rss_entries")
        
        return articles
    
    @handle_exceptions("fetch_news_by_category")
    def fetch_news_by_category(self, category: str = "top_stories") -> List[NewsArticle]:
        """Fetch news articles by category"""
        try:
            if category not in GOOGLE_NEWS_URLS:
                self.error_handler.log_warning(f"Unknown category: {category}", "fetch_news_by_category")
                category = "top_stories"
            
            rss_url = GOOGLE_NEWS_URLS[category]
            self.error_handler.log_info(f"Fetching news for category: {category}", "fetch_news_by_category")
            
            # Fetch RSS feed
            feed = self.fetch_rss_feed(rss_url)
            if not feed:
                return []
            
            # Parse entries
            articles = self.parse_rss_entries(feed)
            
            self.error_handler.log_info(f"Successfully fetched {len(articles)} articles for category: {category}", "fetch_news_by_category")
            
            return articles
            
        except Exception as e:
            self.error_handler.log_error(e, f"fetch_news_by_category: {category}")
            return []
    
    @handle_exceptions("fetch_news_by_query")
    def fetch_news_by_query(self, query: str) -> List[NewsArticle]:
        """Fetch news articles by search query"""
        try:
            # Construct search URL
            search_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            self.error_handler.log_info(f"Searching news for query: {query}", "fetch_news_by_query")
            
            # Fetch RSS feed
            feed = self.fetch_rss_feed(search_url)
            if not feed:
                return []
            
            # Parse entries
            articles = self.parse_rss_entries(feed)
            
            self.error_handler.log_info(f"Successfully found {len(articles)} articles for query: {query}", "fetch_news_by_query")
            
            return articles
            
        except Exception as e:
            self.error_handler.log_error(e, f"fetch_news_by_query: {query}")
            return []
    
    def get_available_categories(self) -> List[str]:
        """Get list of available news categories"""
        return list(GOOGLE_NEWS_URLS.keys())
