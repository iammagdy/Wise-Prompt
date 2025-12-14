import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urljoin, urlparse

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="God-Mode AI Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER: SELF-HEALING AI ---
def generate_with_fallback(user_model_name, prompt):
    try:
        model = genai.GenerativeModel(user_model_name)
        return model.generate_content(prompt)
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            st.warning(f"⚠️ Model '{user_model_name}' not found. Switching to backup 'gemini-pro'...")
            try:
                backup_model = genai.GenerativeModel("gemini-pro")
                return backup_model.generate_content(prompt)
            except Exception as e2:
                st.error(f"❌ Backup failed. Check API Key. Error: {e2}")
                return None
        else:
            st.error(f"❌ Error: {e}")
            return None

# --- HELPER: ASSET HUNTER ---
def extract_assets(soup, url):
    """
    Finds Fonts, Icons, and Images to help the Chat AI answer questions about design.
    """
    assets = {
        "fonts": [],
        "icons": [],
        "images": []
    }
    # 1. Fonts
    for link in soup.find_all('link', href=True):
        href = link['href']
        if 'fonts.googleapis.com' in href or href.endswith('.woff') or href.endswith('.woff2'):
            assets['fonts'].append(urljoin(url, href))
    # 2. Icons
    for link in soup.find_all('link', rel=True):
        if 'icon' in link['rel']:
            assets['icons'].append(urljoin(url, link.get('href', '')))
    # 3. Images (Logos/SVGs)
    for img in soup.find_all('img', src=True):
        src = img['src']
        full_src = urljoin(url, src)
        if 'logo' in src.lower() or src.endswith('.svg'):
            assets['icons'].append(full_src)
        else:
            assets['images'].append(full_src)
    return assets

# --- HELPER: RECURSIVE CRAWLER V3 (With Counters) ---
def recursive_crawl(start_url, max_pages=5):
    visited = set()
    queue = [start_url]
    combined_text = ""
    site_structure = {} 
    all_assets = {"fonts": set(), "icons": set(), "images": set()}
    
    # NEW: Global Counters
    global_stats = {
        "pages": 0,
        "buttons": 0,
        "links": 0,
        "images": 0,
        "inputs": 0,
        "words": 0
    }
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    base_domain = urlparse(start_url).netloc
    
    # UI: Progress Bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    count = 0
    while queue and count < max_pages:
        # Update Progress
        progress = int((count / max_pages) * 100)
        progress_bar.progress(progress)
        
        url = queue.pop(0)
        if url in visited: continue
        
        try:
            status_text.markdown(f"**🕷️ Scanning Page {count+1}/{max_pages}:** `{url}`")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200: continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- 1. COUNT ELEMENTS (The New Feature) ---
            global_stats["buttons"] += len(soup.find_all('button'))
            global_stats["links"] += len(soup.find_all('a'))
            global_stats["images"] += len(soup.find_all('img'))
            global_stats["inputs"] += len(soup.find_all('input'))
            text_content = soup.get_text(separator=' ', strip=True)
            global_stats["words"] += len(text_content.split())
            global_stats["pages"] += 1
            
            # --- 2. DATA EXTRACTION ---
            scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
            title = soup.title.string if soup.title else "No Title"
            
            # --- 3. SMART MAP ---
            site_structure[url] = {"title": title, "scripts": scripts[:3]}
            
            # --- 4. ASSETS ---
            page_assets = extract_assets(soup, url)
            all_assets['fonts'].update(page_assets['fonts'])
            all_assets['icons'].update(page_assets['icons'])
            
            combined_text += f"\n\n--- PAGE: {title} ({url}) ---\nDETECTED SCRIPTS: {scripts[:5]}\nCONTENT: {text_content[:4000]}"
            
            visited.add(url)
            count += 1
            
            # --- 5. QUEUE ---
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == base_domain and full_url not in visited and full_url not in queue:
                    queue.append(full_url)
            
            time.sleep(0.3)
            
        except Exception as e:
            st.warning(f"Skipped {url}: {e}")
            
    progress_bar.progress(100)
    status_text.success(f"✅ Mission Complete! Scanned {count} pages.")
    
    final_assets = {k: list(v) for k, v in all_assets.items()}
    return combined_text, site_structure, final_assets, global_stats

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Engine Room")
    api_key = st.text_input("🔑 Paste Gemini API Key:", type="password")
    st.divider()
    model_name = st.text_input("Model Name:", value="gemini-pro") 
    
    if st.button("🐞 Check My Available Models"):
        if not api_key:
            st.error("Paste API Key first!")
        else:
            try:
                genai.configure(api_key=api_key)
                st.write("✅ **Your Key supports:**")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name.replace("models/", ""))
            except Exception as e:
                st.error(f"Error: {e}")

# --- MAIN APP ---
st.title("⚡ God-Mode AI Suite")
st.markdown("Tab 1: Create Prompts | Tab 2: **Full Site Scanner & Chat**")

if not api_key:
    st.warning("⬅️ Waiting for API Key...")
    st.stop()

genai.configure(api_key=api_key)

tab1, tab2 = st.tabs(["✨ Prompt Enhancer", "🕷️ Crawl & Chat (Superpower)"])

# ==========================================
# TAB 1: PROMPT ENHANCER (Simplified)
# ==========================================
with tab1:
    st.header("✨ The Active Reasoning Engine")
    mode = st.selectbox("Strategy:", ["✨ Auto-Detect", "⚡ Vibe Coder", "CO-STAR", "Chain of Thought"])
    raw_prompt = st.text_area("Your Request:", height=150)
    if st.button("🚀 Enhance"):
        with st.spinner("Enhancing..."):
            res = generate_with_fallback(model_name, f"Enhance this prompt using {mode}: {raw_prompt}")
            if res: st.code(res.text, language='markdown')

# ==========================================
# TAB 2: CRAWL & CHAT (THE SUPERPOWER)
# ==========================================
with tab2:
    st.header("🕷️ Deep Scan & Chat")
    
    # State
    if 'messages' not in st.session_state: st.session_state.messages = []
    if 'knowledge_base' not in st.session_state: st.session_state.knowledge_base = ""
    if 'scanned_url' not in st.session_state: st.session_state.scanned_url = ""
    if 'global_stats' not in st.session_state: st.session_state.global_stats = {}

    # --- 1. CONFIGURATION ---
    c1, c2 = st.columns([3, 1])
    with c1:
        url = st.text_input("Target URL:", placeholder="https://example.com")
    with c2:
        # NEW: CRAWL SCOPE DROPDOWN
        crawl_scope = st.selectbox(
            "Scan Scope:", 
            ["Home Page Only (1 Page)", "Quick Scan (5 Pages)", "Deep Scan (20 Pages)", "Massive Scan (50 Pages)"]
        )

    # Convert Dropdown to Number
    page_limit = 1
    if "Quick" in crawl_scope: page_limit = 5
    if "Deep" in crawl_scope: page_limit = 20
    if "Massive" in crawl_scope: page_limit = 50
    
    if st.button("🕷️ Start Scan", type="primary"):
        if not url:
            st.warning("Need URL!")
        else:
            # RUN CRAWLER
            full_text, structure, assets, stats = recursive_crawl(url, max_pages=page_limit)
            
            # Save Data
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
            
            # Reset Chat
            st.session_state.messages = [{"role": "assistant", "content": f"I have scanned **{stats['pages']} pages** on {url}. I found {stats['buttons']} buttons and {stats['images']} images. Ask me anything!"}]
            st.rerun()

    # --- 2. RESULTS DASHBOARD ---
    if st.session_state.knowledge_base:
        st.divider()
        
        # STATS ROW
        stats = st.session_state.global_stats
        if stats:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Pages Scanned", stats.get('pages', 0))
            k2.metric("Total Links", stats.get('links', 0))
            k3.metric("Total Buttons", stats.get('buttons', 0))
            k4.metric("Images Found", stats.get('images', 0))

        st.divider()
        st.subheader(f"💬 Chatting with: {st.session_state.scanned_url}")
        
        # Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if user_input := st.chat_input("Ask about tech stack, colors, or code..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # AI Reply
            with st.chat_message("assistant"):
                with st.spinner("Analyzing site data..."):
                    chat_prompt = f"""
                    You are a Senior Technical Architect.
                    KNOWLEDGE BASE (Scraped Data):
                    {st.session_state.knowledge_base[:30000]}
                    
                    USER QUESTION: "{user_input}"
                    
                    INSTRUCTIONS:
                    1. Answer based ONLY on the scraped data.
                    2. If asked for a prompt, write a 'Cursor/Bolt.new' system prompt.
                    3. Be concise and technical.
                    """
                    response = generate_with_fallback(model_name, chat_prompt)
                    if response:
                        ai_reply = response.text
                        st.markdown(ai_reply)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        
        with st.expander("📦 Download Raw Data"):
            st.download_button("Download Full Scan JSON", st.session_state.knowledge_base, file_name="scan_data.json")
