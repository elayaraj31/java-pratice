import json
import asyncio
import time
import logging
from datetime import datetime
from pathlib import Path
import sqlite3
import os
import io

# --- Image Processing Libraries ---
from PIL import Image, ImageSequence, ImageEnhance 

import google.generativeai as genai
from dateutil import parser
from GoogleNews import GoogleNews
from newspaper import Article, Config
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import shutil
from elevenlabs.client import ElevenLabs
from elevenlabs import save as save_audio
from io import BytesIO
from datetime import datetime, timedelta  # <--- timedelta-வை இங்கே சேர்க்கவும்

# --- [NEW] Google Cloud TTS Import ---
from google.cloud import texttospeech
from google.oauth2 import service_account

# --- Configuration ---------------------------------------------------
MIN_TEXT_LENGTH = 250
DB_FILE = "news_archive.db"
DEFAULT_ARTICLES_TO_FETCH = 20
DEFAULT_MAX_CONCURRENT = 50
JSON_OUTPUT_DIR = Path("news_articles")
ELEVENLABS_AUDIO_DIR = Path("static/audio")
IMAGE_OUTPUT_DIR = Path("static/images")

# --- Logo Path Configuration ---
COMPANY_LOGO_PATH = Path("static/logo.png")

# --- Flask App Setup -------------------------------------------------
app = Flask(__name__, static_folder='static')

# --- Gemini AI Configuration ------------------------------------
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
    gemini_image_model = genai.GenerativeModel('gemini-2.5-flash-image')
except KeyError:
    logging.warning("!!! GEMINI_API_KEY environment variable not set. AI Writer will not work. !!!")
    gemini_model = None
    gemini_image_model = None

# --- ElevenLabs AI Configuration ------------------------------------
try:
    elevenlabs_client = ElevenLabs(
        api_key=os.environ["ELEVENLABS_API_KEY"]
    )
    ELEVENLABS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("ElevenLabs client configured.")
except KeyError:
    logging.warning("!!! ELEVENLABS_API_KEY environment variable not set. !!!")
    elevenlabs_client = None

# --- [UPDATED] Google Cloud TTS Configuration with Path Fix ---
google_tts_client = None
try:
    # 1. தற்போதைய ஃபைல் (webmap.py) இருக்கும் இடத்தைக் கண்டுபிடித்தல்
    base_dir = os.path.dirname(os.path.abspath(__file__))
    key_file_path = os.path.join(base_dir, "key.json")

    # 2. அந்த இடத்தில் key.json இருக்கிறதா என்று பார்த்தல்
    if os.path.exists(key_file_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
        google_tts_client = texttospeech.TextToSpeechClient()
        logging.info(f"Google Cloud TTS client configured using: {key_file_path}")
    
    # 3. அல்லது Environment Variable-ல் உள்ளதா என்று பார்த்தல்
    elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        google_tts_client = texttospeech.TextToSpeechClient()
        logging.info("Google Cloud TTS client configured from Environment Variable.")
    else:
        logging.warning(f"!!! key.json not found at {key_file_path}. Google TTS will NOT work. !!!")
except Exception as e:
    logging.error(f"Error configuring Google TTS: {e}")


# --- Constants ---
STATES = {
    '': 'Select a State...',
    'Tamil Nadu': 'தமிழ்நாடு (Tamil Nadu)',
    'Karnataka': 'ಕರ್ನಾಟಕ (Karnataka)',
    'Kerala': 'കേരളം (Kerala)',
    'Maharashtra': 'महाराष्ट्र (Maharashtra)',
    'New Delhi': 'नई दिल्ली (New Delhi)',
    'Andhra Pradesh': 'ఆంధ్ర ప్రదేశ్ (Andhra Pradesh)',
    'Telangana': 'తెలంగాణ (Telangana)',
    'Uttar Pradesh': 'उत्तर प्रदेश (Uttar Pradesh)',
    'Gujarat': 'ગુજરાત (Gujarat)',
    'West Bengal': 'পশ্চিমবঙ্গ (West Bengal)'
}

LANGUAGES = {
    'en': 'English', 'ta': 'தமிழ் (Tamil)', 'hi': 'हिंदी (Hindi)',
    'kn': 'ಕನ್ನಡ (Kannada)', 'te': 'తెలుగు (Telugu)', 'ml': 'മലയാളം (Malayalam)'
}

# ElevenLabs Voice IDs (We use names to guess gender for Google TTS)
VOICES = {
    "Rachel": "pNInz6obpgDQGcFmaJgB",   # Female
    "Bharati": "C2RGMrNBTZaNfddRPeRH",  # Female
    "Adam": "pNInz6obpgDQGcFmaJgB",     # Male (Assuming ID maps to a male voice concept)
    "Charlie": "IKne3meq5aSn9XLyUdCD",  # Male
    "Sia": "XwkIUwRxNu9PpezCu4Vg",      # Female
    "Matilda": "NihRgaLj2HWAjvZ5XNxl",  # Female
    "Nila": "C2RGMrNBTZaNfddRPeRH",     # Female
    "Alice": "Xb7hH8MSUJpSbSDYk0k2"     # Female
}

# Male Names Set for Detection
MALE_VOICE_NAMES = {"Adam", "Charlie", "Brian", "Daniel"}

CATEGORIES = ['India', 'World', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health', 'Agriculture']

# --- Logging Setup ---------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Date Formatting Helper ------------------------------------------
@app.template_filter('formatdate')
def format_date_filter(date_str):
    if not date_str or date_str == "None": return ""
    try:
        dt = parser.parse(date_str)
        return dt.strftime('%B %d, %Y')
    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%B %d, %Y')
        except Exception:
            return date_str

# --- Helper Function: GIF & Watermark ---
def add_watermark_and_create_gif(input_image_path, output_filename):
    try:
        base_image = Image.open(input_image_path).convert("RGBA")
        base_w, base_h = base_image.size

        if COMPANY_LOGO_PATH.exists():
            logo = Image.open(COMPANY_LOGO_PATH).convert("RGBA")
            
            logo_ratio = 0.15
            logo_w = int(base_w * logo_ratio)
            logo_aspect = logo.size[1] / logo.size[0]
            logo_h = int(logo_w * logo_aspect)
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)

            margin = 20
            position = (base_w - logo_w - margin, base_h - logo_h - margin)
            
            base_image.paste(logo, position, logo)
        else:
            logging.warning("Logo file not found via path. Skipping watermark.")

        frames = []
        num_frames = 20  
        zoom_factor = 1.2 

        for i in range(num_frames):
            scale = 1 + (zoom_factor - 1) * (i / num_frames)
            
            crop_w = base_w / scale
            crop_h = base_h / scale
            left = (base_w - crop_w) / 2
            top = (base_h - crop_h) / 2
            right = left + crop_w
            bottom = top + crop_h
            
            frame = base_image.crop((left, top, right, bottom))
            frame = frame.resize((base_w, base_h), Image.Resampling.LANCZOS)
            frames.append(frame.convert("RGB"))

        gif_filename = output_filename.replace(".png", ".gif")
        save_path = IMAGE_OUTPUT_DIR / gif_filename
        
        frames[0].save(
            save_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=100, 
            loop=0
        )
        
        return f"static/images/{gif_filename}"

    except Exception as e:
        logging.error(f"Error creating GIF/Watermark: {e}")
        return None

# --- Database Functions ----------------
def setup_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, authors TEXT, publish_date TEXT, 
        text TEXT, text_length INTEGER, top_image TEXT, keywords TEXT,
        summary TEXT, canonical_link TEXT, original_url TEXT UNIQUE, 
        fetch_timestamp TEXT, category TEXT,
        ai_generated_content TEXT,
        ai_generated_audio_path TEXT, 
        is_processed INTEGER DEFAULT 0,
        ai_title TEXT,
        ai_content TEXT,
        ai_generated_image_path TEXT,
        ai_generated_video_path TEXT
    )
    """)
    
    try: cursor.execute("SELECT ai_title FROM articles LIMIT 1")
    except sqlite3.OperationalError: cursor.execute("ALTER TABLE articles ADD COLUMN ai_title TEXT"); cursor.execute("ALTER TABLE articles ADD COLUMN ai_content TEXT")

    try: cursor.execute("SELECT ai_generated_content FROM articles LIMIT 1")
    except sqlite3.OperationalError: cursor.execute("ALTER TABLE articles ADD COLUMN ai_generated_content TEXT"); cursor.execute("ALTER TABLE articles ADD COLUMN is_processed INTEGER DEFAULT 0")

    try: cursor.execute("SELECT ai_generated_audio_path FROM articles LIMIT 1")
    except sqlite3.OperationalError: cursor.execute("ALTER TABLE articles ADD COLUMN ai_generated_audio_path TEXT")
        
    try: cursor.execute("SELECT ai_generated_image_path FROM articles LIMIT 1")
    except sqlite3.OperationalError: cursor.execute("ALTER TABLE articles ADD COLUMN ai_generated_image_path TEXT")

    try: cursor.execute("SELECT ai_generated_video_path FROM articles LIMIT 1")
    except sqlite3.OperationalError: cursor.execute("ALTER TABLE articles ADD COLUMN ai_generated_video_path TEXT")
        
    try: cursor.execute("ALTER TABLE articles DROP COLUMN source")
    except sqlite3.OperationalError: pass

    conn.commit()
    conn.close()
    logging.info(f"Database '{db_name}' initialized.")

def save_articles_to_db(db_name, articles_list, category_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    inserted_count = 0
    
    sql = """
    INSERT OR IGNORE INTO articles (
        title, authors, publish_date, text, text_length, top_image,
        keywords, summary, canonical_link, original_url, fetch_timestamp, category
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    for article in articles_list:
        try:
            authors_str = json.dumps(article.get('authors', []))
            keywords_str = json.dumps(article.get('keywords', []))
            cursor.execute(sql, (
                article.get('title'), authors_str, article.get('publish_date'),
                article.get('text'), article.get('text_length'), article.get('top_image'),
                keywords_str, article.get('summary'), article.get('canonical_link'),
                article.get('original_url'), article.get('fetch_timestamp'),
                category_name
            ))
            inserted_count += cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Failed to insert article: {e}")
    conn.commit()
    conn.close()
    return inserted_count

# --- Scraper Functions -------------------------------
def download_and_parse_sync(original_url, config, timeout=30):
    article = Article(original_url, config=config)
    article.download()
    article.parse()
    article.nlp()
    pub_date = str(article.publish_date) if article.publish_date else datetime.now().isoformat()
    return {
        "title": article.title, "authors": article.authors,
        "publish_date": pub_date, "text": article.text,
        "text_length": len(article.text), "top_image": article.top_image,
        "movies": article.movies, "keywords": article.keywords,
        "summary": article.summary, "canonical_link": article.canonical_link,
        "original_url": original_url, "fetch_timestamp": datetime.now().isoformat()
    }

async def fetch_single_article_async(original_url, config, semaphore, timeout=30):
    async with semaphore:
        try:
            await asyncio.sleep(0.1)
            article_json = await asyncio.wait_for(
                asyncio.to_thread(download_and_parse_sync, original_url, config, timeout),
                timeout=timeout
            )
            return article_json
        except Exception:
            return None

async def fetch_and_parse_news(search_term, category_name, date_from=None, date_to=None, offset=0):
    num_articles = DEFAULT_ARTICLES_TO_FETCH
    max_concurrent = DEFAULT_MAX_CONCURRENT
    
    full_search_term = search_term
    if date_from:
        if len(date_from) >= 8 and '-' in date_from:
            full_search_term += f" after:{date_from}"
    if date_to:
        if len(date_to) >= 8 and '-' in date_to:
            full_search_term += f" before:{date_to}"
            
    logging.info(f"--- Starting Scrape Job for Category: '{category_name}' (Search: '{full_search_term}', Offset: {offset}) ---")
    
    googlenews = GoogleNews(lang='en')
    googlenews.search(full_search_term) 

    start_page = (offset // 10) + 1 
    if start_page > 1:
        googlenews.getpage(start_page)
        
    num_pages_to_fetch = start_page + ((num_articles + 9) // 10)
    all_results = googlenews.results()
    
    if num_pages_to_fetch > start_page:
        for page in range(start_page + 1, num_pages_to_fetch + 1):
            googlenews.getpage(page)
            page_results = googlenews.results()
            if not page_results: break
            all_results.extend(page_results)
    
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    config.request_timeout = 15
    config.fetch_images = False
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = []
    seen_urls = set()
    
    for entry in all_results:
        if len(tasks) >= num_articles: break
        original_url = entry['link'].split('&ved=')[0] 
        if original_url and original_url not in seen_urls and original_url.startswith('http'):
            seen_urls.add(original_url)
            tasks.append(fetch_single_article_async(original_url, config, semaphore, timeout=config.request_timeout))

    all_data = await asyncio.gather(*tasks)
    valid_articles = [data for data in all_data if data is not None]
    filtered_articles = []
    for article in valid_articles:
        if article.get("text_length", 0) > MIN_TEXT_LENGTH and article.get("title"):
            filtered_articles.append(article)
    
    newly_inserted_urls = [a['original_url'] for a in filtered_articles]
    if newly_inserted_urls:
        save_articles_to_db(DB_FILE, filtered_articles, category_name)
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in newly_inserted_urls)
        cursor.execute(f"SELECT id, title, summary, text, original_url, publish_date FROM articles WHERE original_url IN ({placeholders})", newly_inserted_urls)
        articles_with_ids = cursor.fetchall()
        conn.close()
        final_articles = []
        for row in articles_with_ids:
            article_dict = dict(row)
            article_dict['publish_date'] = format_date_filter(article_dict['publish_date'])
            final_articles.append(article_dict)
        return final_articles
    return []

def fetch_breaking_news_job():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fetch_and_parse_news(search_term="Latest News", category_name="Home"))
    except Exception as e:
        logging.error(f"Error in background job: {e}")

# --- Web Routes (Flask) -----------------------------------
@app.context_processor
def inject_shared_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    conn.close()
    
    category_icons = {
        'India': 'fa-solid fa-flag',
        'World': 'fa-solid fa-globe',
        'Business': 'fa-solid fa-chart-line',
        'Technology': 'fa-solid fa-microchip',
        'Entertainment': 'fa-solid fa-film',
        'Sports': 'fa-solid fa-futbol',
        'Science': 'fa-solid fa-flask',
        'Health': 'fa-solid fa-heart-pulse',
        'Agriculture': 'fa-solid fa-wheat-awn'
    }
    
    return dict(
        CATEGORIES=CATEGORIES, 
        LANGUAGES=LANGUAGES, 
        VOICES=VOICES, 
        STATES=STATES, 
        article_count=count,
        CATEGORY_ICONS=category_icons
    )

def get_articles_from_db(query, params):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    articles = cursor.fetchall()
    conn.close()
    return articles

def build_date_query(base_query, date_from, date_to):
    params = []
    query = base_query
    if date_from:
        query += " AND DATE(publish_date) >= ? "
        params.append(date_from)
    if date_to:
        query += " AND DATE(publish_date) <= ? "
        params.append(date_to)
    query += " ORDER BY fetch_timestamp DESC"
    return query, params

@app.route('/')
def index():
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    # --- [MODIFICATION START] ---
    # யூசர் தேதியைத் தேர்வு செய்யவில்லை என்றால், 
    # தானாகவே கடந்த 2 நாட்கள் (நேற்று + இன்று) செய்திகளை மட்டும் காட்டவும்.
    if not date_from and not date_to:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        # நேற்றைய தேதியை 'YYYY-MM-DD' பார்மட்டில் date_from ஆக செட் செய்கிறோம்
        date_from = yesterday.strftime('%Y-%m-%d')
    # --- [MODIFICATION END] ---

    query, params = build_date_query(
        "SELECT id, title, summary, text, original_url, category, publish_date, is_processed FROM articles WHERE is_processed = 0",
        date_from, date_to
    )
    articles = get_articles_from_db(query, params)
    
    # render_template-க்கு date_from-ஐ அனுப்புவதால், ஃபில்டர் பாக்ஸில் அந்தத் தேதி தெரியும்.
    return render_template('index.html', articles=articles, date_from=date_from, date_to=date_to)

@app.route('/unprocessed')
def unprocessed_page():
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    query, params = build_date_query(
        "SELECT id, title, summary, text, original_url, category, publish_date FROM articles WHERE is_processed = 0",
        date_from, date_to
    )
    articles = get_articles_from_db(query, params)
    return render_template('unprocessed.html', articles=articles, date_from=date_from, date_to=date_to)

@app.route('/processed')
def processed_page():
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    query, params = build_date_query(
        "SELECT id, ai_title, ai_content, original_url, publish_date, ai_generated_audio_path, ai_generated_image_path, ai_generated_video_path FROM articles WHERE is_processed = 1", 
        date_from, date_to
    )
    articles = get_articles_from_db(query, params)
    return render_template('processed.html', articles=articles, date_from=date_from, date_to=date_to)

@app.route('/category/<string:category_name>')
def category_page(category_name):
    if category_name not in CATEGORIES:
        return "Category not found", 404
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    base_query = "SELECT id, title, summary, text, original_url, publish_date FROM articles WHERE category = ? AND is_processed = 0"
    params = [category_name]
    
    if date_from:
        base_query += " AND DATE(publish_date) >= ? "
        params.append(date_from)
    if date_to:
        base_query += " AND DATE(publish_date) <= ? "
        params.append(date_to)
        
    base_query += " ORDER BY fetch_timestamp DESC LIMIT 50"
    old_articles = get_articles_from_db(base_query, params)
    
    return render_template('category.html', old_articles=old_articles, category_name=category_name, date_from=date_from, date_to=date_to)

@app.route('/search')
def search_page():
    query = request.args.get('query', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    if not query: return "Please enter a search term.", 400
    return render_template('search.html', query=query, date_from=date_from, date_to=date_to)


# --- API Routes ------------------------------------------

@app.route('/api/fetch-category/<string:category_name>')
def api_fetch_category(category_name):
    if category_name not in CATEGORIES: return jsonify({"error": "Category not found"}), 404
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    offset = request.args.get('offset', type=int) 
    
    try:
        newly_fetched_articles = asyncio.run(fetch_and_parse_news(
            category_name, 
            category_name,
            date_from=date_from,
            date_to=date_to,
            offset=offset 
        ))
        return jsonify(newly_fetched_articles)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/search-and-fetch')
def api_search_and_fetch():
    query = request.args.get('query', '')
    if not query: return jsonify({"error": "No query provided"}), 400
    
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    offset = request.args.get('offset', type=int) 
    
    try:
        newly_fetched_articles = asyncio.run(fetch_and_parse_news(
            query, 
            "Search",
            date_from=date_from,
            date_to=date_to,
            offset=offset 
        ))
        return jsonify(newly_fetched_articles)
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- AI Writer: Returns STATIC IMAGE ---
@app.route('/api/ai-writer', methods=['POST'])
def api_ai_writer():
    if not gemini_model or not gemini_image_model: 
        return jsonify({"error": "Gemini AI models are not configured."}), 500

    data = request.json
    article_id = data.get('article_id')
    title = data.get('title')
    text = data.get('text')
    target_lang = data.get('target_lang', 'en')

    if not article_id or not title or not text:
        return jsonify({"error": "Missing article_id, title, or text"}), 400
        
    lang_name = LANGUAGES.get(target_lang, 'English')

    try:
        # --- 1. Generate Text (Summary) ---
        prompt_template = f"""
        Act as a {lang_name} journalist. Based on the following news article, write a short, layman-readable summary in {lang_name}, under 250 words.
        
        You MUST format the output *only* with the following tags, without any markdown `**`:
        
        @@TITLE_START@@
        (Your {lang_name} title here)
        @@TITLE_END@@
        
        @@CONTENT_START@@
        (Your {lang_name} summary here. Use newlines for paragraphs.)
        @@CONTENT_END@@
        
        ARTICLE:
        TITLE: {title}
        TEXT: {text[:2500]}
        
        YOUR {lang_name.upper()} SUMMARY:
        """
        
        response = gemini_model.generate_content(prompt_template)
        ai_raw_response_text = response.text

        ai_title = "AI Title Error" 
        ai_content_raw = ai_raw_response_text
        ai_content_html = ai_raw_response_text
        
        try:
            ai_title = ai_raw_response_text.split("@@TITLE_START@@")[1].split("@@TITLE_END@@")[0].strip()
            ai_content_raw = ai_raw_response_text.split("@@CONTENT_START@@")[1].split("@@CONTENT_END@@")[0].strip()
            ai_content_html = ai_content_raw.replace('\n', '<br>\n')
        except Exception as e:
            logging.error(f"Failed to parse AI response: {e}. Response: {ai_raw_response_text}")
            ai_title = title 
            ai_content_html = ai_raw_response_text.replace('\n', '<br>\n')

        # --- 2. Generate STATIC Image ---
        db_image_path = None
        if gemini_image_model:
            try:
                logging.info(f"Generating image for article {article_id}")
                image_prompt = f"""
Generate a high-quality, photorealistic news-style image.
DO NOT include any text, letters, or words in the image.
The image must be relevant to the following news story:
Headline: {title}
Summary: {ai_content_raw[:400]}
"""
                image_response = gemini_image_model.generate_content(image_prompt)
                image_bytes = None
                for part in image_response.parts:
                    if part.inline_data:
                        image_bytes = part.inline_data.data
                        break
                
                if image_bytes:
                    image_filename = f"article_img_{article_id}.png"
                    image_save_path = IMAGE_OUTPUT_DIR / image_filename
                    with open(image_save_path, 'wb') as f: f.write(image_bytes)
                    db_image_path = f"static/images/{image_filename}"
                else:
                    logging.warning(f"No image data returned for article {article_id}")

            except Exception as e:
                logging.error(f"Failed to generate image: {e}")

        # --- 3. Update Database ---
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE articles 
               SET ai_title = ?, 
                   ai_content = ?, 
                   is_processed = 1, 
                   ai_generated_content = ?,
                   ai_generated_image_path = ? 
               WHERE id = ?""",
            (ai_title, ai_content_html, ai_raw_response_text, db_image_path, article_id)
        )
        conn.commit()
        conn.close()
        
        if target_lang == 'en': title_label, content_label = "Title", "Text Content"
        elif target_lang == 'ta': title_label, content_label = "தலைப்பு செய்தி", "செய்தி உள்ளடக்கம்"
        else: title_label, content_label = "Title", "Content"

        ai_text_for_js = f"**{title_label}**\n**{ai_title}**\n\n**{content_label}**\n{ai_content_raw}"

        return jsonify({
            "ai_text": ai_text_for_js,
            "image_path": db_image_path 
        })

    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": str(e)}), 500

# --- API: Generate Video (GIF + Update DB) ---
@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    data = request.json
    article_id = data.get('article_id')
    
    if not article_id:
        return jsonify({"error": "Missing article_id"}), 400

    try:
        # 1. Fetch the static image path from DB
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT ai_generated_image_path FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            conn.close()
            return jsonify({"error": "No static image found to generate video from."}), 404
            
        static_image_path = row[0] 
        
        # 2. Check if file exists on disk
        file_path = Path(static_image_path)
        if not file_path.exists():
            conn.close()
            return jsonify({"error": "Image file missing on disk"}), 404
            
        # 3. Generate GIF using existing image
        gif_db_path = add_watermark_and_create_gif(file_path, file_path.name)
        
        if not gif_db_path:
             conn.close()
             return jsonify({"error": "Failed to create GIF"}), 500
             
        # 4. Update Database with Video Path
        cursor.execute("UPDATE articles SET ai_generated_video_path = ? WHERE id = ?", (gif_db_path, article_id))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "video_path": gif_db_path})

    except Exception as e:
        logging.error(f"Error generating video for {article_id}: {e}")
        return jsonify({"error": str(e)}), 500

# --- [UPDATED] API: Generate Voice (ElevenLabs -> Fallback Google TTS with Voice Switching) ---
@app.route('/api/generate-voice', methods=['POST'])
def api_generate_voice():
    if not gemini_model:
        return jsonify({"error": "Gemini Model not configured."}), 500

    data = request.json
    article_id = data.get('article_id')
    ai_summary_text = data.get('ai_text')
    target_lang = data.get('target_lang', 'en')
    voice_id = data.get('voice_id') # This comes from the UI dropdown

    if not all([article_id, ai_summary_text, target_lang]):
        return jsonify({"error": "Missing required parameters"}), 400

    lang_name = LANGUAGES.get(target_lang, 'English')

    try:
        # 1. Generate concise text for speech using Gemini
        deep_summary_prompt = f"""
        Act as a {lang_name} news reader. 
        The following is a news article summary. 
        Your task is to summarize this summary *even further* into a very concise, layman-readable paragraph in {lang_name} (approximately 100 words).
        This summary will be used for a text-to-speech audio clip.
        Start directly with the news in {lang_name}.
        
        ARTICLE SUMMARY:
        {ai_summary_text}

        YOUR CONCISE 100-WORD {lang_name.upper()} AUDIO SCRIPT:
        """
        
        response = gemini_model.generate_content(deep_summary_prompt)
        deep_summary_text = response.text
        
        audio_filename = f"article_{article_id}.mp3"
        audio_save_path = ELEVENLABS_AUDIO_DIR / audio_filename
        
        audio_generated = False
        error_message = ""

        # 2. Try ElevenLabs First
        if elevenlabs_client and voice_id:
            try:
                logging.info(f"Attempting ElevenLabs generation for article {article_id}...")
                audio = elevenlabs_client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=deep_summary_text,
                    model_id="eleven_multilingual_v2"
                )
                with open(audio_save_path, 'wb') as f:
                    for chunk in audio:
                        f.write(chunk)
                audio_generated = True
                logging.info("ElevenLabs generation successful.")
            except Exception as e:
                logging.error(f"ElevenLabs failed: {e}")
                error_message = str(e)
                audio_generated = False
        else:
             logging.warning("ElevenLabs client not configured or missing Voice ID.")

        # 3. Fallback to Google Cloud TTS if ElevenLabs failed
        if not audio_generated:
            if google_tts_client:
                logging.info(f"Switching to Google Cloud TTS for article {article_id}...")
                try:
                    # Determine Gender based on the selected voice ID from existing VOICES dict
                    # Default to Female
                    is_male_voice = False
                    selected_voice_name = "Rachel" # Default
                    
                    # Reverse lookup to find name from ID
                    for name, v_id in VOICES.items():
                        if v_id == voice_id:
                            selected_voice_name = name
                            break
                    
                    if selected_voice_name in MALE_VOICE_NAMES:
                        is_male_voice = True
                        
                    # Map language codes and Gender
                    if target_lang == 'ta':
                        language_code = "ta-IN"
                        if is_male_voice:
                            name = "ta-IN-Wavenet-C" # Tamil Male Voice
                        else:
                            name = "ta-IN-Wavenet-D" # Tamil Female Voice (Requested Default)
                            
                    elif target_lang == 'hi':
                         language_code = "hi-IN"
                         if is_male_voice:
                             name = "hi-IN-Neural2-B" # Hindi Male
                         else:
                             name = "hi-IN-Neural2-A" # Hindi Female
                    else:
                        language_code = "en-US"
                        if is_male_voice:
                            name = "en-US-Journey-D" # English Male
                        else:
                            name = "en-US-Journey-F" # English Female

                    input_text = texttospeech.SynthesisInput(text=deep_summary_text)
                    
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=language_code,
                        name=name
                    )
                    
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3
                    )

                    response = google_tts_client.synthesize_speech(
                        input=input_text, voice=voice, audio_config=audio_config
                    )

                    with open(audio_save_path, "wb") as out:
                        out.write(response.audio_content)
                        
                    audio_generated = True
                    logging.info(f"Google Cloud TTS generation successful using voice: {name}")
                    
                except Exception as google_e:
                    logging.error(f"Google TTS also failed: {google_e}")
                    return jsonify({"error": f"Both ElevenLabs ({error_message}) and Google TTS ({str(google_e)}) failed."}), 500
            else:
                logging.error("Google TTS client not available for fallback.")
                return jsonify({"error": f"ElevenLabs failed: {error_message}. Google TTS not configured."}), 500

        # 4. Save path to DB if successful
        if audio_generated:
            db_path = f"static/audio/{audio_filename}"
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE articles SET ai_generated_audio_path = ? WHERE id = ?",
                (db_path, article_id)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                "success": True, 
                "audio_path": db_path, 
                "deep_summary_text": deep_summary_text
            })
        else:
            return jsonify({"error": "Unknown error during voice generation"}), 500

    except Exception as e:
        logging.error(f"Error in voice generation for {article_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    setup_database(DB_FILE)
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(fetch_breaking_news_job, 'interval', minutes=30, id='breaking_news_india')
    scheduler.start()
    logging.info("--- Background scheduler started. ---")
    app.run(port=5000, debug=True, use_reloader=False)
