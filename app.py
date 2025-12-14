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

# --- HELPER: RECURSIVE CRAWLER ---
def recursive_crawl(start_url, max_pages=3):
    """
    Crawls the homepage and up to 'max_pages' internal links.
    Returns a combined text summary of the site.
    """
    visited = set()
    queue = [start_url]
    combined_text = ""
    page_summaries = []
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
    base_domain = urlparse(start_url).netloc

    status_placeholder = st.empty() # specific UI element for updates

    count = 0
    while queue and count < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        
        try:
            status_placeholder.info(f"🕷️ Crawling: {url}...")
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract Text
            text = soup.get_text(separator=' ', strip=True)[:3000] # Limit per page
            title = soup.title.string if soup.title else "No Title"
            
            combined_text += f"\n\n--- PAGE: {title} ({url}) ---\n{text}"
            page_summaries.append({"url": url, "title": title})
            
            visited.add(url)
            count += 1
            
            # Find internal links for the queue
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Only follow internal links
                if urlparse(full_url).netloc == base_domain and full_url not in visited:
                    if full_url not in queue:
                        queue.append(full_url)
            
            time.sleep(0.5) # Be polite to the server
            
        except Exception as e:
            st.warning(f"Skipped {url}: {e}")
            
    status_placeholder.success(f"✅ Crawled {count} pages successfully!")
    return combined_text, page_summaries

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Engine Room")
    api_key = st.text_input("🔑 Paste Gemini API Key:", type="password")
    
    st.divider()
    model_name = st.text_input("Model Name:", value="gemini-pro") 
    st.caption("Auto-switches if 404 error occurs.")
    
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
st.markdown("Two powerful tools in one app. Select a tab below.")

if not api_key:
    st.warning("⬅️ Waiting for API Key in the sidebar...")
    st.stop()

genai.configure(api_key=api_key)

# --- TABS ---
tab1, tab2 = st.tabs(["✨ Prompt Enhancer (Interactive)", "🕷️ Website Replicator (Deep Scan)"])

# ==========================================
# TAB 1: THE INTERACTIVE PROMPT ENHANCER
# ==========================================
with tab1:
    st.header("✨ The Active Reasoning Engine")
    
    # Session State
    if 'enhancer_step' not in st.session_state:
        st.session_state.enhancer_step = "input"
    if 'draft_result' not in st.session_state:
        st.session_state.draft_result = ""
    if 'discovery_questions' not in st.session_state:
        st.session_state.discovery_questions = []

    # STEP 1: INPUT
    if st.session_state.enhancer_step == "input":
        col1, col2 = st.columns([1, 2])
        with col1:
            mode = st.selectbox(
                "Choose Strategy:",
                [
                    "✨ Auto-Detect (AI Decides)", 
                    "⚡ Vibe Coder (Bolt/Antigravity)", 
                    "CO-STAR (General Writing)", 
                    "Chain of Thought (Logic)", 
                    "Senior Coder (Python/JS)",
                    "Email Polisher",
                    "S.M.A.R.T. (Business)",
                    "The 5 Ws (Reporting)"
                ]
            )
            
            # --- DYNAMIC EXPLANATIONS (The Brief) ---
            descriptions = {
                "✨ Auto-Detect (AI Decides)": "🤖 **Best for:** When you aren't sure. I will analyze your text and pick the perfect framework automatically.",
                "⚡ Vibe Coder (Bolt/Antigravity)": "💻 **Best for:** AI Agents (Bolt.new, Replit Agent). Generates prompts with 'Few-Shot Examples' to prevent bad code.",
                "CO-STAR (General Writing)": "📝 **Best for:** Blogs, Essays, Marketing. Uses Context, Objective, Style, Tone, Audience, Response.",
                "Chain of Thought (Logic)": "🧠 **Best for:** Math, Riddles, Complex Logic. Forces the AI to think step-by-step to avoid errors.",
                "Senior Coder (Python/JS)": "👨‍💻 **Best for:** Technical specs. Focuses on clean architecture, error handling, and security.",
                "Email Polisher": "mw **Best for:** Corporate Comms. Turns 'angry notes' into polite, professional emails.",
                "S.M.A.R.T. (Business)": "📊 **Best for:** Goals & Planning. Ensures outputs are Specific, Measurable, Achievable, Relevant, and Time-bound.",
                "The 5 Ws (Reporting)": "📰 **Best for:** Journalism & Summaries. Ensures Who, What, Where, When, and Why are covered."
            }
            
            # Show the description for the selected mode
            if mode in descriptions:
                st.info(descriptions[mode])
            
            # Sub-options for Vibe Coder
            vibe_type = "Genesis"
            if mode == "⚡ Vibe Coder (Bolt/Antigravity)":
                vibe_type = st.radio("Stage?", ["Genesis (Start)", "Refiner (Polish)", "Logic Fixer (Bugs)"])

        raw_prompt = st.text_area("Your Request:", height=200, placeholder="e.g., build a crypto dashboard...")

        if st.button("🚀 Analyze & Enhance", type="primary"):
            if not raw_prompt:
                st.warning("Type something first!")
            else:
                with st.spinner("🧠 Analyzing gaps in your request..."):
                    
                    target_mode = mode
                    if mode == "✨ Auto-Detect (AI Decides)":
                         classifier_prompt = f"Classify intent: '{raw_prompt}'. Return ONE word: CODE, BUG, WRITING, LOGIC, EMAIL, PLAN."
                         cls = generate_with_fallback(model_name, classifier_prompt)
                         cat = cls.text.strip().upper() if cls else "WRITING"
                         
                         if "CODE" in cat: target_mode = "⚡ Vibe Coder (Bolt/Antigravity)"
                         elif "BUG" in cat: target_mode = "⚡ Vibe Coder (Bolt/Antigravity)"
                         elif "LOGIC" in cat: target_mode = "Chain of Thought (Logic)"
                         elif "EMAIL" in cat: target_mode = "Email Polisher"
                         elif "PLAN" in cat: target_mode = "S.M.A.R.T. (Business)"
                         else: target_mode = "CO-STAR (General Writing)"

                    analysis_prompt = f"""
                    Analyze this user request: "{raw_prompt}"
                    Target Framework: {target_mode}
                    
                    TASK 1: Rewrite it into a 'Draft Prompt' using the target framework.
                    TASK 2: Identify 3 MISSING pieces of information.
                    
                    OUTPUT FORMAT (JSON):
                    {{
                        "draft": "The rewritten draft prompt...",
                        "questions": ["Question 1?", "Question 2?", "Question 3?"]
                    }}
                    """
                    
                    response = generate_with_fallback(model_name, analysis_prompt)
                    
                    if response:
                        try:
                            text = response.text
                            match = re.search(r'\{.*\}', text, re.DOTALL)
                            if match:
                                data = json.loads(match.group())
                                st.session_state.draft_result = data.get('draft', "")
                                st.session_state.discovery_questions = data.get('questions', [])
                                st.session_state.enhancer_step = "analysis"
                                st.rerun()
                            else:
                                st.error("AI output invalid.")
                        except Exception as e:
                            st.error(f"Error: {e}")

    # STEP 2: DISCOVERY
    elif st.session_state.enhancer_step == "analysis":
        st.success("✅ Analysis Complete! I found some gaps.")
        
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.subheader("📄 Draft V1")
            st.code(st.session_state.draft_result, language="markdown")
            if st.button("🔙 Start Over"):
                st.session_state.enhancer_step = "input"
                st.rerun()

        with col_b:
            st.subheader("🕵️ Refinement")
            st.info("The AI suggests answering these:")
            
            with st.form("discovery_form"):
                q_list = st.session_state.discovery_questions
                while len(q_list) < 3: q_list.append("Any extra details?")
                
                q1 = st.text_input(f"1. {q_list[0]}")
                q2 = st.text_input(f"2. {q_list[1]}")
                q3 = st.text_input(f"3. {q_list[2]}")
                
                submitted = st.form_submit_button("✨ Update & Finalize")
                
                if submitted:
                    with st.spinner("Synthesizing..."):
                        final_prompt_request = f"""
                        Merge into FINAL PROMPT.
                        DRAFT: {st.session_state.draft_result}
                        ANSWERS: 1.{q1}, 2.{q2}, 3.{q3}
                        """
                        final_resp = generate_with_fallback(model_name, final_prompt_request)
                        if final_resp:
                            st.session_state.draft_result = final_resp.text
                            st.session_state.enhancer_step = "final"
                            st.rerun()

    # STEP 3: FINAL
    elif st.session_state.enhancer_step == "final":
        st.balloons()
        st.subheader("🚀 God-Mode Prompt (Final)")
        st.code(st.session_state.draft_result, language="markdown")
        if st.button("🔄 Create Another"):
            st.session_state.enhancer_step = "input"
            st.rerun()

# ==========================================
# TAB 2: THE WEBSITE REPLICATOR (DEEP SCAN)
# ==========================================
with tab2:
    st.header("🕷️ Deep Website Scanner")
    
    if 'scraped_text' not in st.session_state:
        st.session_state.scraped_text = ""
    if 'site_map' not in st.session_state:
        st.session_state.site_map = [] # List of pages found

    url = st.text_input("Target Website URL:", placeholder="https://example.com")
    
    if st.button("🕷️ Start Deep Scan (Recursive)"):
        if not url:
            st.warning("Need a URL!")
        else:
            with st.spinner("🕷️ Initializing Recursive Crawler... (This may take 10-20 seconds)"):
                # RUN THE RECURSIVE CRAWLER
                full_text, pages = recursive_crawl(url, max_pages=3)
                
                st.session_state.scraped_text = full_text
                st.session_state.site_map = pages
                st.session_state.site_title = pages[0]['title'] if pages else "Unknown"

    if st.session_state.scraped_text:
        st.divider()
        st.subheader(f"✅ Scanned {len(st.session_state.site_map)} Pages")
        with st.expander("View Site Map"):
            for p in st.session_state.site_map:
                st.write(f"- [{p['title']}]({p['url']})")

        st.subheader("2️⃣ Director's Cut")
        
        c1, c2 = st.columns(2)
        with c1:
            brand_name = st.text_input("Brand Name:", value=st.session_state.site_title)
        with c2:
            role = st.text_input("Industry/Role:", placeholder="e.g. SaaS")
            
        c3, c4 = st.columns(2)
        with c3:
            vibe = st.text_input("Visual Vibe:", placeholder="Dark, Minimal")
        with c4:
            stack = st.selectbox("Tech Stack:", ["Next.js + Tailwind + Framer", "HTML + CSS + JS", "React + Three.js"])

        magic = st.text_area("✨ Describe Animation Magic:", placeholder="e.g., 'A 3D cube spins on hover'.")

        if st.button("🚀 Generate Report & Prompt", type="primary"):
            with st.spinner("Analyzing Deep Data..."):
                
                # --- PROMPT FOR DUAL OUTPUT ---
                analysis_request = f"""
                Act as a Senior Technical Architect.
                
                SOURCE DATA (From Recursive Crawl):
                "{st.session_state.scraped_text[:12000]}..."
                
                USER CONTEXT:
                Brand: {brand_name}, Role: {role}, Vibe: {vibe}, Stack: {stack}, Magic: {magic}
                
                TASK:
                Generate TWO distinct outputs separated by a specific delimiter "|||SEPARATOR|||".
                
                OUTPUT 1: THE BLUEPRINT REPORT (Markdown)
                - Overall Summary (What is this site?)
                - Site Map Analysis (Structure based on crawled pages)
                - Design System (Colors, Fonts, Patterns inferred from text)
                - Tech Stack Detection (Guess frameworks based on patterns)
                
                OUTPUT 2: THE BUILDER PROMPT (System Instruction)
                - A direct system prompt for an AI Agent (Cursor/v0) to build this.
                - Include specific instructions for {stack} and {magic}.
                - Include '### FEW-SHOT TRAINING' examples for code quality.
                
                FORMAT:
                [Markdown Report]
                |||SEPARATOR|||
                [System Prompt Code Block]
                """
                
                response = generate_with_fallback(model_name, analysis_request)
                
                if response:
                    try:
                        parts = response.text.split("|||SEPARATOR|||")
                        report = parts[0]
                        builder_prompt = parts[1] if len(parts) > 1 else "Error generating prompt."
                        
                        # DISPLAY DUAL TABS
                        out_tab1, out_tab2 = st.tabs(["📄 The Blueprint (Report)", "💻 The Builder (Prompt)"])
                        
                        with out_tab1:
                            st.markdown(report)
                        with out_tab2:
                            st.code(builder_prompt, language='markdown')
                            
                    except Exception as e:
                        st.error("Error splitting output. Showing raw response.")
                        st.write(response.text)
