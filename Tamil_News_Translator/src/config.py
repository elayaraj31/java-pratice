

# Google News RSS Feed URLs
GOOGLE_NEWS_URLS = {
    "top_stories": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "world": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB",
    "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pKVGlnQVAB",
    "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGxqTnpZU0FtVnVHZ0pKVGlnQVAB",
    "sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pKVGlnQVAB",
    "health": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNR3QwTlRFU0FtVnVHZ0pKVGlnQVAB",
    "entertainment": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREZqY0hsUUVnVnVaUzFWVXlnQVAB"
}

# Translation settings
TRANSLATION_CONFIG = {
    "source_language": "en",
    "target_language": "ta",  # Tamil language code
    "service_urls": [
        'translate.google.com',
        'translate.google.co.kr',
        'translate.google.co.in'
    ]
}

# Web scraping settings
SCRAPING_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "timeout": 30,
    "max_retries": 3,
    "backoff_factor": 1,
    "status_forcelist": [429, 500, 502, 503, 504],
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
}

# File paths
FILE_PATHS = {
    "json_output": "data/translated_articles.json",
    "text_output": "data/translated_articles.txt",
    "error_log": "data/error_log.txt"
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}

# Rate limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 30,
    "delay_between_requests": 2,  # seconds
    "google_news_delay": 1,  # seconds between Google News requests
    "translation_delay": 0.5  # seconds between translation requests
}

# Article processing limits
PROCESSING_LIMITS = {
    "max_articles_per_run": 50,
    "max_article_length": 15000,  # characters (googletrans limit)
    "min_article_length": 100,    # minimum article length to process
    "chunk_size": 5000           # for splitting long articles
}
