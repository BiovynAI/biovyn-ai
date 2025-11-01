

import streamlit as st
import requests
import json
import openai
import os

# ==========================
# 🌿 PAGE CONFIG
# ==========================
st.set_page_config(page_title="BiovynAI 🧬🧠", layout="centered")

# ==========================
# 🌈 CUSTOM PAGE STYLE
# ==========================
page_bg = """
<style>
body {
    background: linear-gradient(to bottom right, #C8E6C9, #BBDEFB);
    font-family: 'Helvetica', sans-serif;
}
.chat-bubble-user {
    background-color: #1565C0;
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 75%;
    align-self: flex-end;
}
.chat-bubble-ai {
    background-color: #2E7D32;
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 75%;
    align-self: flex-start;
}
.header {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: #1B5E20;
    margin-bottom: 10px;
}
.footer {
    text-align: center;
    font-size: 14px;
    margin-top: 25px;
    color: rgba(0,0,0,0.6);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ==========================
# 🌿 HEADER
# ==========================
st.markdown("<div class='header'>BiovynAI 🧬🧠</div>", unsafe_allow_html=True)

# ==========================
# 💚 SESSION STATE
# ==========================
if "history" not in st.session_state:
    st.session_state.history = []
if "last_visual" not in st.session_state:
    st.session_state.last_visual = None

# ==========================
# ⚙️ HYBRID MODEL SETUP
# ==========================
USE_OPENAI = st.secrets.get("USE_OPENAI", False)
OLLAMA_URL = os.environ.get("OLLAMA_URL") or st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")

if USE_OPENAI:
    openai.api_key = st.secrets.get("OPENAI_API_KEY")

# ==========================
# 🧠 FUNCTION: GET RESPONSE
# ==========================
def get_biovyn_response(prompt, study_mode=False):
    system_prompt = (
        "You are BiovynAI, a helpful and friendly biology mentor. "
        "Explain with accuracy and simplicity, using analogies and examples."
        if study_mode
        else "You are BiovynAI, a conversational biology assistant."
    )

    if USE_OPENAI:
        # --- Use OpenAI GPT model (for cloud) ---
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message["content"]

    else:
        # --- Use Ollama (local model) ---
        payload = {"model": "llama3:3b", "prompt": f"{system_prompt}\n\n{prompt}"}
        resp = requests.post(OLLAMA_URL, json=payload, stream=False)
        return resp.text.strip()

# ==========================
# 🌿 FUNCTION: FETCH DIAGRAM
# ==========================
def fetch_diagram(query):
    try:
        search = f"https://api.duckduckgo.com/?q={query}+biology+diagram&format=json"
        r = requests.get(search)
        data = r.json()
        if "Image" in data and data["Image"]:
            return data["Image"]
        else:
            return None
    except:
        return None

# ==========================
# 🎓 STUDY MODE TOGGLE
# ==========================
study_mode = st.toggle("🎓 Study Mode", value=True)

# ==========================
# 🗑️ CLEAR CHAT BUTTON
# ==========================
if st.button("🗑️ Clear Chat"):
    st.session_state.history = []
    st.session_state.last_visual = None
    st.rerun()

# ==========================
# 💬 CHAT DISPLAY
# ==========================
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)

# ==========================
# 💡 USER INPUT
# ==========================
user_input = st.chat_input("Ask BiovynAI anything about Biology 🧬")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    reply = get_biovyn_response(user_input, study_mode)
    st.session_state.history.append({"role": "assistant", "content": reply})
    st.rerun()

# ==========================
# 🧠 SHOW DIAGRAM BUTTON
# ==========================
if st.session_state.history:
    if st.button("🧠 Show Diagram"):
        last_query = st.session_state.history[-1]["content"]
        img_url = fetch_diagram(last_query)
        if img_url:
            st.image(img_url, caption="Concept Diagram")
            st.session_state.last_visual = img_url
        else:
            st.warning("No relevant diagram found for this topic.")

# ==========================
# 💚 FOOTER
# ==========================
st.markdown("<div class='footer'>Powered by BiovynAI — Created with love by Gunjan 💚</div>", unsafe_allow_html=True)