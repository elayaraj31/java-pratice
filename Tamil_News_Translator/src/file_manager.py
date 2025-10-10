
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from config import FILE_PATHS
from error_handler import ErrorHandler, handle_exceptions
from news_fetcher import NewsArticle


class FileManager:
    """Manages file operations for saving translated articles"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(FILE_PATHS["json_output"])
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.error_handler.log_info(f"Created data directory: {data_dir}", "file_manager")
    
    @handle_exceptions("save_to_json")
    def save_to_json(self, articles: List[NewsArticle], filename: str = None) -> bool:
        """Save articles to JSON file"""
        try:
            filename = filename or FILE_PATHS["json_output"]
            
            # Convert articles to dictionaries
            articles_data = []
            for article in articles:
                article_dict = article.to_dict()
                articles_data.append(article_dict)
            
            # Create complete data structure
            data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_articles": len(articles),
                    "translated_articles": sum(1 for a in articles if a.translated_title or a.translated_content),
                    "format_version": "1.0"
                },
                "articles": articles_data
            }
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.error_handler.log_info(f"Successfully saved {len(articles)} articles to {filename}", "save_to_json")
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, f"save_to_json: {filename}")
            return False
    
    @handle_exceptions("save_to_text")
    def save_to_text(self, articles: List[NewsArticle], filename: str = None) -> bool:
        """Save articles to formatted text file"""
        try:
            filename = filename or FILE_PATHS["text_output"]
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("தமிழ் செய்தி மொழிபெயர்ப்பு (Tamil News Translation)\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total articles: {len(articles)}\n")
                f.write("=" * 80 + "\n\n")
                
                # Write articles
                for i, article in enumerate(articles, 1):
                    f.write(f"Article {i}:\n")
                    f.write("-" * 50 + "\n")
                    
                    # Original title
                    if article.title:
                        f.write(f"Original Title: {article.title}\n")
                    
                    # Tamil title
                    if article.translated_title:
                        f.write(f"Tamil Title: {article.translated_title}\n")
                    
                    # Source and publication info
                    if article.source:
                        f.write(f"Source: {article.source}\n")
                    
                    if article.published:
                        f.write(f"Published: {article.published}\n")
                    
                    if article.original_url:
                        f.write(f"URL: {article.original_url}\n")
                    
                    f.write("\n")
                    
                    # Original content (first 200 chars)
                    if article.full_content:
                        f.write("Original Content (excerpt):\n")
                        excerpt = article.full_content[:200] + "..." if len(article.full_content) > 200 else article.full_content
                        f.write(f"{excerpt}\n\n")
                    
                    # Tamil translation
                    if article.translated_content:
                        f.write("Tamil Translation:\n")
                        f.write(f"{article.translated_content}\n")
                    else:
                        f.write("Tamil Translation: Not available\n")
                    
                    f.write("\n" + "=" * 80 + "\n\n")
            
            self.error_handler.log_info(f"Successfully saved {len(articles)} articles to {filename}", "save_to_text")
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, f"save_to_text: {filename}")
            return False
    
    @handle_exceptions("load_from_json")
    def load_from_json(self, filename: str = None) -> List[NewsArticle]:
        """Load articles from JSON file"""
        try:
            filename = filename or FILE_PATHS["json_output"]
            
            if not os.path.exists(filename):
                self.error_handler.log_warning(f"File not found: {filename}", "load_from_json")
                return []
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            articles = []
            articles_data = data.get("articles", [])
            
            for article_dict in articles_data:
                article = NewsArticle(
                    title=article_dict.get("title", ""),
                    link=article_dict.get("link", ""),
                    published=article_dict.get("published", ""),
                    description=article_dict.get("description", ""),
                    source=article_dict.get("source", "")
                )
                
                # Set additional attributes
                article.original_url = article_dict.get("original_url")
                article.full_content = article_dict.get("full_content")
                article.translated_title = article_dict.get("translated_title")
                article.translated_content = article_dict.get("translated_content")
                
                articles.append(article)
            
            self.error_handler.log_info(f"Successfully loaded {len(articles)} articles from {filename}", "load_from_json")
            return articles
            
        except Exception as e:
            self.error_handler.log_error(e, f"load_from_json: {filename}")
            return []
    
    @handle_exceptions("create_summary_report")
    def create_summary_report(self, articles: List[NewsArticle], translation_stats: Dict[str, Any]) -> bool:
        """Create a summary report of the translation process"""
        try:
            report_filename = f"data/summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write("Tamil News Translator - Summary Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Statistics
                f.write("Translation Statistics:\n")
                f.write("-" * 25 + "\n")
                f.write(f"Total articles processed: {translation_stats.get('total_articles', 0)}\n")
                f.write(f"Titles translated: {translation_stats.get('titles_translated', 0)}\n")
                f.write(f"Content translated: {translation_stats.get('content_translated', 0)}\n")
                f.write(f"Fully translated: {translation_stats.get('fully_translated', 0)}\n")
                f.write(f"Translation cache size: {translation_stats.get('cache_size', 0)}\n\n")
                
                # Success rate
                total = translation_stats.get('total_articles', 0)
                if total > 0:
                    success_rate = (translation_stats.get('fully_translated', 0) / total) * 100
                    f.write(f"Success rate: {success_rate:.2f}%\n\n")
                
                # File information
                f.write("Output Files:\n")
                f.write("-" * 15 + "\n")
                f.write(f"JSON file: {FILE_PATHS['json_output']}\n")
                f.write(f"Text file: {FILE_PATHS['text_output']}\n")
                f.write(f"Error log: {FILE_PATHS['error_log']}\n\n")
                
                # Article titles (first 10)
                f.write("Processed Articles (first 10):\n")
                f.write("-" * 35 + "\n")
                for i, article in enumerate(articles[:10], 1):
                    title = article.translated_title or article.title or "No title"
                    f.write(f"{i:2d}. {title[:60]}...\n")
                
                if len(articles) > 10:
                    f.write(f"... and {len(articles) - 10} more articles\n")
            
            self.error_handler.log_info(f"Summary report saved to {report_filename}", "create_summary_report")
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "create_summary_report")
            return False
    
    @handle_exceptions("backup_existing_files")
    def backup_existing_files(self) -> bool:
        """Backup existing output files before overwriting"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for file_type, filepath in FILE_PATHS.items():
                if os.path.exists(filepath) and file_type in ['json_output', 'text_output']:
                    backup_name = f"{filepath}.backup_{timestamp}"
                    os.rename(filepath, backup_name)
                    self.error_handler.log_info(f"Backed up {filepath} to {backup_name}", "backup_existing_files")
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "backup_existing_files")
            return False
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about output files"""
        info = {}
        
        for file_type, filepath in FILE_PATHS.items():
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                info[file_type] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                info[file_type] = {"exists": False}
        
        return info
