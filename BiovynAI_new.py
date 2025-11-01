


import streamlit as st
import openai
import requests
from PIL import Image
from io import BytesIO

# --- Page setup ---
st.set_page_config(page_title="Biovyn AI", page_icon="🧬", layout="wide")

# --- Load secrets ---
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
OLLAMA_URL = st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")

# --- OpenAI client setup ---
openai.api_key = OPENAI_API_KEY

# --- Custom CSS Styling ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #d8f3dc, #b7e4c7, #74c69d, #95d5b2);
    background-attachment: fixed;
}
.chat-bubble {
    padding: 1rem;
    border-radius: 1rem;
    margin: 0.5rem 0;
    max-width: 80%;
    font-size: 1rem;
}
.user-bubble {
    background-color: #1b4332;
    color: white;
    align-self: flex-end;
}
.bot-bubble {
    background-color: #081c15;
    color: white;
    align-self: flex-start;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #d7f9d7, #d7ecf9);
}
[data-testid="stSidebar"] * {
    color: #003366 !important;
    font-weight: 500;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #002244 !important;
    font-weight: 700;
}
footer {
    text-align: center;
    font-size: 0.9rem;
    color: #004225;
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/88/DNA_icon.png", width=100)
st.sidebar.title("🌿 Biovyn AI")
st.sidebar.markdown("**Ask Biovyn AI anything about Biology!** 🧬")
st.sidebar.divider()
st.sidebar.markdown("✨ **Pro Version Coming Soon!** Unlock quiz mode, voice chat & more! 💚")

# --- App Header ---
st.title("🧬 Biovyn AI")
st.caption("Ask BiovynAI anything about Biology!")

# --- Study Mode Selector ---
study_mode = st.radio("Select Study Mode:", ["Concept Visualizer", "Quick Explain"], horizontal=True)

# --- Chat Container ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Input Box ---
user_input = st.text_input("Type your Biology question here:", "")

# --- Response Function ---
def get_biovyn_response(question, mode):
    prompt = f"Answer this biology question clearly in '{mode}' mode:\n{question}"
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- Generate Diagram Function ---
def generate_biology_diagram(topic):
    try:
        response = openai.images.generate(
            model="gpt-image-1",
            prompt=f"A simple labeled biology diagram of {topic}, scientific but clean and colorful."
        )
        image_url = response.data[0].url
        image_data = requests.get(image_url)
        image = Image.open(BytesIO(image_data.content))
        return image
    except Exception as e:
        st.warning("Couldn't generate diagram right now. Try again later!")
        return None

# --- Chat Logic ---
if user_input:
    reply = get_biovyn_response(user_input, study_mode)
    st.session_state["messages"].append(("user", user_input))
    st.session_state["messages"].append(("bot", reply))
    st.rerun()

# --- Display Chat ---
for role, msg in st.session_state["messages"]:
    if role == "user":
        st.markdown(f"<div class='chat-bubble user-bubble'>🧑‍💬 {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble bot-bubble'>🧬 {msg}</div>", unsafe_allow_html=True)
        if "diagram" not in msg.lower():
            if st.button("🧫 Show Diagram", key=f"diagram_{msg[:15]}"):
                image = generate_biology_diagram(msg)
                if image:
                    st.image(image, caption="Concept Diagram", use_column_width=True)

# --- Clear Chat Button ---
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state["messages"] = []
    st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("<footer>💚 Powered by <b>Biovyn AI</b> — Created with love by <b>Gunjan</b> 💚</footer>", unsafe_allow_html=True)