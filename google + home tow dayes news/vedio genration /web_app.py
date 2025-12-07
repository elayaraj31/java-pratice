import json
import asyncio
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import os
import io

# --- Image Processing Libraries ---
from PIL import Image, ImageSequence, ImageEnhance 

# --- MoviePy for Video Editing (NEW) ---
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips

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

# --- Google Cloud TTS Import ---
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

# --- Google Cloud TTS Configuration ---
google_tts_client = None
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    key_file_path = os.path.join(base_dir, "key.json")
    if os.path.exists(key_file_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
        google_tts_client = texttospeech.TextToSpeechClient()
        logging.info(f"Google Cloud TTS client configured using: {key_file_path}")
    elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        google_tts_client = texttospeech.TextToSpeechClient()
        logging.info("Google Cloud TTS client configured from Environment Variable.")
    else:
        logging.warning(f"!!! key.json not found. Google TTS will NOT work. !!!")
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

VOICES = {
    "Rachel": "pNInz6obpgDQGcFmaJgB",   # Female
    "Bharati": "C2RGMrNBTZaNfddRPeRH",  # Female
    "Adam": "pNInz6obpgDQGcFmaJgB",      # Male
    "Charlie": "IKne3meq5aSn9XLyUdCD",  # Male
    "Sia": "XwkIUwRxNu9PpezCu4Vg",       # Female
    "Matilda": "NihRgaLj2HWAjvZ5XNxl",  # Female
    "Nila": "C2RGMrNBTZaNfddRPeRH",      # Female
    "Alice": "Xb7hH8MSUJpSbSDYk0k2"      # Female
}

MALE_VOICE_NAMES = {"Adam", "Charlie", "Brian", "Daniel"}
CATEGORIES = ['India', 'World', 'Business', 'Technology', 'Entertainment', 'Sports', 'Science', 'Health', 'Agriculture']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        return str(save_path) # Return Absolute/Relative path string

    except Exception as e:
        logging.error(f"Error creating GIF/Watermark: {e}")
        return None

# --- NEW Helper: Combine GIF + Audio to MP4 ---
def create_mp4_video(gif_path, audio_path, output_filename):
    try:
        # Load the GIF as a VideoClip
        video_clip = VideoFileClip(gif_path)
        
        # Load the Audio
        audio_clip = AudioFileClip(audio_path)
        
        # Loop the GIF to match the Audio duration
        final_video = video_clip.loop(duration=audio_clip.duration)
        
        # Set the audio to the video
        final_video = final_video.set_audio(audio_clip)
        
        # Write the result to a file
        output_path = IMAGE_OUTPUT_DIR / output_filename
        final_video.write_videofile(str(output_path), codec='libx264', audio_codec='aac', fps=24, verbose=False, logger=None)
        
        return f"static/images/{output_filename}"
    
    except Exception as e:
        logging.error(f"Error converting to MP4: {e}")
        return None
    finally:
        # Close clips to release resources
        try:
            if 'video_clip' in locals(): video_clip.close()
            if 'audio_clip' in locals(): audio_clip.close()
            if 'final_video' in locals(): final_video.close()
        except: pass


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
    conn.commit()
    conn.close()

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

# --- Scraper Functions (Unchanged) ---
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
    if date_from and len(date_from) >= 8: full_search_term += f" after:{date_from}"
    if date_to and len(date_to) >= 8: full_search_term += f" before:{date_to}"
            
    logging.info(f"--- Scrape Job: '{category_name}' (Search: '{full_search_term}') ---")
    
    googlenews = GoogleNews(lang='en')
    googlenews.search(full_search_term) 
    start_page = (offset // 10) + 1 
    if start_page > 1: googlenews.getpage(start_page)
        
    num_pages_to_fetch = start_page + ((num_articles + 9) // 10)
    all_results = googlenews.results()
    if num_pages_to_fetch > start_page:
        for page in range(start_page + 1, num_pages_to_fetch + 1):
            googlenews.getpage(page)
            page_results = googlenews.results()
            if not page_results: break
            all_results.extend(page_results)
    
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0'
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
    filtered_articles = [a for a in valid_articles if a.get("text_length", 0) > MIN_TEXT_LENGTH and a.get("title")]
    
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
            d = dict(row)
            d['publish_date'] = format_date_filter(d['publish_date'])
            final_articles.append(d)
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
    return dict(CATEGORIES=CATEGORIES, LANGUAGES=LANGUAGES, VOICES=VOICES, STATES=STATES, article_count=count, CATEGORY_ICONS={})

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
    
    # --- [CHANGED] Default to Last 2 Days ---
    if not date_from and not date_to:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        date_from = yesterday.strftime('%Y-%m-%d')
    # ----------------------------------------

    query, params = build_date_query(
        "SELECT id, title, summary, text, original_url, category, publish_date, is_processed FROM articles WHERE is_processed = 0",
        date_from, date_to
    )
    articles = get_articles_from_db(query, params)
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
    if category_name not in CATEGORIES: return "Category not found", 404
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    return render_template('category.html', category_name=category_name, date_from=date_from, date_to=date_to)

@app.route('/search')
def search_page():
    query = request.args.get('query', '')
    return render_template('search.html', query=query)

# --- API Routes ------------------------------------------

@app.route('/api/fetch-category/<string:category_name>')
def api_fetch_category(category_name):
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    offset = request.args.get('offset', type=int) 
    try:
        newly_fetched = asyncio.run(fetch_and_parse_news(category_name, category_name, date_from, date_to, offset))
        return jsonify(newly_fetched)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/search-and-fetch')
def api_search_and_fetch():
    query = request.args.get('query', '')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    offset = request.args.get('offset', type=int) 
    try:
        newly_fetched = asyncio.run(fetch_and_parse_news(query, "Search", date_from, date_to, offset))
        return jsonify(newly_fetched)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/ai-writer', methods=['POST'])
def api_ai_writer():
    if not gemini_model or not gemini_image_model: return jsonify({"error": "Gemini AI models are not configured."}), 500
    data = request.json
    article_id = data.get('article_id')
    title = data.get('title')
    text = data.get('text')
    target_lang = data.get('target_lang', 'en')

    lang_name = LANGUAGES.get(target_lang, 'English')
    try:
        prompt_template = f"""
        Act as a {lang_name} journalist. Write a short summary in {lang_name}, under 250 words.
        Format:
        @@TITLE_START@@(Title)@@TITLE_END@@
        @@CONTENT_START@@(Content)@@CONTENT_END@@
        ARTICLE: {title} {text[:2500]}
        """
        response = gemini_model.generate_content(prompt_template)
        ai_raw = response.text
        try:
            ai_title = ai_raw.split("@@TITLE_START@@")[1].split("@@TITLE_END@@")[0].strip()
            ai_content = ai_raw.split("@@CONTENT_START@@")[1].split("@@CONTENT_END@@")[0].strip().replace('\n', '<br>\n')
        except:
            ai_title = title; ai_content = ai_raw.replace('\n', '<br>\n')

        # Generate STATIC Image
        db_image_path = None
        try:
            image_prompt = f"High-quality news image for: {title}. No text."
            image_response = gemini_image_model.generate_content(image_prompt)
            if image_response.parts[0].inline_data:
                image_bytes = image_response.parts[0].inline_data.data
                image_filename = f"article_img_{article_id}.png"
                image_save_path = IMAGE_OUTPUT_DIR / image_filename
                with open(image_save_path, 'wb') as f: f.write(image_bytes)
                db_image_path = f"static/images/{image_filename}"
        except Exception as e: logging.error(f"Image gen failed: {e}")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE articles SET ai_title=?, ai_content=?, is_processed=1, ai_generated_content=?, ai_generated_image_path=? WHERE id=?", (ai_title, ai_content, ai_raw, db_image_path, article_id))
        conn.commit()
        conn.close()

        ai_text_for_js = f"**{ai_title}**\n\n{ai_content.replace('<br>', '')}"
        return jsonify({"ai_text": ai_text_for_js, "image_path": db_image_path})
    except Exception as e: return jsonify({"error": str(e)}), 500


# --- [UPDATED] API: Generate Video (MP4) ---
@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    data = request.json
    article_id = data.get('article_id')
    
    if not article_id: return jsonify({"error": "Missing article_id"}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT ai_generated_image_path, ai_generated_audio_path FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Article not found"}), 404

        static_image_path = row[0]
        audio_path = row[1]
        
        if not static_image_path or not os.path.exists(static_image_path):
            conn.close()
            return jsonify({"error": "Image not found. Please regenerate AI text/image."}), 404
        
        if not audio_path or not os.path.exists(audio_path):
            conn.close()
            return jsonify({"error": "Audio not found. Please generate voice first."}), 404

        # 1. Create GIF (Zoom Effect)
        gif_abs_path = add_watermark_and_create_gif(Path(static_image_path), Path(static_image_path).name)
        
        if not gif_abs_path:
             conn.close()
             return jsonify({"error": "Failed to create intermediate GIF"}), 500
        
        # 2. Combine GIF + Audio -> MP4
        mp4_filename = f"video_{article_id}.mp4"
        mp4_db_path = create_mp4_video(gif_abs_path, audio_path, mp4_filename)
        
        if not mp4_db_path:
             conn.close()
             return jsonify({"error": "Failed to combine Video and Audio"}), 500

        # 3. Update DB
        cursor.execute("UPDATE articles SET ai_generated_video_path = ? WHERE id = ?", (mp4_db_path, article_id))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "video_path": mp4_db_path})

    except Exception as e:
        logging.error(f"Error generating video for {article_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-voice', methods=['POST'])
def api_generate_voice():
    if not gemini_model: return jsonify({"error": "Gemini Model not configured."}), 500
    data = request.json
    article_id = data.get('article_id')
    ai_summary_text = data.get('ai_text')
    target_lang = data.get('target_lang', 'en')
    voice_id = data.get('voice_id')

    try:
        # 1. Generate Script
        response = gemini_model.generate_content(f"Summarize this for news audio in {target_lang} (100 words): {ai_summary_text}")
        deep_summary_text = response.text
        
        audio_filename = f"article_{article_id}.mp3"
        audio_save_path = ELEVENLABS_AUDIO_DIR / audio_filename
        audio_generated = False
        error_msg = ""

        # 2. ElevenLabs
        if elevenlabs_client and voice_id:
            try:
                audio = elevenlabs_client.text_to_speech.convert(voice_id=voice_id, text=deep_summary_text, model_id="eleven_multilingual_v2")
                with open(audio_save_path, 'wb') as f: 
                    for chunk in audio: f.write(chunk)
                audio_generated = True
            except Exception as e: error_msg = str(e)

        # 3. Google TTS Fallback
        if not audio_generated and google_tts_client:
             try:
                lang_code = "ta-IN" if target_lang == 'ta' else "en-US"
                # Simple logic for voice selection based on 'Male' names in VOICES dict could be added here
                name = "ta-IN-Wavenet-D" if target_lang == 'ta' else "en-US-Journey-F" 
                
                input_text = texttospeech.SynthesisInput(text=deep_summary_text)
                voice = texttospeech.VoiceSelectionParams(language_code=lang_code, name=name)
                audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                response = google_tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
                with open(audio_save_path, "wb") as out: out.write(response.audio_content)
                audio_generated = True
             except Exception as e: error_msg += f" | GoogleTTS: {e}"

        if audio_generated:
            db_path = f"static/audio/{audio_filename}"
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE articles SET ai_generated_audio_path = ? WHERE id = ?", (db_path, article_id))
            conn.commit()
            conn.close()
            return jsonify({"success": True, "audio_path": db_path, "deep_summary_text": deep_summary_text})
        else:
            return jsonify({"error": f"Voice generation failed. {error_msg}"}), 500

    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    setup_database(DB_FILE)
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(fetch_breaking_news_job, 'interval', minutes=30)
    scheduler.start()
    app.run(port=5000, debug=True, use_reloader=False)
