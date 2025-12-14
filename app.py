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
    div[data-testid="stMarkdownContainer"] p { font-size: 1.1em; }
    div.stAlert { background-color: #161B22; border: 1px solid #30363D; color: #E6EDF3; }
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
    
    # NEW MODEL SELECTOR
    model_options = [
        "gemini-2.0-flash-exp", 
        "gemini-3-pro-preview", 
        "gemini-2.5-flash", 
        "gemini-1.5-pro", 
        "gemini-1.5-flash",
        "Custom (Type new...)"
    ]
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

# --- 4. MAIN APP ---
st.title("⚡ GOD-MODE: OMNI-TOOL")
st.markdown("---")

if not api_key:
    st.warning("🔒 ENTER API KEY TO UNLOCK")
    st.stop()

genai.configure(api_key=api_key)

tab1, tab2, tab3 = st.tabs(["✨ PROMPT ARCHITECT", "🕷️ DEEP CRAWLER", "👁️ VISION REPLICATOR"])

# ==========================================
# TAB 1: PROMPT ARCHITECT (FULL MODES RESTORED)
# ==========================================
with tab1:
    st.header("✨ The Architect Engine")
    
    # 1. STRATEGY SELECTOR
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

    # --- THE DYNAMIC BRIEFS (RESTORED) ---
    descriptions = {
        "✨ Auto-Detect (AI Decides)": "🤖 **Best for:** Unsure users. I analyze intent and pick the best framework automatically.",
        "⚡ Vibe Coder (Bolt/Antigravity)": "💻 **Best for:** AI Agents (Bolt.new, Replit). Adds 'Few-Shot Examples' & Coding Standards.",
        "🧠 Super-System (The Architect)": "🏗️ **Best for:** Complex Tasks. Builds a massive 'System Protocol' with Role, Task, Knowledge, and Constraints.",
        "CO-STAR (General Writing)": "📝 **Best for:** Blogs & Essays. Uses Context, Objective, Style, Tone, Audience, Response.",
        "Chain of Thought (Logic)": "🧠 **Best for:** Math & Riddles. Forces step-by-step thinking.",
        "Senior Coder (Python/JS)": "👨‍💻 **Best for:** Technical specs. Focuses on clean architecture and security.",
        "Email Polisher": "📧 **Best for:** Corporate Comms. Turns notes into professional emails.",
        "S.M.A.R.T. (Business)": "📊 **Best for:** Goals. Ensures Specific, Measurable, Achievable, Relevant, Time-bound outputs.",
        "The 5 Ws (Reporting)": "📰 **Best for:** Journalism. Ensures Who, What, Where, When, Why.",
        "Custom Persona": "🎭 **Best for:** Roleplay. (e.g., Steve Jobs, Lawyer)."
    }
    
    if mode in descriptions:
        st.info(descriptions[mode])
    
    # 2. SUB-OPTIONS
    vibe_type = "Genesis"
    agent_name = "Expert"
    complexity = "God-Mode"

    if mode == "⚡ Vibe Coder (Bolt/Antigravity)":
        vibe_type = st.radio("STAGE?", ["Genesis (Start New)", "Refiner (Polish UI)", "Logic Fixer (Debug)"], horizontal=True)
    elif mode == "Custom Persona":
        agent_name = st.text_input("WHO IS THE AGENT?", placeholder="e.g. Steve Jobs")
    elif mode == "🧠 Super-System (The Architect)":
        complexity = st.select_slider("DEPTH", ["Standard", "Detailed", "God-Mode"], value="God-Mode")

    # 3. INPUT
    raw_prompt = st.text_area("YOUR REQUEST", height=150, placeholder="e.g. bring any updated pdf to charts...")
    
    # 4. EXECUTION
    if st.button("🚀 ARCHITECT PROMPT", type="primary"):
        if not raw_prompt:
            st.warning("Input required.")
        else:
            with st.spinner("Architecting..."):
                
                system_instruction = ""

                # --- ARCHITECT LOGIC (SUPER SYSTEM) ---
                if mode == "🧠 Super-System (The Architect)":
                    system_instruction = f"""
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

                # --- VIBE CODER LOGIC ---
                elif mode == "⚡ Vibe Coder (Bolt/Antigravity)":
                    subtype_instruction = ""
                    if "Genesis" in vibe_type: subtype_instruction = "Focus on scaffolding and project setup."
                    if "Refiner" in vibe_type: subtype_instruction = "Focus on UI/UX, Tailwind classes, and Animations."
                    if "Logic" in vibe_type: subtype_instruction = "Focus on Error Handling, Types, and Debugging."
                    
                    system_instruction = f"""
                    Act as an Expert Prompt Engineer for AI Agents.
                    FRAMEWORK: Vibe Coder ({vibe_type})
                    USER INPUT: "{raw_prompt}"
                    
                    TASK: Create a System Prompt for an AI Coder.
                    {subtype_instruction}
                    
                    CRITICAL REQUIREMENT:
                    You MUST include a section called '### FEW-SHOT TRAINING'.
                    In this section, provide examples of 'Bad Output' vs 'Good Output' relevant to the request.
                    
                    OUTPUT: Markdown Code Block.
                    """

                # --- AUTO DETECT LOGIC ---
                elif mode == "✨ Auto-Detect (AI Decides)":
                    system_instruction = f"""
                    Analyze: "{raw_prompt}".
                    1. Detect the intent (Code, Email, Logic, or Planning?).
                    2. Rewrite it using the BEST framework for that intent (e.g. CO-STAR or Architect).
                    3. Output ONLY the rewritten prompt in Markdown.
                    """

                # --- STANDARD MODES ---
                elif mode == "CO-STAR (General Writing)":
                    system_instruction = f"Rewrite using CO-STAR (Context, Objective, Style, Tone, Audience, Response). INPUT: '{raw_prompt}'"
                elif mode == "Chain of Thought (Logic)":
                    system_instruction = f"Rewrite to force step-by-step reasoning. INPUT: '{raw_prompt}'"
                elif mode == "S.M.A.R.T. (Business)":
                    system_instruction = f"Rewrite as S.M.A.R.T Goals. INPUT: '{raw_prompt}'"
                elif mode == "Email Polisher":
                    system_instruction = f"Rewrite as a Professional Email. INPUT: '{raw_prompt}'"
                elif mode == "Custom Persona":
                    system_instruction = f"Act as {agent_name}. Rewrite exactly how they would speak. INPUT: '{raw_prompt}'"
                else:
                    system_instruction = f"Rewrite professionally. INPUT: '{raw_prompt}'"

                # EXECUTE
                res = generate_with_fallback(model_name, system_instruction)
                if res: 
                    st.success("✅ Architecture Complete")
                    st.markdown(res.text)

# ==========================================
# TAB 2: CRAWL & CHAT (Deep Net Scanner)
# ==========================================
with tab2:
    st.header("🕷️ Deep Net Scanner")
    
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

# ==========================================
# TAB 3: VISION REPLICATOR
# ==========================================
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
                prompt = f"""
                Act as a Senior Frontend Dev. 
                Write a system prompt to build this exact UI using {stack}. 
                Vibe: {vibe}.
                Identify components, colors, and layout structure.
                """
                res = generate_with_fallback(model_name, prompt, image=img)
                if res: st.markdown(res.text)
