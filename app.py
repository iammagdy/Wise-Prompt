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

# --- HELPER FUNCTION: SELF-HEALING AI ---
def generate_with_fallback(user_model_name, prompt):
    """
    Tries the user's selected model. If it fails (404), 
    it automatically switches to 'gemini-pro' to save the crash.
    """
    try:
        # 1. Try User's Choice
        model = genai.GenerativeModel(user_model_name)
        return model.generate_content(prompt)
    except Exception as e:
        # 2. Check for 404 (Model Not Found)
        if "404" in str(e) or "not found" in str(e).lower():
            st.warning(f"⚠️ Model '{user_model_name}' not found. Switching to backup 'gemini-pro'...")
            try:
                # 3. Try Backup
                backup_model = genai.GenerativeModel("gemini-pro")
                return backup_model.generate_content(prompt)
            except Exception as e2:
                st.error(f"❌ Backup failed too. Your API Key might be invalid. Error: {e2}")
                return None
        else:
            # Real error (like Policy Violation)
            st.error(f"❌ Error: {e}")
            return None

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("⚙️ Engine Room")
    api_key = st.text_input("🔑 Paste Gemini API Key:", type="password")
    
    st.divider()
    
    # SMART MODEL SELECTOR
    st.subheader("🧠 AI Brain Power")
    # CHANGED DEFAULT to 'gemini-pro' as it is the most stable
    model_name = st.text_input("Model Name:", value="gemini-pro") 
    st.caption("If 'flash' fails, we auto-switch to 'pro'.")
    
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
        mode = st.selectbox(
            "Choose Enhancement Mode:",
            [
                "CO-STAR (Best for General Text)", 
                "Chain of Thought (Best for Logic/Math)", 
                "Senior Coder (Best for Python/JS)",
                "Email Polisher (Best for Professionalism)",
                "Midjourney/Dal-E (Best for Image Gen)",
                "Custom Persona (Define your own Agent)"
            ]
        )
        
        agent_name = "Expert Prompt Engineer"
        if mode == "Custom Persona (Define your own Agent)":
            agent_name = st.text_input("Who should the AI act as?", placeholder="e.g. Steve Jobs, Elon Musk")

    raw_prompt = st.text_area("Your Draft:", height=200, placeholder="e.g., write a marketing plan for coffee...")

    if st.button("✨ Enhance Prompt", type="primary"):
        if not raw_prompt:
            st.warning("Type something first!")
        else:
            with st.spinner("Engineering your prompt..."):
                
                # LOGIC
                if mode == "Custom Persona (Define your own Agent)":
                    system_prompt = f"""
                    Act as {agent_name}. Rewrite the following user request exactly how {agent_name} would handle it.
                    INPUT: "{raw_prompt}"
                    OUTPUT: The rewritten prompt in a code block.
                    """
                elif mode == "CO-STAR (Best for General Text)":
                    system_prompt = f"""
                    Act as an Expert Prompt Engineer. Rewrite this using the CO-STAR framework (Context, Objective, Style, Tone, Audience, Response).
                    INPUT: "{raw_prompt}"
                    OUTPUT: The rewritten prompt in a code block.
                    """
                elif mode == "Chain of Thought (Best for Logic/Math)":
                    system_prompt = f"""
                    Rewrite this prompt to force the AI to think step-by-step.
                    INPUT: "{raw_prompt}"
                    OUTPUT: A prompt that instructs the AI to 'Take a deep breath' and 'Show reasoning before the answer'.
                    """
                elif mode == "Senior Coder (Best for Python/JS)":
                    system_prompt = f"""
                    Act as a Senior Software Architect. Rewrite this request into a technical specification.
                    INPUT: "{raw_prompt}"
                    OUTPUT: A prompt asking for clean code, error handling, and comments.
                    """
                elif mode == "Email Polisher (Best for Professionalism)":
                    system_prompt = f"""
                    Act as a Communications Director. Rewrite this draft into a polite, professional, and clear email prompt.
                    INPUT: "{raw_prompt}"
                    OUTPUT: A prompt that asks the AI to write the final email.
                    """
                elif mode == "Midjourney/Dal-E (Best for Image Gen)":
                    system_prompt = f"""
                    Act as a Digital Artist. Rewrite this idea into a detailed image generation prompt.
                    INPUT: "{raw_prompt}"
                    OUTPUT: A prompt including lighting, style, camera angles, and rendering engine details.
                    """
                
                # EXECUTE WITH SELF-HEALING
                response = generate_with_fallback(model_name, system_prompt)
                
                if response:
                    st.subheader("🚀 Result:")
                    st.code(response.text)

# ==========================================
# TOOL 2: THE WEBSITE REPLICATOR (V3)
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
                
                # EXECUTE WITH SELF-HEALING
                response = generate_with_fallback(model_name, final_prompt)
                
                if response:
                    st.subheader("🧬 Your Master Prompt:")
                    st.code(response.text, language='markdown')
