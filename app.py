import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from PIL import Image
import json
import re
import time
from urllib.parse import urljoin, urlparse

# --- 1. PAGE CONFIG & CYBERPUNK CSS ---
st.set_page_config(
    page_title="GOD-MODE: OMNI-TOOL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject "Hacker" Vibe CSS
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #00FF94; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0D1117 !important; color: #E6EDF3 !important; border: 1px solid #30363D;
    }
    .stButton button { background-color: #238636; color: white; border: none; font-weight: bold; }
    .stButton button:hover { background-color: #2EA043; }
    h1, h2, h3 { font-family: 'Courier New', monospace; color: #E6EDF3; }
    .metric-container { background-color: #0D1117; border: 1px solid #30363D; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---

def generate_with_fallback(user_model_name, prompt, image=None):
    """Safely calls the API with error handling."""
    try:
        model = genai.GenerativeModel(user_model_name)
        if image:
            return model.generate_content([prompt, image])
        return model.generate_content(prompt)
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            st.warning(f"⚠️ Model '{user_model_name}' not found. Switching to backup 'gemini-pro'...")
            try:
                backup_model = genai.GenerativeModel("gemini-pro")
                if image: return backup_model.generate_content([prompt, image])
                return backup_model.generate_content(prompt)
            except Exception as e2:
                st.error(f"❌ Backup failed. Check API Key. Error: {e2}")
                return None
        else:
            st.error(f"❌ Error: {e}")
            return None

def extract_assets(soup, url):
    """Finds Fonts, Icons, and Images."""
    assets = {"fonts": [], "icons": [], "images": []}
    
    # Fonts
    for link in soup.find_all('link', href=True):
        href = link['href']
        if 'fonts.googleapis.com' in href or href.endswith('.woff') or href.endswith('.woff2'):
            assets['fonts'].append(urljoin(url, href))
            
    # Icons
    for link in soup.find_all('link', rel=True):
        rel_val = link['rel']
        if isinstance(rel_val, list):
            if 'icon' in rel_val: assets['icons'].append(urljoin(url, link.get('href', '')))
        elif 'icon' in rel_val:
             assets['icons'].append(urljoin(url, link.get('href', '')))
             
    # Images
    for img in soup.find_all('img', src=True):
        src = img['src']
        full_src = urljoin(url, src)
        if 'logo' in src.lower() or src.endswith('.svg'):
            assets['icons'].append(full_src)
        else:
            assets['images'].append(full_src)
    return assets

def recursive_crawl(start_url, max_pages=5):
    """Crawls the site, counts elements, and builds a map."""
    visited = set()
    queue = [start_url]
    combined_text = ""
    site_structure = {} 
    all_assets = {"fonts": set(), "icons": set(), "images": set()}
    
    global_stats = {
        "pages": 0, "buttons": 0, "links": 0, 
        "images": 0, "inputs": 0, "words": 0
    }
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_domain = urlparse(start_url).netloc
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    count = 0
    while queue and count < max_pages:
        progress_bar.progress(min(int((count / max_pages) * 100), 99))
        
        url = queue.pop(0)
        if url in visited: continue
        
        try:
            status_text.markdown(f"**🕷️ Scanning Page {count+1}/{max_pages}:** `{url}`")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200: continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Count Elements
            global_stats["buttons"] += len(soup.find_all('button'))
            global_stats["links"] += len(soup.find_all('a'))
            global_stats["images"] += len(soup.find_all('img'))
            global_stats["inputs"] += len(soup.find_all('input'))
            text_content = soup.get_text(separator=' ', strip=True)
            global_stats["words"] += len(text_content.split())
            global_stats["pages"] += 1
            
            # Map Structure
            scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
            title = soup.title.string if soup.title else "No Title"
            site_structure[url] = {"title": title, "scripts": scripts[:3]}
            
            # Hunt Assets
            page_assets = extract_assets(soup, url)
            all_assets['fonts'].update(page_assets['fonts'])
            all_assets['icons'].update(page_assets['icons'])
            
            combined_text += f"\n\n--- PAGE: {title} ({url}) ---\nDETECTED SCRIPTS: {scripts[:5]}\nCONTENT: {text_content[:4000]}"
            
            visited.add(url)
            count += 1
            
            # Find Next Links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == base_domain and full_url not in visited and full_url not in queue:
                    queue.append(full_url)
            
            time.sleep(0.3)
            
        except Exception as e:
            pass
            
    progress_bar.progress(100)
    status_text.success(f"✅ Mission Complete! Scanned {count} pages.")
    
    final_assets = {k: list(v) for k, v in all_assets.items()}
    return combined_text, site_structure, final_assets, global_stats

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ SYSTEM CONTROL")
    api_key = st.text_input("API KEY", type="password")
    st.divider()
    model_name = st.selectbox("MODEL", ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"])
    st.caption("Use 'gemini-2.0-flash-exp' for Vision/Images.")
    
    if st.button("🐞 SYSTEM CHECK"):
        if not api_key:
            st.error("ACCESS DENIED: NO KEY")
        else:
            try:
                genai.configure(api_key=api_key)
                st.write("✅ **ACCESS GRANTED:**")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name.replace("models/", ""))
            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. MAIN APP ---
st.title("⚡ GOD-MODE: OMNI-TOOL")
st.markdown("---")

if not api_key:
    st.warning("🔒 ENTER API KEY TO UNLOCK")
    st.stop()

genai.configure(api_key=api_key)

tab1, tab2, tab3 = st.tabs(["✨ PROMPT ENGINEER", "🕷️ DEEP CRAWLER", "👁️ VISION REPLICATOR"])

# --- TAB 1: PROMPT ENHANCER ---
with tab1:
    st.header("✨ Active Reasoning Engine")
    mode = st.selectbox("STRATEGY", ["✨ Auto-Detect", "⚡ Vibe Coder", "CO-STAR", "Chain of Thought"])
    raw_prompt = st.text_area("INPUT PROMPT", height=150)
    if st.button("🚀 ENHANCE"):
        with st.spinner("PROCESSING..."):
            res = generate_with_fallback(model_name, f"Enhance this prompt using {mode}: {raw_prompt}")
            if res: st.code(res.text, language='markdown')

# --- TAB 2: CRAWL & CHAT ---
with tab2:
    st.header("🕷️ Deep Net Scanner")
    
    # Initialize Session State
    if 'messages' not in st.session_state: st.session_state.messages = []
    if 'knowledge_base' not in st.session_state: st.session_state.knowledge_base = ""
    if 'scanned_url' not in st.session_state: st.session_state.scanned_url = ""
    if 'global_stats' not in st.session_state: st.session_state.global_stats = {}

    c1, c2 = st.columns([3, 1])
    with c1:
        url = st.text_input("TARGET URL", placeholder="https://example.com")
    with c2:
        crawl_scope = st.selectbox(
            "SCOPE", 
            ["Home Page Only (1 Page)", "Quick Scan (5 Pages)", "Deep Scan (20 Pages)", "Massive Scan (50 Pages)"]
        )

    # Convert Dropdown to Number
    page_limit = 1
    if "Quick" in crawl_scope: page_limit = 5
    if "Deep" in crawl_scope: page_limit = 20
    if "Massive" in crawl_scope: page_limit = 50
    
    if st.button("🕷️ INITIATE SCAN", type="primary"):
        if not url:
            st.warning("URL REQUIRED")
        else:
            full_text, structure, assets, stats = recursive_crawl(url, max_pages=page_limit)
            
            st.session_state.scanned_url = url
            st.session_state.global_stats = stats
            st.session_state.knowledge_base = f"""
            SOURCE URL: {url}
            STATS: {json.dumps(stats)}
            SITE MAP: {json.dumps(structure)}
            ASSETS FOUND: {json.dumps(assets)}
            RAW CONTENT & SCRIPTS:
            {full_text}
            """
            
            st.session_state.messages = [{"role": "assistant", "content": f"**SCAN COMPLETE.** Analyzed {stats['pages']} pages. Found {stats['buttons']} buttons. Ready for queries."}]
            st.rerun()

    # Results Dashboard
    if st.session_state.knowledge_base:
        st.divider()
        stats = st.session_state.global_stats
        if stats:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("PAGES", stats.get('pages', 0))
            k2.metric("LINKS", stats.get('links', 0))
            k3.metric("BUTTONS", stats.get('buttons', 0))
            k4.metric("IMAGES", stats.get('images', 0))

        st.divider()
        st.subheader(f"💬 DATA LINK: {st.session_state.scanned_url}")
        
        # Chat Interface
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_input := st.chat_input("QUERY DATABASE..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("COMPUTING..."):
                    chat_prompt = f"""
                    You are a Senior Technical Architect.
                    KNOWLEDGE BASE: {st.session_state.knowledge_base[:30000]}
                    USER QUERY: "{user_input}"
                    INSTRUCTIONS: Answer based ONLY on the data. Be technical.
                    """
                    response = generate_with_fallback(model_name, chat_prompt)
                    if response:
                        ai_reply = response.text
                        st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        
        with st.expander("📦 RAW DATA EXPORT"):
            st.download_button("DOWNLOAD JSON", st.session_state.knowledge_base, file_name="scan_data.json")

# --- TAB 3: VISION REPLICATOR ---
with tab3:
    st.header("👁️ Vision Replicator")
    st.info("Upload a screenshot to replicate the design pixel-perfectly.")
    
    uploaded_file = st.file_uploader("UPLOAD INTERFACE IMAGE", type=['png', 'jpg', 'jpeg'])
    
    col_a, col_b = st.columns(2)
    with col_a: stack = st.selectbox("TECH STACK", ["Next.js + Tailwind", "React + Three.js", "HTML/CSS"])
    with col_b: vibe = st.text_input("VIBE", placeholder="Cyberpunk, Clean")

    if st.button("🧬 GENERATE REPLICA CODE"):
        if not uploaded_file:
            st.warning("UPLOAD REQUIRED")
        else:
            with st.spinner("ANALYZING PIXELS..."):
                img = Image.open(uploaded_file)
                prompt = f"Act as a Senior Frontend Dev. Write a system prompt to build this exact UI using {stack}. Vibe: {vibe}."
                res = generate_with_fallback(model_name, prompt, image=img)
                if res: st.code(res.text, language='markdown')
