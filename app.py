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

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("⚙️ Engine Room")
    api_key = st.text_input("🔑 Paste Gemini API Key:", type="password")
    
    st.divider()
    
    # SMART MODEL SELECTOR
    st.subheader("🧠 AI Brain Power")
    model_name = st.text_input("Model Name:", value="gemini-1.5-flash")
    st.caption("Tip: Use `gemini-2.0-flash-exp` if your key supports it.")
    
    # DEBUGGER
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

    st.divider()
    st.info("Created with the 'No-Code' Guide.")

# --- MAIN APP ---
st.title("⚡ God-Mode AI Suite")
st.markdown("Two powerful tools in one app. Select a tab below.")

if not api_key:
    st.warning("⬅️ Waiting for API Key in the sidebar...")
    st.stop()

# Configure AI Globally
genai.configure(api_key=api_key)

# --- TABS FOR TOOLS ---
tab1, tab2 = st.tabs(["✨ Prompt Enhancer (Writer)", "🕷️ Website Replicator (Builder)"])

# ==========================================
# TOOL 1: THE PROMPT ENHANCER
# ==========================================
with tab1:
    st.header("✨ Turn Lazy Ideas into Gold")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # EXPANDED OPTIONS
        mode = st.selectbox(
            "Choose Enhancement Mode:",
            [
                "CO-STAR (Best for General Text)", 
                "Chain of Thought (Best for Logic/Math)", 
                "Senior Coder (Best for Python/JS)",
                "Email Polisher (Best for Professionalism)",
                "Midjourney/Dal-E (Best for Image Gen)"
            ]
        )
    
    raw_prompt = st.text_area("Your Draft:", height=200, placeholder="e.g., write a marketing plan for coffee...")

    if st.button("✨ Enhance Prompt", type="primary"):
        if not raw_prompt:
            st.warning("Type something first!")
        else:
            try:
                model = genai.GenerativeModel(model_name)
                with st.spinner("Engineering your prompt..."):
                    
                    # DEFINING THE "BRAINS" FOR EACH MODE
                    prompts = {
                        "CO-STAR (Best for General Text)": f"""
                        Act as an Expert Prompt Engineer. Rewrite this using the CO-STAR framework (Context, Objective, Style, Tone, Audience, Response).
                        INPUT: "{raw_prompt}"
                        OUTPUT: The rewritten prompt in a code block.
                        """,
                        
                        "Chain of Thought (Best for Logic/Math)": f"""
                        Rewrite this prompt to force the AI to think step-by-step.
                        INPUT: "{raw_prompt}"
                        OUTPUT: A prompt that instructs the AI to 'Take a deep breath' and 'Show reasoning before the answer'.
                        """,
                        
                        "Senior Coder (Best for Python/JS)": f"""
                        Act as a Senior Software Architect. Rewrite this request into a technical specification.
                        INPUT: "{raw_prompt}"
                        OUTPUT: A prompt asking for clean code, error handling, and comments.
                        """,
                        
                        "Email Polisher (Best for Professionalism)": f"""
                        Act as a Communications Director. Rewrite this draft into a polite, professional, and clear email prompt.
                        INPUT: "{raw_prompt}"
                        OUTPUT: A prompt that asks the AI to write the final email.
                        """,
                        
                        "Midjourney/Dal-E (Best for Image Gen)": f"""
                        Act as a Digital Artist. Rewrite this idea into a detailed image generation prompt.
                        INPUT: "{raw_prompt}"
                        OUTPUT: A prompt including lighting, style (e.g. Cyberpunk), camera angles, and rendering engine details (e.g. Unreal Engine 5).
                        """
                    }
                    
                    response = model.generate_content(prompts[mode])
                    st.subheader("🚀 Result:")
                    st.code(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# TOOL 2: THE WEBSITE REPLICATOR (V3)
# ==========================================
with tab2:
    st.header("🕷️ Clone a Website's Soul")
    
    # Initialize Session State
    if 'scraped_text' not in st.session_state:
        st.session_state.scraped_text = ""
    if 'site_title' not in st.session_state:
        st.session_state.site_title = ""

    # INPUT URL
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

    # REFINEMENT FORM
    if st.session_state.scraped_text:
        st.divider()
        st.subheader("2️⃣ Director's Cut (Customize It)")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            role = st.text_input("Role:", placeholder="SaaS, Portfolio, Store")
        with c2:
            vibe = st.text_input("Vibe:", placeholder="Dark, Minimal, Colorful")
        with c3:
            # Dropdown for Tech Stack
            stack = st.selectbox("Tech Stack:", ["Next.js + Tailwind + Framer", "HTML + CSS + JS", "Vue.js + Tailwind", "React + Three.js (3D)"])

        # THE MAGIC BOX
        magic = st.text_area("✨ Describe the Magic (Animations/Interactions):", 
                             placeholder="IMPORTANT: Describe what moves. e.g., 'A 3D cube spins on hover', 'Text fades in on scroll'.")

        if st.button("🚀 Generate Replicator Prompt", type="primary"):
            try:
                model = genai.GenerativeModel(model_name)
                with st.spinner("Synthesizing Code Strategy..."):
                    
                    final_prompt = f"""
                    Act as a Senior Frontend Architect.
                    TASK: Create a system prompt for an AI Coding Agent (Cursor/v0) to REPLICATE this website.
                    
                    ### 1. SOURCE DATA
                    * **Title:** {st.session_state.site_title}
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
                    3. Structure the Scraped Content into a beautiful layout matching the '{vibe}'.
                    
                    OUTPUT: Provide ONLY the prompt in a code block.
                    """
                    
                    response = model.generate_content(final_prompt)
                    st.subheader("🧬 Your Master Prompt:")
                    st.code(response.text, language='markdown')
            except Exception as e:
                st.error(f"Error: {e}")
