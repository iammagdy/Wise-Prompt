import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from PIL import Image
import json
import re
import time
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse

# --- 1. PAGE CONFIG & RESPONSIVE CYBERPUNK CSS ---
st.set_page_config(
    page_title="GOD-MODE: OMNI-TOOL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto" # Let Streamlit decide based on screen size
)

# Inject "Hacker" Vibe CSS with Mobile Optimizations
st.markdown("""
    <style>
    /* --- MAIN DESKTOP THEME --- */
    .stApp { background-color: #0E1117; color: #00FF94; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0D1117 !important; 
        color: #E6EDF3 !important; 
        border: 1px solid #30363D;
    }
    
    /* Headers */
    h1, h2, h3 { font-family: 'Courier New', monospace; color: #E6EDF3; }
    
    /* Metrics */
    .metric-container { background-color: #0D1117; border: 1px solid #30363D; padding: 10px; border-radius: 5px; }
    div[data-testid="stMarkdownContainer"] p { font-size: 1.05em; }

    /* --- MOBILE OPTIMIZATIONS (The Magic) --- */
    @media only screen and (max-width: 600px) {
        
        /* 1. Reset Padding for small screens */
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        /* 2. Big, Tappable Buttons */
        .stButton button {
            width: 100% !important;
            height: 3.5rem !important;
            font-size: 1.2rem !important;
            margin-top: 10px;
            background-color: #238636;
            color: white;
            border-radius: 8px;
        }
        
        /* 3. Prevent iOS Zoom on Inputs (Font 16px+) */
        .stTextInput input, .stTextArea textarea, .stSelectbox div {
            font-size: 16px !important;
        }

        /* 4. Headers Scaling */
        h1 { font-size: 1.8rem !important; text-align: center; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.2rem !important; }

        /* 5. Metrics Stacking */
        div[data-testid="stMetric"] {
            background-color: #161B22;
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 5px;
            border: 1px solid #30363D;
            text-align: center;
        }
        
        /* 6. Sidebar Mobile */
        [data-testid="stSidebar"] {
            width: 85% !important; /* Make it wider on mobile for ease of use */
        }
    }
    
    /* Desktop Button Hover Effect (Keep for desktop users) */
    @media only screen and (min-width: 601px) {
        .stButton button { 
            background-color: #238636; 
            color: white; 
            border: none; 
            font-weight: bold; 
            transition: all 0.3s ease;
        }
        .stButton button:hover { 
            background-color: #2EA043; 
            box-shadow: 0 0 10px #2EA043;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. PERSISTENCE LAYER (HISTORY) ---
HISTORY_FILE = "god_mode_history.json"

def load_history_db():
    if not os.path.exists(HISTORY_FILE): return {}
    try:
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    except: return {}

def save_history_db(db):
    with open(HISTORY_FILE, "w") as f: json.dump(db, f, indent=4)

def add_to_history(api_key, tool_used, input_data, output_data):
    db = load_history_db()
    if api_key not in db: db[api_key] = []
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tool": tool_used,
        "input": str(input_data)[:200] + "...", 
        "output": output_data
    }
    db[api_key].insert(0, entry)
    save_history_db(db)

def get_user_history(api_key):
    db = load_history_db()
    return db.get(api_key, [])

def clear_user_history(api_key):
    db = load_history_db()
    if api_key in db:
        del db[api_key]
        save_history_db(db)

# --- 3. HELPER FUNCTIONS ---

def generate_with_fallback(user_model_name, prompt, image=None):
    try:
        model = genai.GenerativeModel(user_model_name)
        if image: return model.generate_content([prompt, image])
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
    assets = {"fonts": [], "icons": [], "images": []}
    for link in soup.find_all('link', href=True):
        href = link['href']
        if 'fonts.googleapis.com' in href or href.endswith('.woff') or href.endswith('.woff2'):
            assets['fonts'].append(urljoin(url, href))
    for link in soup.find_all('link', rel=True):
        rel_val = link['rel']
        if isinstance(rel_val, list):
            if 'icon' in rel_val: assets['icons'].append(urljoin(url, link.get('href', '')))
        elif 'icon' in rel_val:
             assets['icons'].append(urljoin(url, link.get('href', '')))
    for img in soup.find_all('img', src=True):
        src = img['src']
        full_src = urljoin(url, src)
        if 'logo' in src.lower() or src.endswith('.svg'):
            assets['icons'].append(full_src)
        else:
            assets['images'].append(full_src)
    return assets

def recursive_crawl(start_url, max_pages=5):
    visited = set()
    queue = [start_url]
    combined_text = ""
    site_structure = {} 
    all_assets = {"fonts": set(), "icons": set(), "images": set()}
    global_stats = {"pages": 0, "buttons": 0, "links": 0, "images": 0, "inputs": 0, "words": 0}
    
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
            
            global_stats["buttons"] += len(soup.find_all('button'))
            global_stats["links"] += len(soup.find_all('a'))
            global_stats["images"] += len(soup.find_all('img'))
            global_stats["inputs"] += len(soup.find_all('input'))
            text_content = soup.get_text(separator=' ', strip=True)
            global_stats["words"] += len(text_content.split())
            global_stats["pages"] += 1
            
            scripts = [s.get('src') for s in soup.find_all('script') if s.get('src')]
            title = soup.title.string if soup.title else "No Title"
            site_structure[url] = {"title": title, "scripts": scripts[:3]}
            
            page_assets = extract_assets(soup, url)
            all_assets['fonts'].update(page_assets['fonts'])
            all_assets['icons'].update(page_assets['icons'])
            
            combined_text += f"\n\n--- PAGE: {title} ({url}) ---\nDETECTED SCRIPTS: {scripts[:5]}\nCONTENT: {text_content[:4000]}"
            visited.add(url)
            count += 1
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == base_domain and full_url not in visited and full_url not in queue:
                    queue.append(full_url)
            time.sleep(0.3)
        except: pass
            
    progress_bar.progress(100)
    status_text.success(f"✅ Mission Complete! Scanned {count} pages.")
    final_assets = {k: list(v) for k, v in all_assets.items()}
    return combined_text, site_structure, final_assets, global_stats

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ SYSTEM CONTROL")
    api_key = st.text_input("API KEY", type="password")
    st.divider()
    
    model_options = ["gemini-2.0-flash-exp", "gemini-3-pro-preview", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash", "Custom (Type new...)"]
    selected_option = st.selectbox("MODEL", model_options)
    if selected_option == "Custom (Type new...)":
        model_name = st.text_input("ENTER CUSTOM MODEL NAME", value="gemini-2.0-flash-exp")
    else:
        model_name = selected_option
    st.caption(f"Active Model: `{model_name}`")
    
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

# --- 5. MAIN APP ---
st.title("⚡ GOD-MODE: OMNI-TOOL")
st.markdown("---")

if not api_key:
    st.warning("🔒 ENTER API KEY TO UNLOCK")
    st.stop()

genai.configure(api_key=api_key)

tab1, tab2, tab3, tab4 = st.tabs(["✨ PROMPT ARCHITECT", "🕷️ DEEP NET SCANNER", "👁️ VISION REPLICATOR", "📜 HISTORY"])

# ==========================================
# TAB 1: PROMPT ARCHITECT
# ==========================================
with tab1:
    st.header("✨ The Architect Engine")
    
    mode = st.selectbox(
        "STRATEGY", 
        [
            "✨ Auto-Detect (AI Decides)", 
            "⚡ Vibe Coder (Bolt/Antigravity)", 
            "🧠 Super-System (The Architect)", 
            "CO-STAR (General Writing)", 
            "Chain of Thought (Logic)", 
            "Senior Coder (Python/JS)", 
            "Email Polisher", 
            "S.M.A.R.T. (Business)", 
            "The 5 Ws (Reporting)", 
            "Custom Persona"
        ]
    )

    descriptions = {
        "✨ Auto-Detect (AI Decides)": "🤖 **Best for:** Unsure users. I analyze intent and pick the best framework automatically.",
        "⚡ Vibe Coder (Bolt/Antigravity)": "💻 **Best for:** AI Agents. Adds 'Few-Shot Examples' & Coding Standards.",
        "🧠 Super-System (The Architect)": "🏗️ **Best for:** Complex Tasks. Builds a massive 'System Protocol' with Role, Task, Knowledge, and Constraints.",
        "CO-STAR (General Writing)": "📝 **Best for:** Blogs & Essays. Context, Objective, Style, Tone, Audience, Response.",
        "Chain of Thought (Logic)": "🧠 **Best for:** Math & Riddles. Forces step-by-step thinking.",
        "Senior Coder (Python/JS)": "👨‍💻 **Best for:** Technical specs. Focuses on clean architecture and security.",
        "Email Polisher": "📧 **Best for:** Corporate Comms. Turns notes into professional emails.",
        "S.M.A.R.T. (Business)": "📊 **Best for:** Goals. Specific, Measurable, Achievable, Relevant, Time-bound.",
        "The 5 Ws (Reporting)": "📰 **Best for:** Journalism. Who, What, Where, When, Why.",
        "Custom Persona": "🎭 **Best for:** Roleplay. (e.g., Steve Jobs, Lawyer)."
    }
    if mode in descriptions: st.info(descriptions[mode])

    vibe_type = "Genesis"
    agent_name = "Expert"
    complexity = "God-Mode"

    if mode == "⚡ Vibe Coder (Bolt/Antigravity)":
        vibe_type = st.radio("STAGE?", ["Genesis (Start New)", "Refiner (Polish UI)", "Logic Fixer (Debug)"], horizontal=True)
    elif mode == "Custom Persona":
        agent_name = st.text_input("WHO IS THE AGENT?", placeholder="e.g. Steve Jobs")
    elif mode == "🧠 Super-System (The Architect)":
        complexity = st.select_slider("DEPTH", ["Standard", "Detailed", "God-Mode"], value="God-Mode")

    raw_prompt = st.text_area("YOUR REQUEST", height=150, placeholder="e.g. bring any updated pdf to charts...")
    
    if st.button("🚀 ARCHITECT PROMPT", type="primary"):
        if not raw_prompt:
            st.warning("Input required.")
        else:
            with st.spinner("Architecting..."):
                system_instruction = ""
                if mode == "🧠 Super-System (The Architect)":
                    system_instruction = f"You are the World's Greatest Prompt Architect. USER INPUT: '{raw_prompt}'. INTENSITY: {complexity}. GOAL: Transform this into a massive, world-class 'System Prompt'. STRICT OUTPUT STRUCTURE (Markdown): 1. MISSION PROFILE 2. STRATEGIC PROTOCOL 3. KNOWLEDGE BASE 4. CONSTRAINTS 5. OUTPUT FORMATTING"
                elif mode == "⚡ Vibe Coder (Bolt/Antigravity)":
                    subtype = ""
                    if "Genesis" in vibe_type: subtype = "Focus on scaffolding."
                    if "Refiner" in vibe_type: subtype = "Focus on UI polish."
                    if "Logic" in vibe_type: subtype = "Focus on debugging."
                    system_instruction = f"Act as Expert Prompt Engineer. FRAMEWORK: Vibe Coder ({vibe_type}). USER INPUT: '{raw_prompt}'. TASK: Create System Prompt for AI Coder. {subtype} CRITICAL: Include '### FEW-SHOT TRAINING' examples."
                elif mode == "✨ Auto-Detect (AI Decides)":
                    system_instruction = f"Analyze: '{raw_prompt}'. Detect intent. Rewrite using BEST framework. Output ONLY the rewritten prompt."
                elif mode == "CO-STAR (General Writing)":
                    system_instruction = f"Rewrite using CO-STAR. INPUT: '{raw_prompt}'"
                elif mode == "S.M.A.R.T. (Business)":
                    system_instruction = f"Rewrite as S.M.A.R.T Goals. INPUT: '{raw_prompt}'"
                elif mode == "Senior Coder (Python/JS)":
                    system_instruction = f"Rewrite as Technical Spec. INPUT: '{raw_prompt}'"
                elif mode == "Email Polisher":
                    system_instruction = f"Rewrite as Professional Email. INPUT: '{raw_prompt}'"
                else:
                    system_instruction = f"Rewrite professionally. INPUT: '{raw_prompt}'"

                res = generate_with_fallback(model_name, system_instruction)
                if res: 
                    st.success("✅ Architecture Complete")
                    st.markdown(res.text)
                    add_to_history(api_key, f"Prompt Architect ({mode})", raw_prompt, res.text)

# ==========================================
# TAB 2: DEEP NET SCANNER
# ==========================================
with tab2:
    st.header("🕷️ Deep Net Scanner")
    
    if 'messages' not in st.session_state: st.session_state.messages = []
    if 'knowledge_base' not in st.session_state: st.session_state.knowledge_base = ""
    if 'scanned_url' not in st.session_state: st.session_state.scanned_url = ""
    if 'global_stats' not in st.session_state: st.session_state.global_stats = {}

    c1, c2 = st.columns([3, 1])
    with c1: url = st.text_input("TARGET URL", placeholder="https://example.com")
    with c2: crawl_scope = st.selectbox("SCOPE", ["Home Page Only", "Quick Scan (5 Pages)", "Deep Scan (20 Pages)", "Massive Scan (50 Pages)"])

    page_limit = 1
    if "Quick" in crawl_scope: page_limit = 5
    if "Deep" in crawl_scope: page_limit = 20
    if "Massive" in crawl_scope: page_limit = 50
    
    if st.button("🕷️ INITIATE SCAN", type="primary"):
        if not url: st.warning("URL REQUIRED")
        else:
            full_text, structure, assets, stats = recursive_crawl(url, max_pages=page_limit)
            
            kb_content = f"""SOURCE URL: {url}\nSTATS: {json.dumps(stats)}\nSITE MAP: {json.dumps(structure)}\nASSETS: {json.dumps(assets)}\nCONTENT: {full_text}"""
            st.session_state.scanned_url = url
            st.session_state.global_stats = stats
            st.session_state.knowledge_base = kb_content
            st.session_state.messages = [{"role": "assistant", "content": f"**SCAN COMPLETE.** Analyzed {stats['pages']} pages. Found {stats['buttons']} buttons. Ready for queries."}]
            
            add_to_history(api_key, "Web Scanner", url, f"Scanned {stats['pages']} pages. Found {len(assets['fonts'])} fonts.")
            st.rerun()

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
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if user_input := st.chat_input("QUERY DATABASE..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"): st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("COMPUTING..."):
                    chat_prompt = f"Expert Architect. KB: {st.session_state.knowledge_base[:30000]}. Q: {user_input}"
                    response = generate_with_fallback(model_name, chat_prompt)
                    if response:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
        with st.expander("📦 RAW DATA EXPORT"):
            st.download_button("DOWNLOAD JSON", st.session_state.knowledge_base, file_name="scan_data.json")

# ==========================================
# TAB 3: VISION REPLICATOR
# ==========================================
with tab3:
    st.header("👁️ Vision Replicator")
    uploaded_file = st.file_uploader("UPLOAD INTERFACE IMAGE", type=['png', 'jpg', 'jpeg'])
    c1, c2 = st.columns(2)
    with c1: stack = st.selectbox("TECH STACK", ["Next.js + Tailwind", "React + Three.js", "HTML/CSS"])
    with c2: vibe = st.text_input("VIBE", placeholder="Cyberpunk, Clean")

    if st.button("🧬 GENERATE REPLICA CODE"):
        if not uploaded_file: st.warning("UPLOAD REQUIRED")
        else:
            with st.spinner("ANALYZING PIXELS..."):
                img = Image.open(uploaded_file)
                prompt = f"Act as Senior Frontend Dev. Write system prompt to build this exact UI using {stack}. Vibe: {vibe}."
                res = generate_with_fallback(model_name, prompt, image=img)
                if res: 
                    st.markdown(res.text)
                    add_to_history(api_key, "Vision Replicator", f"Image Upload: {stack}", res.text)

# ==========================================
# TAB 4: HISTORY ARCHIVE
# ==========================================
with tab4:
    st.header("📜 History Archive")
    st.caption("Past generations saved locally by API Key.")
    
    if st.button("🗑️ Clear My History"):
        clear_user_history(api_key)
        st.success("History wiped.")
        st.rerun()

    history = get_user_history(api_key)
    if not history:
        st.info("No history found. Start generating!")
    else:
        for item in history:
            with st.expander(f"{item['timestamp']} | {item['tool']} | {item['input']}"):
                st.subheader("Output:")
                st.markdown(item['output'])
