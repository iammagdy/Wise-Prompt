import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# --- PAGE SETUP ---
st.set_page_config(page_title="God-Mode Enhancer", page_icon="⚡", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Paste Gemini API Key:", type="password")
    
    # NEW: Mode Selector
    mode = st.radio("Select Mode:", ["✨ Text Prompt Enhancer", "🕷️ Website Replicator"])
    
    st.markdown("---")
    if st.button("🐞 Check Available Models"):
        if not api_key:
            st.error("Paste API key first!")
        else:
            try:
                genai.configure(api_key=api_key)
                st.write("**Your Valid Models:**")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except Exception as e:
                st.error(f"Error: {e}")

# --- MAIN APP ---
st.title("⚡ God-Mode AI Suite")

if not api_key:
    st.warning("⬅️ Please paste your Gemini API Key in the sidebar to start.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash') # Or 'gemini-pro' if flash fails

# ==========================================
# MODE 1: STANDARD PROMPT ENHANCER
# ==========================================
if mode == "✨ Text Prompt Enhancer":
    st.subheader("Turn lazy ideas into engineering-grade prompts.")
    
    col1, col2 = st.columns(2)
    with col1:
        framework = st.selectbox("Style:", ["CO-STAR (Best for Text)", "Chain of Thought (Logic)", "Python Expert (Code)"])
    with col2:
        model_name = st.text_input("Model Name (Optional):", value="gemini-1.5-flash")

    raw_prompt = st.text_area("Your Lazy Draft:", height=200, placeholder="e.g., write a marketing plan for coffee...")

    if st.button("✨ Enhance Prompt", type="primary"):
        if not raw_prompt:
            st.warning("Enter a prompt first.")
        else:
            try:
                if model_name: model = genai.GenerativeModel(model_name)
                
                with st.spinner("Engineering your prompt..."):
                    meta_prompts = {
                        "CO-STAR (Best for Text)": f"""
                        Act as an Expert Prompt Engineer. Rewrite this using the CO-STAR framework.
                        Input: "{raw_prompt}"
                        Output: The rewritten prompt in a code block.
                        """,
                        "Chain of Thought (Logic)": f"""
                        Rewrite to force step-by-step logic.
                        Input: "{raw_prompt}"
                        Output: A prompt that requires "Step-by-step reasoning".
                        """,
                        "Python Expert (Code)": f"""
                        Act as a Senior Dev. Rewrite for Python.
                        Input: "{raw_prompt}"
                        Output: Technical spec prompt.
                        """
                    }
                    response = model.generate_content(meta_prompts[framework])
                    st.subheader("🚀 Result:")
                    st.code(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# MODE 2: WEBSITE REPLICATOR (NEW!)
# ==========================================
elif mode == "🕷️ Website Replicator":
    st.subheader("Clone a website's style and structure.")
    st.info("Enter a URL, and I will write a prompt to help you build a clone of it.")

    target_url = st.text_input("Enter Website URL (e.g., https://example.com):")

    if st.button("🕷️ Crawl & Generate Super-Prompt", type="primary"):
        if not target_url:
            st.warning("Please enter a URL.")
        else:
            try:
                with st.spinner("🕷️ Crawling website content... (This might take 10s)"):
                    # 1. Scrape the website
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    page = requests.get(target_url, headers=headers, timeout=10)
                    soup = BeautifulSoup(page.content, 'html.parser')
                    
                    # Get text (limit to 10,000 chars to fit in memory)
                    site_text = soup.get_text(separator=' ', strip=True)[:10000]
                    
                with st.spinner("🧠 Analyzing design & structure..."):
                    # 2. Ask Gemini to analyze it
                    analysis_prompt = f"""
                    Act as a Senior UI/UX Designer and Frontend Developer.
                    I have scraped the text content of a website below.
                    
                    YOUR TASK:
                    Write a comprehensive "System Prompt" that I can give to an AI coding agent (like Cursor, v0, or ChatGPT) to REPLICATE this website.
                    
                    The prompt you write must describe:
                    1. The Vibe/Aesthetics (guess colors/fonts based on content tone).
                    2. The Structure (Hero, Features, Footer, etc.).
                    3. The Content Strategy.
                    4. The exact technical instruction to build it (HTML/Tailwind/React).
                    
                    SCRAPED WEBSITE CONTENT:
                    "{site_text}"
                    
                    OUTPUT:
                    Provide ONLY the prompt I should use, inside a code block.
                    """
                    
                    response = model.generate_content(analysis_prompt)
                    
                    st.success("Analysis Complete! Copy the prompt below to build your clone.")
                    st.subheader("🧬 The Replication Prompt:")
                    st.code(response.text, language='markdown')
                    
            except Exception as e:
                st.error(f"Could not crawl site. It might be blocking bots. Error: {e}")
