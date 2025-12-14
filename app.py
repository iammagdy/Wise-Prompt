import streamlit as st
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="My Prompt Enhancer", page_icon="⚡")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("⚙️ App Settings")
    # This box is where you paste the key from Phase 1
    api_key = st.text_input("Paste your Gemini API Key here:", type="password")
    
    # Dropdown menu to choose the style
    framework = st.selectbox(
        "Choose Enhancement Style:", 
        ["CO-STAR (Best for General Text)", "Chain of Thought (Best for Logic)", "Python Coder (Best for Code)"]
    )

# --- MAIN PAGE ---
st.title("⚡ My Personal Prompt Enhancer")
st.write("Turn a lazy idea into a professional AI instruction.")

# The box where you type your draft
raw_prompt = st.text_area("Type your lazy idea here:", height=150, placeholder="Example: write an email to my boss asking for a raise...")

# --- THE AI BRAIN ---
if st.button("✨ Enhance My Prompt", type="primary"):
    
    # 1. Check if the key is missing
    if not api_key:
        st.error("⚠️ Stop! You forgot to paste your API Key in the sidebar on the left.")
    
    # 2. Check if the prompt is missing
    elif not raw_prompt:
        st.warning("⚠️ Please type something in the box first.")
        
    # 3. Run the AI
    else:
        try:
            # Connect to Google
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            # The Secret Instructions (Meta-Prompts)
            meta_prompts = {
                "CO-STAR (Best for General Text)": f"""
                Act as an Expert Prompt Engineer. Rewrite the user's raw idea into the CO-STAR framework.
                
                USER'S RAW IDEA: "{raw_prompt}"
                
                INSTRUCTIONS:
                1. Context: Add a realistic background.
                2. Objective: Clearly define the task.
                3. Style: Make it professional.
                4. Tone: Make it clear and direct.
                5. Audience: Define who is reading this.
                6. Response: Specify the format (e.g., text, table).
                
                OUTPUT: Return ONLY the rewritten prompt inside a code block.
                """,
                
                "Chain of Thought (Best for Logic)": f"""
                Rewrite this prompt to force the AI to think step-by-step.
                USER'S RAW IDEA: "{raw_prompt}"
                Output a prompt that instructs the AI to: "Think step by step" and "Explain your reasoning before giving the answer."
                """,
                
                "Python Coder (Best for Code)": f"""
                Act as a Senior Python Developer. Rewrite this request into a technical spec.
                USER'S RAW IDEA: "{raw_prompt}"
                Ensure the new prompt asks for: Error handling, comments, and clean code.
                """
            }

            # Show a loading spinner
            with st.spinner("Engineering your prompt..."):
                response = model.generate_content(meta_prompts[framework])
                
            # Show the result
            st.subheader("🚀 Copy This Result:")
            st.code(response.text)
            st.success("Now copy the text above and paste it into ChatGPT or Claude!")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
