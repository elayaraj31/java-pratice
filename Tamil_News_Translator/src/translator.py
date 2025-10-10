
"""
Updated Translator module for Tamil News Translator
Handles translation of text from English to Tamil using deep-translator (more reliable)
"""

import time
from typing import Optional, List
import re

from deep_translator import GoogleTranslator

from config import TRANSLATION_CONFIG, RATE_LIMIT_CONFIG, PROCESSING_LIMITS
from error_handler import ErrorHandler, TranslationErrorHandler, handle_exceptions, rate_limit
from news_fetcher import NewsArticle


class TamilTranslator:
    """Translates text from English to Tamil using deep-translator library"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.translation_error_handler = TranslationErrorHandler(self.error_handler)
        
        # Initialize Google Translator with deep-translator (more reliable)
        self.translator = GoogleTranslator(
            source=TRANSLATION_CONFIG["source_language"],
            target=TRANSLATION_CONFIG["target_language"]
        )
        
        # Translation cache to avoid duplicate translations
        self.translation_cache = {}
    
    @handle_exceptions("translate_text")
    @rate_limit(calls_per_minute=20)  # Conservative rate limiting for translation
    def translate_text(self, text: str, max_retries: int = 3) -> Optional[str]:
        """Translate text from English to Tamil"""
        if not text or not text.strip():
            return None
        
        # Clean the text
        text = text.strip()
        
        # Check cache first
        text_key = text[:100]  # Use first 100 chars as key
        if text_key in self.translation_cache:
            self.error_handler.log_info("Using cached translation", "translate_text")
            return self.translation_cache[text_key]
        
        # Split text if it's too long
        if len(text) > PROCESSING_LIMITS["max_article_length"]:
            return self._translate_long_text(text, max_retries)
        
        for attempt in range(max_retries):
            try:
                self.error_handler.log_info(f"Translating text (attempt {attempt + 1}): {text[:50]}...", "translate_text")
                
                # Perform translation using deep-translator
                translated_text = self.translator.translate(text)
                
                if translated_text and translated_text.strip():
                    # Cache the translation
                    self.translation_cache[text_key] = translated_text
                    
                    self.error_handler.log_info(f"Translation successful: {translated_text[:50]}...", "translate_text")
                    
                    # Add delay to respect rate limits
                    time.sleep(RATE_LIMIT_CONFIG["translation_delay"])
                    
                    return translated_text
                else:
                    self.error_handler.log_warning("Translation returned empty result", "translate_text")
                    
            except Exception as e:
                self.error_handler.log_error(e, f"translate_text attempt {attempt + 1}")
                
                # Handle specific translation errors
                error_str = str(e).lower()
                if "429" in error_str or "too many requests" in error_str:
                    self.error_handler.log_warning(f"Rate limit hit, waiting...", "translate_text")
                    wait_time = RATE_LIMIT_CONFIG["translation_delay"] * (attempt + 2)
                    time.sleep(wait_time)
                elif "quota" in error_str or "limit" in error_str:
                    self.error_handler.log_error(e, "Translation quota exceeded")
                    return None
                else:
                    if attempt < max_retries - 1:
                        wait_time = RATE_LIMIT_CONFIG["translation_delay"] * (attempt + 1)
                        time.sleep(wait_time)
                        continue
        
        return None
    
    @handle_exceptions("_translate_long_text")
    def _translate_long_text(self, text: str, max_retries: int = 3) -> Optional[str]:
        """Translate long text by splitting into chunks"""
        try:
            self.error_handler.log_info(f"Translating long text ({len(text)} chars)", "_translate_long_text")
            
            # Split text into sentences for better context
            sentences = self._split_into_sentences(text)
            translated_chunks = []
            
            current_chunk = ""
            
            for sentence in sentences:
                # Check if adding this sentence would exceed chunk size
                if len(current_chunk) + len(sentence) > PROCESSING_LIMITS["chunk_size"]:
                    if current_chunk:
                        # Translate current chunk
                        translated_chunk = self.translate_text(current_chunk.strip(), max_retries)
                        if translated_chunk:
                            translated_chunks.append(translated_chunk)
                        
                        # Add delay between chunks
                        time.sleep(RATE_LIMIT_CONFIG["translation_delay"] * 2)
                    
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
            
            # Translate remaining chunk
            if current_chunk.strip():
                translated_chunk = self.translate_text(current_chunk.strip(), max_retries)
                if translated_chunk:
                    translated_chunks.append(translated_chunk)
            
            if translated_chunks:
                final_translation = " ".join(translated_chunks)
                self.error_handler.log_info(f"Successfully translated long text into {len(final_translation)} chars", "_translate_long_text")
                return final_translation
            else:
                self.error_handler.log_warning("Failed to translate any chunks", "_translate_long_text")
                return None
                
        except Exception as e:
            self.error_handler.log_error(e, "_translate_long_text")
            return None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for better translation context"""
        # Simple sentence splitting (can be improved with NLTK)
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Ignore very short fragments
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    @handle_exceptions("detect_language")
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of given text (simplified version)"""
        try:
            if not text or not text.strip():
                return None
            
            # Simple heuristic: if text contains mostly English characters, assume English
            english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
            total_chars = sum(1 for c in text if c.isalpha())
            
            if total_chars > 0:
                english_ratio = english_chars / total_chars
                if english_ratio > 0.7:
                    self.error_handler.log_info("Detected language: en (English)", "detect_language")
                    return "en"
                else:
                    self.error_handler.log_info("Detected language: non-English", "detect_language")
                    return "other"
            
            return "en"  # Default to English
            
        except Exception as e:
            self.error_handler.log_error(e, "detect_language")
            return "en"  # Default to English
    
    @handle_exceptions("translate_article")
    def translate_article(self, article: NewsArticle) -> NewsArticle:
        """Translate both title and content of a news article"""
        try:
            self.error_handler.log_info(f"Translating article: {article.title[:50]}...", "translate_article")
            
            # Translate title
            if article.title:
                self.error_handler.log_info("Translating title...", "translate_article")
                translated_title = self.translate_text(article.title)
                if translated_title:
                    article.translated_title = translated_title
                    self.error_handler.log_info(f"Title translation successful: {translated_title[:50]}...", "translate_article")
                else:
                    self.error_handler.log_warning("Title translation failed", "translate_article")
            
            # Translate content
            if article.full_content:
                self.error_handler.log_info("Translating content...", "translate_article")
                
                # Always translate content (don't worry about language detection for now)
                translated_content = self.translate_text(article.full_content)
                if translated_content:
                    article.translated_content = translated_content
                    self.error_handler.log_info(f"Content translation successful ({len(translated_content)} chars)", "translate_article")
                else:
                    self.error_handler.log_warning("Content translation failed", "translate_article")
            else:
                self.error_handler.log_warning("No content to translate", "translate_article")
            
            return article
            
        except Exception as e:
            self.error_handler.log_error(e, f"translate_article: {article.title}")
            return article
    
    @handle_exceptions("translate_multiple_articles")
    def translate_multiple_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Translate multiple articles with progress tracking"""
        translated_articles = []
        total_articles = len(articles)
        
        try:
            self.error_handler.log_info(f"Starting translation of {total_articles} articles", "translate_multiple_articles")
            
            for i, article in enumerate(articles, 1):
                self.error_handler.log_info(f"Translating article {i}/{total_articles}", "translate_multiple_articles")
                
                # Translate the article
                translated_article = self.translate_article(article)
                translated_articles.append(translated_article)
                
                # Progress update
                if i % 5 == 0 or i == total_articles:
                    successful = sum(1 for a in translated_articles[:i] if a.translated_title or a.translated_content)
                    self.error_handler.log_info(f"Completed {i}/{total_articles} translations ({successful} successful)", "translate_multiple_articles")
                
                # Rate limiting delay between articles
                if i < total_articles:  # Don't delay after the last article
                    time.sleep(RATE_LIMIT_CONFIG["translation_delay"] * 2)
            
            successful_translations = sum(1 for a in translated_articles if a.translated_title or a.translated_content)
            self.error_handler.log_info(f"Translation completed: {successful_translations}/{total_articles} successful", "translate_multiple_articles")
            
            return translated_articles
            
        except Exception as e:
            self.error_handler.log_error(e, "translate_multiple_articles")
            return translated_articles
    
    def get_translation_stats(self, articles: List[NewsArticle]) -> dict:
        """Get translation statistics"""
        stats = {
            "total_articles": len(articles),
            "titles_translated": sum(1 for a in articles if a.translated_title),
            "content_translated": sum(1 for a in articles if a.translated_content),
            "fully_translated": sum(1 for a in articles if a.translated_title and a.translated_content),
            "cache_size": len(self.translation_cache)
        }
        
        return stats


