import streamlit as st
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="My Prompt Enhancer", page_icon="⚡")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Paste your Gemini API Key:", type="password")
    
    # DEBUGGER: This button checks what models you have access to
    if st.button("🐞 Check Available Models"):
        if not api_key:
            st.error("Paste API key first!")
        else:
            try:
                genai.configure(api_key=api_key)
                st.write("---")
                st.write("**Your Valid Models:**")
                # This asks Google for the list
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except Exception as e:
                st.error(f"Error: {e}")

# --- MAIN APP ---
st.title("⚡ My Personal Prompt Enhancer")
st.info("If you get a 404 error, use the sidebar button to find the correct model name.")

# 1. Paste the Model Name here (Copy it from the sidebar result)
model_name = st.text_input("Enter Model Name (e.g., gemini-1.5-flash):", value="gemini-1.5-flash")

raw_prompt = st.text_area("Type your lazy idea here:", height=150)

if st.button("✨ Enhance My Prompt", type="primary"):
    if not api_key:
        st.error("⚠️ Missing API Key")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # Use the model name you typed in the box
            model = genai.GenerativeModel(model_name)
            
            with st.spinner("Engineering your prompt..."):
                # Simple CO-STAR Framework
                response = model.generate_content(f"""
                Act as an Expert Prompt Engineer. Rewrite this using the CO-STAR framework.
                Input: "{raw_prompt}"
                Output: The rewritten prompt in a code block.
                """)
                st.code(response.text)
                
        except Exception as e:
            st.error(f"Error: {e}")
