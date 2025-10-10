
import logging
import time
import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import LOGGING_CONFIG, SCRAPING_CONFIG, RATE_LIMIT_CONFIG


class ErrorHandler:
    """Central error handling class for the project"""
    
    def __init__(self, log_file: str = "data/error_log.txt"):
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG["level"]),
            format=LOGGING_CONFIG["format"],
            datefmt=LOGGING_CONFIG["datefmt"],
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_error(self, error: Exception, context: str = "", additional_info: Dict = None):
        """Log error with context and additional information"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "additional_info": additional_info or {}
        }
        
        self.logger.error(f"ERROR in {context}: {error_info}")
        return error_info
        
    def log_warning(self, message: str, context: str = ""):
        """Log warning message"""
        self.logger.warning(f"WARNING in {context}: {message}")
        
    def log_info(self, message: str, context: str = ""):
        """Log info message"""
        self.logger.info(f"INFO in {context}: {message}")


class NetworkErrorHandler:
    """Handles network-related errors and retries"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        
    def create_session_with_retries(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=SCRAPING_CONFIG["max_retries"],
            backoff_factor=SCRAPING_CONFIG["backoff_factor"],
            status_forcelist=SCRAPING_CONFIG["status_forcelist"],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    )
    def make_request(self, url: str, session: Optional[requests.Session] = None, **kwargs) -> requests.Response:
        """Make HTTP request with error handling and retries"""
        if session is None:
            session = self.create_session_with_retries()
            
        try:
            response = session.get(
                url, 
                headers=SCRAPING_CONFIG["headers"],
                timeout=SCRAPING_CONFIG["timeout"],
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            self.error_handler.log_error(e, f"HTTP Error for URL: {url}")
            if e.response.status_code == 429:
                self.error_handler.log_warning("Rate limit detected, slowing down requests", "make_request")
                time.sleep(RATE_LIMIT_CONFIG["delay_between_requests"] * 2)
            raise
            
        except requests.exceptions.ConnectionError as e:
            self.error_handler.log_error(e, f"Connection Error for URL: {url}")
            raise
            
        except requests.exceptions.Timeout as e:
            self.error_handler.log_error(e, f"Timeout Error for URL: {url}")
            raise
            
        except requests.exceptions.RequestException as e:
            self.error_handler.log_error(e, f"Request Error for URL: {url}")
            raise


def handle_exceptions(context: str = ""):
    """Decorator for handling exceptions in functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                error_handler.log_error(e, context or func.__name__)
                return None
        return wrapper
    return decorator


def rate_limit(calls_per_minute: int = 30):
    """Decorator for rate limiting function calls"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator


class TranslationErrorHandler:
    """Specialized error handler for translation operations"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        
    def handle_translation_error(self, error: Exception, text: str, attempt: int = 1) -> Optional[str]:
        """Handle translation-specific errors"""
        if "Too Many Requests" in str(error) or "429" in str(error):
            self.error_handler.log_warning(f"Translation rate limit hit, attempt {attempt}", "translation")
            time.sleep(RATE_LIMIT_CONFIG["translation_delay"] * attempt)
            return None
            
        elif "Service Unavailable" in str(error):
            self.error_handler.log_warning("Translation service unavailable", "translation")
            time.sleep(5)
            return None
            
        else:
            self.error_handler.log_error(error, f"Translation failed for text: {text[:100]}...")
            return None


# Global error handler instance
global_error_handler = ErrorHandler()
