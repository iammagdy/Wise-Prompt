import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

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
tab1, tab2 = st.tabs(["✨ Prompt Enhancer (Writer)", "🕷️ Website Replicator (Builder)"])

# ==========================================
# TAB 1: THE PROMPT ENHANCER (Updated)
# ==========================================
with tab1:
    st.header("✨ Turn Lazy Ideas into Gold")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # THE NEW "AUTO-DETECT" IS THE DEFAULT
        mode = st.selectbox(
            "Choose Strategy:",
            [
                "✨ Auto-Detect (AI Decides Best Fit)", 
                "⚡ Vibe Coder (Bolt/Antigravity)", 
                "CO-STAR (General Writing)", 
                "Chain of Thought (Logic/Math)", 
                "Senior Coder (Python/JS)",
                "Email Polisher (Professional)",
                "Midjourney/Dal-E (Image Gen)",
                "S.M.A.R.T. (Business Goals)", # NEW
                "The 5 Ws (News/Reporting)"    # NEW
            ]
        )
        
        # LOGIC FOR MANUAL MODES
        vibe_type = "Genesis (New Project)" 
        if mode == "⚡ Vibe Coder (Bolt/Antigravity)":
            vibe_type = st.radio("Stage?", ["Genesis (Start)", "Refiner (Polish)", "Logic Fixer (Bugs)"])
        
        agent_name = "Expert"
        if mode == "Custom Persona":
            agent_name = st.text_input("Who should the AI act as?", placeholder="e.g. Steve Jobs")

    raw_prompt = st.text_area("Your Request:", height=200, placeholder="e.g., build a dashboard, OR write a angry email, OR solve a riddle...")

    if st.button("✨ Enhance Prompt", type="primary"):
        if not raw_prompt:
            st.warning("Type something first!")
        else:
            with st.spinner("🧠 Analyzing complexity & choosing framework..."):
                
                # --- 1. AUTO-DETECT INTELLIGENCE LAYER ---
                target_mode = mode # Default to what user picked
                
                if mode == "✨ Auto-Detect (AI Decides Best Fit)":
                    # We ask the AI to categorize the prompt first
                    classifier_prompt = f"""
                    Analyze this user request: "{raw_prompt}"
                    
                    Classify it into ONE of these categories based on the user's intent:
                    - CODE_GENESIS (If building a new app/website)
                    - CODE_FIX (If asking to fix a bug)
                    - WRITING (If writing an article, blog, or text)
                    - LOGIC (If a math problem, riddle, or complex reasoning)
                    - EMAIL (If sending a message/reply)
                    - IMAGE (If describing a picture)
                    - PLAN (If setting goals or business strategy)

                    OUTPUT ONLY THE CATEGORY NAME.
                    """
                    classification = generate_with_fallback(model_name, classifier_prompt)
                    
                    # Map the AI's classification to our Frameworks
                    detected_category = classification.text.strip().upper() if classification else "WRITING"
                    
                    if "CODE_GENESIS" in detected_category:
                        target_mode = "⚡ Vibe Coder (Bolt/Antigravity)"
                        vibe_type = "Genesis (New Project)"
                        st.info("🤖 AI Detected: New App Build -> Using **Vibe Coder (Genesis)**")
                    elif "CODE_FIX" in detected_category:
                        target_mode = "⚡ Vibe Coder (Bolt/Antigravity)"
                        vibe_type = "Logic Fixer (Bugs)"
                        st.info("🤖 AI Detected: Bug Fix -> Using **Vibe Coder (Fixer)**")
                    elif "LOGIC" in detected_category:
                        target_mode = "Chain of Thought (Logic/Math)"
                        st.info("🤖 AI Detected: Logic Puzzle -> Using **Chain of Thought**")
                    elif "EMAIL" in detected_category:
                        target_mode = "Email Polisher (Professional)"
                        st.info("🤖 AI Detected: Email -> Using **Email Polisher**")
                    elif "IMAGE" in detected_category:
                        target_mode = "Midjourney/Dal-E (Image Gen)"
                        st.info("🤖 AI Detected: Image Prompt -> Using **Midjourney Mode**")
                    elif "PLAN" in detected_category:
                        target_mode = "S.M.A.R.T. (Business Goals)"
                        st.info("🤖 AI Detected: Planning -> Using **S.M.A.R.T. Framework**")
                    else:
                        target_mode = "CO-STAR (General Writing)"
                        st.info("🤖 AI Detected: General Text -> Using **CO-STAR**")

                # --- 2. GENERATE SYSTEM PROMPT BASED ON (DETECTED) MODE ---
                system_prompt = ""
                
                # VIBE CODER LOGIC
                if target_mode == "⚡ Vibe Coder (Bolt/Antigravity)":
                    if "Genesis" in vibe_type:
                        system_prompt = f"""
                        Act as an Expert Prompt Engineer for AI Agents. Rewrite into a 'Genesis Prompt' using CO-STAR.
                        CRITICAL: Append a '### FEW-SHOT TRAINING' section with 'Bad Output' vs 'Good Output' (Next.js/Tailwind).
                        INPUT: "{raw_prompt}"
                        """
                    elif "Refiner" in vibe_type:
                        system_prompt = f"""
                        Act as a UI/UX Director. Rewrite into a 'Refiner Prompt'.
                        CRITICAL: Append a '### FEW-SHOT TRAINING' section (e.g. 'Make it pop' -> 'shadow-xl').
                        INPUT: "{raw_prompt}"
                        """
                    elif "Fixer" in vibe_type or "Logic" in vibe_type:
                        system_prompt = f"""
                        Act as a Senior Backend Engineer. Rewrite into a 'Logic Fixer Prompt'.
                        CRITICAL: Append a '### FEW-SHOT TRAINING' section about Error Handling.
                        INPUT: "{raw_prompt}"
                        """

                # STANDARD LOGIC
                elif target_mode == "CO-STAR (General Writing)":
                    system_prompt = f"Act as an Expert Writer. Rewrite using CO-STAR (Context, Objective, Style, Tone, Audience, Response). INPUT: '{raw_prompt}'"
                elif target_mode == "Chain of Thought (Logic/Math)":
                    system_prompt = f"Rewrite this prompt to force the AI to think step-by-step. INPUT: '{raw_prompt}'"
                elif target_mode == "Senior Coder (Python/JS)":
                    system_prompt = f"Act as a Senior Architect. Rewrite into a technical spec. INPUT: '{raw_prompt}'"
                elif target_mode == "Email Polisher (Professional)":
                    system_prompt = f"Act as a Comms Director. Rewrite into a professional email. INPUT: '{raw_prompt}'"
                elif target_mode == "Midjourney/Dal-E (Image Gen)":
                    system_prompt = f"Act as a Digital Artist. Rewrite into a detailed image generation prompt (Lighting, Camera, Style). INPUT: '{raw_prompt}'"
                elif target_mode == "S.M.A.R.T. (Business Goals)":
                    system_prompt = f"Rewrite this goal using the S.M.A.R.T framework (Specific, Measurable, Achievable, Relevant, Time-bound). INPUT: '{raw_prompt}'"
                elif target_mode == "The 5 Ws (News/Reporting)":
                    system_prompt = f"Rewrite this request to ensure it answers: Who, What, Where, When, and Why. INPUT: '{raw_prompt}'"

                # --- 3. EXECUTE ---
                response = generate_with_fallback(model_name, system_prompt)
                
                if response:
                    st.subheader(f"🚀 Result ({target_mode}):")
                    st.code(response.text)

# ==========================================
# TAB 2: THE WEBSITE REPLICATOR (V3)
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
