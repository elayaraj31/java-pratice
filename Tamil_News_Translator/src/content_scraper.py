
import time
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from newspaper import Article
try:
    from readability import Document
except ImportError:
    Document = None

from config import SCRAPING_CONFIG, RATE_LIMIT_CONFIG, PROCESSING_LIMITS
from error_handler import ErrorHandler, NetworkErrorHandler, handle_exceptions, rate_limit
from news_fetcher import NewsArticle


class ContentScraper:
    """Scrapes full content from news article URLs"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.network_handler = NetworkErrorHandler(self.error_handler)
        self.session = self.network_handler.create_session_with_retries()
        
    @handle_exceptions("scrape_with_newspaper3k")
    @rate_limit(calls_per_minute=RATE_LIMIT_CONFIG["requests_per_minute"])
    def scrape_with_newspaper3k(self, url: str) -> Optional[dict]:
        """Scrape article content using newspaper3k library"""
        try:
            self.error_handler.log_info(f"Scraping with newspaper3k: {url}", "scrape_with_newspaper3k")
            
            # Create Article object
            article = Article(url)
            
            # Download and parse the article
            article.download()
            article.parse()
            
            # Extract content
            content = {
                "title": article.title,
                "text": article.text,
                "authors": article.authors,
                "publish_date": article.publish_date,
                "top_image": article.top_image,
                "summary": "",
                "keywords": []
            }
            
            # Try to get NLP features (optional)
            try:
                article.nlp()
                content["summary"] = article.summary
                content["keywords"] = article.keywords
            except Exception as e:
                self.error_handler.log_warning(f"NLP processing failed: {e}", "scrape_with_newspaper3k")
            
            if content["text"] and len(content["text"]) > PROCESSING_LIMITS["min_article_length"]:
                self.error_handler.log_info("Successfully scraped with newspaper3k", "scrape_with_newspaper3k")
                return content
            else:
                self.error_handler.log_warning("Article text too short or empty", "scrape_with_newspaper3k")
                return None
                
        except Exception as e:
            self.error_handler.log_error(e, f"scrape_with_newspaper3k: {url}")
            return None
    
    @handle_exceptions("scrape_with_beautifulsoup")
    @rate_limit(calls_per_minute=RATE_LIMIT_CONFIG["requests_per_minute"])
    def scrape_with_beautifulsoup(self, url: str) -> Optional[dict]:
        """Scrape article content using BeautifulSoup with fallback strategies"""
        try:
            self.error_handler.log_info(f"Scraping with BeautifulSoup: {url}", "scrape_with_beautifulsoup")
            
            # Make request
            response = self.network_handler.make_request(url, self.session)
            if not response:
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content using multiple strategies
            content_text = self._extract_content_text(soup)
            
            if not content_text or len(content_text) < PROCESSING_LIMITS["min_article_length"]:
                self.error_handler.log_warning("Could not extract sufficient content", "scrape_with_beautifulsoup")
                return None
            
            content = {
                "title": title,
                "text": content_text,
                "authors": [],
                "publish_date": None,
                "top_image": self._extract_top_image(soup, url),
                "summary": "",
                "keywords": []
            }
            
            self.error_handler.log_info("Successfully scraped with BeautifulSoup", "scrape_with_beautifulsoup")
            return content
            
        except Exception as e:
            self.error_handler.log_error(e, f"scrape_with_beautifulsoup: {url}")
            return None
    
    @handle_exceptions("scrape_with_readability")
    def scrape_with_readability(self, url: str) -> Optional[dict]:
        """Scrape article content using readability library"""
        if Document is None:
            return None
            
        try:
            self.error_handler.log_info(f"Scraping with readability: {url}", "scrape_with_readability")
            
            # Make request
            response = self.network_handler.make_request(url, self.session)
            if not response:
                return None
            
            # Use readability to extract main content
            doc = Document(response.text)
            
            # Extract content
            title = doc.title()
            content_html = doc.summary()
            
            # Parse the content HTML to get clean text
            content_soup = BeautifulSoup(content_html, 'lxml')
            content_text = content_soup.get_text(strip=True, separator=' ')
            
            if not content_text or len(content_text) < PROCESSING_LIMITS["min_article_length"]:
                self.error_handler.log_warning("Could not extract sufficient content", "scrape_with_readability")
                return None
            
            content = {
                "title": title,
                "text": content_text,
                "authors": [],
                "publish_date": None,
                "top_image": "",
                "summary": "",
                "keywords": []
            }
            
            self.error_handler.log_info("Successfully scraped with readability", "scrape_with_readability")
            return content
            
        except Exception as e:
            self.error_handler.log_error(e, f"scrape_with_readability: {url}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title using multiple strategies"""
        # Try different title selectors
        title_selectors = [
            'h1',
            '.article-title',
            '.post-title',
            '.entry-title',
            '.headline',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 10:
                    return title
        
        return "No title found"
    
    def _extract_content_text(self, soup: BeautifulSoup) -> str:
        """Extract main content text using multiple strategies"""
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
            tag.decompose()
        
        # Try different content selectors
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.article-body',
            '.story-body',
            '.content',
            'main'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Extract paragraphs from the content
                paragraphs = content_elem.find_all('p')
                if paragraphs and len(paragraphs) > 2:
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(text) > PROCESSING_LIMITS["min_article_length"]:
                        return text
        
        # Fallback: get all paragraphs
        all_paragraphs = soup.find_all('p')
        if all_paragraphs:
            text = ' '.join([p.get_text(strip=True) for p in all_paragraphs])
            if len(text) > PROCESSING_LIMITS["min_article_length"]:
                return text
        
        return ""
    
    def _extract_top_image(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract top image URL"""
        # Try different image selectors
        image_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            '.article-image img',
            '.featured-image img',
            'article img'
        ]
        
        for selector in image_selectors:
            img_elem = soup.select_one(selector)
            if img_elem:
                if selector.startswith('meta'):
                    img_url = img_elem.get('content', '')
                else:
                    img_url = img_elem.get('src', '')
                
                if img_url:
                    # Convert relative URL to absolute
                    return urljoin(base_url, img_url)
        
        return ""
    
    @handle_exceptions("scrape_article_content")
    def scrape_article_content(self, article: NewsArticle) -> NewsArticle:
        """Scrape full content for a news article using multiple methods"""
        try:
            url = article.original_url or article.link
            if not url:
                self.error_handler.log_warning("No URL available for scraping", "scrape_article_content")
                return article
            
            self.error_handler.log_info(f"Scraping article content from: {url}", "scrape_article_content")
            
            # Try different scraping methods in order of preference
            scraped_content = None
            
            # Method 1: newspaper3k (most reliable for news articles)
            scraped_content = self.scrape_with_newspaper3k(url)
            
            # Method 2: BeautifulSoup (fallback)
            if not scraped_content:
                time.sleep(1)  # Brief delay between methods
                scraped_content = self.scrape_with_beautifulsoup(url)
            
            # Method 3: readability (last resort)
            if not scraped_content and Document:
                time.sleep(1)  # Brief delay between methods
                scraped_content = self.scrape_with_readability(url)
            
            if scraped_content:
                # Update article with scraped content
                article.full_content = scraped_content["text"]
                
                # Update title if scraped title is better
                if scraped_content["title"] and len(scraped_content["title"]) > len(article.title):
                    article.title = scraped_content["title"]
                
                self.error_handler.log_info(f"Successfully scraped {len(article.full_content)} characters", "scrape_article_content")
            else:
                self.error_handler.log_warning("All scraping methods failed", "scrape_article_content")
            
            # Add rate limiting delay
            time.sleep(RATE_LIMIT_CONFIG["delay_between_requests"])
            
            return article
            
        except Exception as e:
            self.error_handler.log_error(e, f"scrape_article_content: {article.link}")
            return article
