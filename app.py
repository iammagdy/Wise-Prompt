import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from PIL import Image
import json
import re
import time
from urllib.parse import urljoin, urlparse

# --- 1. CONFIG & STYLING (HACKER MODE) ---
st.set_page_config(
    page_title="GOD-MODE: OMNI-TOOL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    div[data-testid="stMarkdownContainer"] p { font-size: 1.1em; }
    div.stAlert { background-color: #161B22; border: 1px solid #30363D; color: #E6EDF3; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE FUNCTIONS ---

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
                st.error(f"❌ Backup failed: {e2}")
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
            status_text.markdown(f"**🕷️ Scanning:** `{url}`")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200: continue
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Stats & Structure
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
            
            # Assets & Text
            page_assets = extract_assets(soup, url)
            all_assets['fonts'].update(page_assets['fonts'])
            all_assets['icons'].update(page_assets['icons'])
            combined_text += f"\n\n--- PAGE: {title} ({url}) ---\nSCRIPTS: {scripts[:5]}\nCONTENT: {text_content[:4000]}"
            
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
    status_text.success(f"✅ Scanned {count} pages.")
    final_assets = {k: list(v) for k, v in all_assets.items()}
    return combined_text, site_structure, final_assets, global_stats

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ SYSTEM CONTROL")
    api_key = st.text_input("API KEY", type="password")
    st.divider()
    
    model_options = ["gemini-2.0-flash-exp", "gemini-3-pro-preview", "gemini-2.5-flash", "gemini-1.5-pro", "Custom (Type new...)"]
    selected_option = st.selectbox("MODEL", model_options)
    if selected_option == "Custom (Type new...)":
        model_name = st.text_input("ENTER CUSTOM MODEL", value="gemini-2.0-flash-exp")
    else:
        model_name = selected_option
    st.caption(f"Active: `{model_name}`")

# --- 4. MAIN APP ---
st.title("⚡ GOD-MODE: OMNI-TOOL")
st.markdown("---")

if not api_key:
    st.warning("🔒 ENTER API KEY")
    st.stop()

genai.configure(api_key=api_key)

tab1, tab2, tab3 = st.tabs(["✨ PROMPT ARCHITECT", "🕷️ REVERSE ENGINEER", "👁️ FRONTEND ARCHITECT"])

# ==========================================
# TAB 1: PROMPT ARCHITECT (The God-Mode You Liked)
# ==========================================
with tab1:
    st.header("✨ The Architect Engine")
    st.info("Transforms simple ideas into world-class System Protocols.")
    
    c1, c2 = st.columns([3, 1])
    with c1: raw_prompt = st.text_area("YOUR IDEA", height=150, placeholder="e.g. bring any updated pdf to charts...")
    with c2: complexity = st.select_slider("DEPTH", ["Standard", "Detailed", "God-Mode"], value="God-Mode")

    if st.button("🚀 ARCHITECT PROMPT", type="primary"):
        if not raw_prompt:
            st.warning("Input required.")
        else:
            with st.spinner("Deconstructing & Architecting..."):
                sys_prompt = f"""
                You are the World's Greatest Prompt Architect.
                USER INPUT: "{raw_prompt}"
                INTENSITY: {complexity}
                
                GOAL: Transform this into a massive, world-class "System Prompt".
                
                STRICT OUTPUT STRUCTURE (Markdown):
                # 1. MISSION PROFILE
                **Role:** [Precise Persona]
                **Objective:** [Success State]
                **Context:** [Why?]

                # 2. STRATEGIC PROTOCOL
                [Step-by-Step execution plan. Be algorithmic.]

                # 3. KNOWLEDGE BASE & BEST PRACTICES (Crucial)
                [List 5-7 expert principles. Hallucinate these based on domain. e.g. "Prioritize Tufte's data-ink ratio".]

                # 4. CONSTRAINTS
                [What must the AI NOT do?]

                # 5. OUTPUT FORMATTING
                [Exact format definition]

                INTERNAL: Do NOT talk to user. JUST OUTPUT THE PROMPT.
                """
                res = generate_with_fallback(model_name, sys_prompt)
                if res: st.markdown(res.text)

# ==========================================
# TAB 2: REVERSE ENGINEER (Upgraded Crawler)
# ==========================================
with tab2:
    st.header("🕷️ Site Reverse Engineer")
    st.info("Crawls the site, analyzes the Tech Stack, and builds a Cloning Protocol.")
    
    if 'kb' not in st.session_state: st.session_state.kb = ""
    
    c1, c2 = st.columns([3, 1])
    with c1: url = st.text_input("TARGET URL", placeholder="https://...")
    with c2: scope = st.selectbox("SCOPE", ["Home Page", "Quick Scan (5)", "Deep Scan (20)"])
    
    page_limit = 1 if "Home" in scope else (5 if "Quick" in scope else 20)

    if st.button("🕷️ START AUTOPSY", type="primary"):
        if not url: st.warning("URL required")
        else:
            full_text, structure, assets, stats = recursive_crawl(url, max_pages=page_limit)
            
            st.session_state.kb = f"URL: {url}\nSTATS: {stats}\nASSETS: {assets}\nCONTENT: {full_text[:30000]}"
            
            with st.spinner("Analzying DNA..."):
                # --- THE UPGRADED ANALYSIS PROMPT ---
                analysis_prompt = f"""
                Act as a Senior Reverse Engineer.
                
                DATA SOURCE:
                {st.session_state.kb[:30000]}
                
                TASK:
                Perform a full technical autopsy of this website and generate a "Cloning Protocol".
                
                OUTPUT STRUCTURE:
                
                ### 1. 🧬 DNA ANALYSIS
                * **Likely Tech Stack:** (Guess based on scripts: React? Vue? WordPress? Tailwind?)
                * **Color Palette:** (Extract hex codes implied by the text/style).
                * **Typography:** (List fonts found in assets).
                
                ### 2. 🗺️ ARCHITECTURE MAP
                * **Page Structure:** (Tree view of the scanned pages).
                * **Key Components:** (e.g., "Sticky Navbar", "Hero Carousel", "Pricing Grid").
                
                ### 3. 💻 CLONING INSTRUCTION (System Prompt)
                [Write a ready-to-use prompt for Cursor/Bolt to rebuild this site's Homepage]
                * Include: "Use these specific fonts: {assets.get('fonts')}"
                * Include: "Mock up these images: {len(assets.get('images'))} placeholders needed."
                """
                
                res = generate_with_fallback(model_name, analysis_prompt)
                if res: st.markdown(res.text)

    # Chat
    if st.session_state.kb:
        st.divider()
        user_q = st.chat_input("Ask about the site's code, stack, or design...")
        if user_q:
            with st.chat_message("user"): st.write(user_q)
            with st.chat_message("assistant"):
                q_prompt = f"Expert Technical Architect. Answer based on: {st.session_state.kb[:20000]}. Q: {user_q}"
                ans = generate_with_fallback(model_name, q_prompt)
                if ans: st.write(ans.text)

# ==========================================
# TAB 3: FRONTEND ARCHITECT (Upgraded Vision)
# ==========================================
with tab3:
    st.header("👁️ Visual Frontend Architect")
    st.info("Turns screenshots into Production-Ready Component Architecture.")
    
    img_file = st.file_uploader("UPLOAD UI", type=['png', 'jpg'])
    c1, c2 = st.columns(2)
    with c1: stack = st.selectbox("STACK", ["Next.js + Tailwind", "React + Material UI", "HTML + CSS"])
    with c2: focus = st.radio("FOCUS", ["Pixel Perfect Clone", "Component Architecture"], horizontal=True)

    if st.button("🧬 DECODE UI"):
        if not img_file: st.warning("Upload Image")
        else:
            with st.spinner("Decoding Pixels..."):
                img = Image.open(img_file)
                
                # --- THE UPGRADED VISION PROMPT ---
                vision_prompt = f"""
                Act as a Lead Frontend Architect.
                TARGET: {stack}
                MODE: {focus}
                
                Analyze this UI screenshot. Do not just write code. ARCHITECT it.
                
                OUTPUT STRUCTURE:
                
                ### 1. 🧱 COMPONENT BREAKDOWN
                Identify reusable components.
                * **Atomic:** (Buttons, Inputs, Badges)
                * **Molecules:** (Search Bar, User Card)
                * **Organisms:** (Navbar, Sidebar, Hero Section)
                
                ### 2. 🎨 DESIGN TOKENS
                * **Spacing System:** (Compact vs Spacious)
                * **Border Radius:** (Rounded vs Sharp)
                * **Shadows:** (Flat vs Elevated)
                
                ### 3. ⚡ STATE MANAGEMENT
                Identify where state is needed (e.g., "Is 'Open Modal' needed?", "Is there a Carousel index?").
                
                ### 4. 💻 THE CODE (The Vibe)
                Write the {stack} code for the MAIN CONTAINER component, importing the sub-components defined above.
                """
                
                res = generate_with_fallback(model_name, vision_prompt, image=img)
                if res: st.markdown(res.text)
