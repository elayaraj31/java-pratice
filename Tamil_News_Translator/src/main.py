
import sys
import argparse
from datetime import datetime
from typing import List, Optional

from config import GOOGLE_NEWS_URLS, PROCESSING_LIMITS, FILE_PATHS
from error_handler import ErrorHandler
from news_fetcher import GoogleNewsFetcher, NewsArticle
from content_scraper import ContentScraper
from translator import TamilTranslator
from file_manager import FileManager


class TamilNewsTranslator:
    """Main class that orchestrates the entire translation process"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.news_fetcher = GoogleNewsFetcher()
        self.content_scraper = ContentScraper()
        self.translator = TamilTranslator()
        self.file_manager = FileManager()
        
        self.error_handler.log_info("Tamil News Translator initialized", "main")
    
    def run(self, category: str = "top_stories", query: str = None, max_articles: int = None) -> bool:
        """Run the complete translation process"""
        try:
            max_articles = max_articles or PROCESSING_LIMITS["max_articles_per_run"]
            
            self.error_handler.log_info(f"Starting Tamil News Translator", "run")
            self.error_handler.log_info(f"Category: {category}, Query: {query}, Max articles: {max_articles}", "run")
            
            # Step 1: Fetch news articles
            self.error_handler.log_info("Step 1: Fetching news articles...", "run")
            if query:
                articles = self.news_fetcher.fetch_news_by_query(query)
            else:
                articles = self.news_fetcher.fetch_news_by_category(category)
            
            if not articles:
                self.error_handler.log_warning("No articles fetched", "run")
                return False
            
            # Limit articles if needed
            articles = articles[:max_articles]
            self.error_handler.log_info(f"Fetched {len(articles)} articles", "run")
            
            # Step 2: Scrape full content
            self.error_handler.log_info("Step 2: Scraping full content...", "run")
            scraped_articles = []
            for i, article in enumerate(articles, 1):
                self.error_handler.log_info(f"Scraping article {i}/{len(articles)}: {article.title[:50]}...", "run")
                scraped_article = self.content_scraper.scrape_article_content(article)
                scraped_articles.append(scraped_article)
            
            # Filter articles with content
            articles_with_content = [a for a in scraped_articles if a.full_content]
            self.error_handler.log_info(f"Successfully scraped content for {len(articles_with_content)} articles", "run")
            
            if not articles_with_content:
                self.error_handler.log_warning("No articles with content to translate", "run")
                # Still save the articles we have
                self.file_manager.save_to_json(scraped_articles)
                self.file_manager.save_to_text(scraped_articles)
                return False
            
            # Step 3: Translate articles
            self.error_handler.log_info("Step 3: Translating articles...", "run")
            translated_articles = self.translator.translate_multiple_articles(articles_with_content)
            
            # Step 4: Save results
            self.error_handler.log_info("Step 4: Saving results...", "run")
            
            # Backup existing files
            self.file_manager.backup_existing_files()
            
            # Save to JSON
            json_success = self.file_manager.save_to_json(translated_articles)
            
            # Save to text
            text_success = self.file_manager.save_to_text(translated_articles)
            
            # Create summary report
            translation_stats = self.translator.get_translation_stats(translated_articles)
            report_success = self.file_manager.create_summary_report(translated_articles, translation_stats)
            
            # Log final results
            self.error_handler.log_info("Translation process completed!", "run")
            self.error_handler.log_info(f"Results:", "run")
            self.error_handler.log_info(f"  - Total articles processed: {len(translated_articles)}", "run")
            self.error_handler.log_info(f"  - Articles with translated titles: {translation_stats['titles_translated']}", "run")
            self.error_handler.log_info(f"  - Articles with translated content: {translation_stats['content_translated']}", "run")
            self.error_handler.log_info(f"  - Fully translated articles: {translation_stats['fully_translated']}", "run")
            self.error_handler.log_info(f"  - JSON saved: {json_success}", "run")
            self.error_handler.log_info(f"  - Text saved: {text_success}", "run")
            self.error_handler.log_info(f"  - Report created: {report_success}", "run")
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "run")
            return False
    
    def run_interactive(self):
        """Run the translator in interactive mode"""
        print("\n" + "="*60)
        print("   Tamil News Translator (தமிழ் செய்தி மொழிபெயர்ப்பு)")
        print("="*60)
        print()
        
        try:
            # Get user preferences
            print("Available categories:")
            categories = self.news_fetcher.get_available_categories()
            for i, category in enumerate(categories, 1):
                print(f"  {i}. {category}")
            print(f"  {len(categories) + 1}. Custom search query")
            print()
            
            choice = input("Select category (number) or press Enter for top_stories: ").strip()
            
            if not choice:
                category = "top_stories"
                query = None
                print(f"Selected: {category}")
            elif choice.isdigit() and 1 <= int(choice) <= len(categories):
                category = categories[int(choice) - 1]
                query = None
                print(f"Selected: {category}")
            elif choice.isdigit() and int(choice) == len(categories) + 1:
                query = input("Enter search query: ").strip()
                if not query:
                    print("No query provided, using top_stories")
                    category = "top_stories"
                    query = None
                else:
                    category = None
                    print(f"Search query: {query}")
            else:
                print("Invalid choice, using top_stories")
                category = "top_stories"
                query = None
            
            # Get number of articles
            max_articles_input = input(f"Maximum articles to process (default {PROCESSING_LIMITS['max_articles_per_run']}): ").strip()
            try:
                max_articles = int(max_articles_input) if max_articles_input else PROCESSING_LIMITS['max_articles_per_run']
                max_articles = min(max_articles, 100)  # Limit to 100 for safety
            except ValueError:
                max_articles = PROCESSING_LIMITS['max_articles_per_run']
            
            print(f"\nProcessing {max_articles} articles...")
            print("This may take several minutes depending on the number of articles.")
            print("Please be patient...\n")
            
            # Run the process
            success = self.run(category=category, query=query, max_articles=max_articles)
            
            if success:
                print("\n" + "="*60)
                print("   Translation completed successfully!")
                print("="*60)
                print("\nOutput files:")
                print(f"  - JSON: {FILE_PATHS['json_output']}")
                print(f"  - Text: {FILE_PATHS['text_output']}")
                print(f"  - Error log: {FILE_PATHS['error_log']}")
            else:
                print("\n" + "="*60)
                print("   Translation completed with errors!")
                print("="*60)
                print(f"Check the error log: {self.file_manager.FILE_PATHS['error_log']}")
                
        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user.")
        except Exception as e:
            self.error_handler.log_error(e, "run_interactive")
            print(f"\nAn error occurred: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Tamil News Translator")
    parser.add_argument(
        "--category", 
        choices=list(GOOGLE_NEWS_URLS.keys()),
        default="top_stories",
        help="News category to fetch"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Search query for custom news search"
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=PROCESSING_LIMITS["max_articles_per_run"],
        help="Maximum number of articles to process"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Create translator instance
    translator = TamilNewsTranslator()
    
    if args.interactive:
        translator.run_interactive()
    else:
        success = translator.run(
            category=args.category,
            query=args.query,
            max_articles=args.max_articles
        )
        
        if success:
            print("Translation completed successfully!")
        else:
            print("Translation completed with errors!")
            sys.exit(1)


if __name__ == "__main__":
    main()
