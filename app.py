import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import json

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
tab1, tab2 = st.tabs(["✨ Prompt Enhancer (Interactive)", "🕷️ Website Replicator (Builder)"])

# ==========================================
# TAB 1: THE INTERACTIVE PROMPT ENHANCER
# ==========================================
with tab1:
    st.header("✨ The Active Reasoning Engine")
    
    # Session State for Discovery Mode
    if 'enhancer_step' not in st.session_state:
        st.session_state.enhancer_step = "input" # input -> analysis -> final
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
                    
                    # 1. ANALYZE & GENERATE QUESTIONS
                    analysis_prompt = f"""
                    Analyze this user request: "{raw_prompt}"
                    
                    TASK 1: Rewrite it into a 'Draft Prompt' using the best framework (CO-STAR or Technical Spec).
                    TASK 2: Identify 3 MISSING pieces of information that would make this prompt perfect.
                    
                    OUTPUT FORMAT (JSON):
                    {{
                        "draft": "The rewritten draft prompt...",
                        "questions": ["Question 1?", "Question 2?", "Question 3?"]
                    }}
                    """
                    
                    # Force JSON response logic
                    response = generate_with_fallback(model_name, analysis_prompt + "\nReturn Valid JSON only.")
                    
                    if response:
                        try:
                            # Parse the JSON
                            cleaned_text = response.text.replace("```json", "").replace("```", "")
                            data = json.loads(cleaned_text)
                            
                            st.session_state.draft_result = data['draft']
                            st.session_state.discovery_questions = data['questions']
                            st.session_state.enhancer_step = "analysis" # Move to next step
                            st.rerun() # Refresh page to show new UI
                        except:
                            st.error("AI Analysis failed to format correctly. Try again.")

    # STEP 2: DISCOVERY & REFINEMENT
    elif st.session_state.enhancer_step == "analysis":
        st.success("✅ Analysis Complete! I found some gaps.")
        
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.subheader("📄 Draft V1 (Good)")
            st.code(st.session_state.draft_result, language="markdown")
            
            if st.button("🔙 Start Over"):
                st.session_state.enhancer_step = "input"
                st.rerun()

        with col_b:
            st.subheader("🕵️ Refinement (Make it Perfect)")
            st.info("The AI suggests answering these to reach 'God Mode':")
            
            with st.form("discovery_form"):
                q1 = st.text_input(f"1. {st.session_state.discovery_questions[0]}")
                q2 = st.text_input(f"2. {st.session_state.discovery_questions[1]}")
                q3 = st.text_input(f"3. {st.session_state.discovery_questions[2]}")
                
                submitted = st.form_submit_button("✨ Update & Finalize")
                
                if submitted:
                    with st.spinner("Synthesizing your answers..."):
                        final_prompt_request = f"""
                        The user has refined the previous draft.
                        
                        ORIGINAL DRAFT:
                        {st.session_state.draft_result}
                        
                        USER ANSWERS TO CLARIFYING QUESTIONS:
                        1. {q1}
                        2. {q2}
                        3. {q3}
                        
                        TASK: Merge the original draft and the new answers into a FINAL MASTER PROMPT.
                        If this is code, include '### FEW-SHOT TRAINING' examples.
                        """
                        
                        final_resp = generate_with_fallback(model_name, final_prompt_request)
                        if final_resp:
                            st.session_state.draft_result = final_resp.text
                            st.session_state.enhancer_step = "final"
                            st.rerun()

    # STEP 3: FINAL RESULT
    elif st.session_state.enhancer_step == "final":
        st.balloons()
        st.subheader("🚀 God-Mode Prompt (Final)")
        st.code(st.session_state.draft_result, language="markdown")
        
        if st.button("🔄 Create Another"):
            st.session_state.enhancer_step = "input"
            st.rerun()

# ==========================================
# TAB 2: THE WEBSITE REPLICATOR (Same as before)
# ==========================================
with tab2:
    st.header("🕷️ Clone a Website's Soul")
    
    if 'scraped_text' not in st.session_state:
        st.session_state.scraped_text = ""
    if 'site_title' not in st.session_state:
        st.session_state.site_title = ""

    url = st.text_input("Target Website URL:", placeholder="https://example.com")
    
    if st.button("🕷️ Scan Website"):
        if not url:
            st.warning("Need a URL!")
        else:
            with st.spinner("Reading website..."):
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    r = requests.get(url, headers=headers, timeout=10)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    st.session_state.site_title = soup.title.string if soup.title else "Unknown"
                    st.session_state.scraped_text = soup.get_text(separator=' ', strip=True)[:10000]
                    st.success(f"✅ Scanned: {st.session_state.site_title}")
                except Exception as e:
                    st.error(f"Scan failed: {e}")

    if st.session_state.scraped_text:
        st.divider()
        st.subheader("2️⃣ Director's Cut (Customize It)")
        
        c1, c2 = st.columns(2)
        with c1:
            brand_name = st.text_input("Agent / Brand Name:", value=st.session_state.site_title)
        with c2:
            role = st.text_input("Industry / Role:", placeholder="e.g. SaaS, Portfolio")
            
        c3, c4 = st.columns(2)
        with c3:
            vibe = st.text_input("Visual Vibe:", placeholder="Dark, Minimal, Colorful")
        with c4:
            stack = st.selectbox("Tech Stack:", ["Next.js + Tailwind + Framer", "HTML + CSS + JS", "Vue.js + Tailwind", "React + Three.js (3D)"])

        magic = st.text_area("✨ Describe the Magic (Animations/Interactions):", 
                             placeholder="IMPORTANT: Describe what moves. e.g., 'A 3D cube spins on hover'.")

        if st.button("🚀 Generate Replicator Prompt", type="primary"):
            with st.spinner("Synthesizing Code Strategy..."):
                
                final_prompt = f"""
                Act as a Senior Frontend Architect.
                TASK: Create a system prompt for an AI Coding Agent (Cursor/v0) to REPLICATE this website.
                
                ### 1. SOURCE DATA
                * **Brand Name:** {brand_name}
                * **Original Title:** {st.session_state.site_title}
                * **Content Summary:** "{st.session_state.scraped_text[:2000]}..."
                
                ### 2. USER VISION
                * **Role:** {role}
                * **Vibe:** {vibe}
                * **Tech Stack:** {stack}
                * **REQUIRED ANIMATIONS (Crucial):** {magic}
                
                ### 3. INSTRUCTIONS
                Write a prompt that instructs the AI to:
                1. Use the defined Tech Stack ({stack}).
                2. If the user described 3D/Physics in the 'Animations' section, explicitly recommend libraries like Three.js or Matter.js.
                3. Structure the Scraped Content into a beautiful layout for '{brand_name}' matching the '{vibe}'.
                
                OUTPUT: Provide ONLY the prompt in a code block.
                """
                
                response = generate_with_fallback(model_name, final_prompt)
                if response:
                    st.subheader("🧬 Your Master Prompt:")
                    st.code(response.text, language='markdown')
