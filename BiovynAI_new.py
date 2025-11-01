
# BiovynAI_new.py
# BiovynAI v2.1 — Study Mode + Concept Visualizer + Clear Chat + Safe Secrets Redirect
# Model: llama3:3b via Ollama REST

import streamlit as st
import requests, json, time
from urllib.parse import quote_plus

# -------------------------
# Page config & styles
# -------------------------
st.set_page_config(page_title="BiovynAI — Your BioMentor", page_icon="🧬", layout="wide")

st.markdown(
    """
    <style>
    body { background: linear-gradient(180deg,#fbfffb,#f3fff6); }
    .bio-header {display:flex; align-items:center; gap:14px; margin-bottom:8px;}
    .bio-badge {width:64px; height:64px; border-radius:12px; background:linear-gradient(135deg,#8AD29E,#5BB07F); display:flex; align-items:center; justify-content:center; font-weight:700; color:white; font-size:30px;}
    .bio-title {font-size:26px; font-weight:700; color:#083827;}
    .bio-sub {color:#285a47; margin-top:4px; font-size:13px;}
    .chat-box {background:transparent; padding:8px;}
    .user-msg {background:#e8f8ef; padding:10px; border-radius:10px; margin:6px 0;}
    .bot-msg {background:#ffffff; padding:10px; border-radius:10px; margin:6px 0; border:1px solid #e6f4ea;}
    .small-muted {color:#466e58; font-size:13px;}
    .footer {text-align:center; color:#234e3b; margin-top:18px; font-size:14px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
with st.container():
    st.markdown(
        """
        <div class="bio-header">
            <div class="bio-badge">B</div>
            <div>
                <div class="bio-title">BiovynAI — Your BioMentor</div>
                <div class="bio-sub">Study Mode • Concept Visualizer (on demand) • Friendly tutor for biology learners</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("---")

# -------------------------
# Sidebar controls
# -------------------------
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["Study Mode", "Chat Mode"], index=0)
    st.text_input("Ollama model", value="llama3:3b", key="ollama_model")
    st.markdown("---")
    st.markdown("**Pro idea:** Quiz Mode & Analytics → coming in future release 🌿")
    st.markdown("---")
    st.markdown("App auto-detects Ollama endpoint via Streamlit secrets or localhost.")

# -------------------------
# Session state defaults
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "last_visual" not in st.session_state:
    st.session_state.last_visual = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# -------------------------
# Endpoint config (with safe redirect)
# -------------------------
OLLAMA_URL = st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")

# -------------------------
# Helpers
# -------------------------
def call_ollama_generate(prompt, model="llama3:3b", timeout=60):
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            if "response" in data:
                return data["response"].strip()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("message", {}).get("content", "").strip()
            return json.dumps(data)
        return str(data)
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")

def compose_prompt(messages, mode):
    if mode == "Study Mode":
        preface = (
            "You are BiovynAI, a friendly biology tutor. "
            "Explain clearly and step-by-step using analogies. End with 'Summary:' and a follow-up question.\n\n"
        )
    else:
        preface = "You are BiovynAI, a concise biology assistant. Provide short, accurate responses.\n\n"

    convo = ""
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "user":
            convo += f"User: {content}\n"
        else:
            convo += f"Assistant: {content}\n"
    return preface + convo + "\nAssistant:"

def svg_placeholder(text="No image"):
    return f"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'><rect width='100%' height='100%' fill='#f3fff6'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='20' fill='#246b4a'>{quote_plus(text)}</text></svg>"

@st.cache_data(show_spinner=False)
def find_wikipedia_image(query):
    try:
        q = quote_plus(query.strip())
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{q}"
        r = requests.get(summary_url, timeout=8)
        if r.ok:
            jr = r.json()
            if "thumbnail" in jr and jr["thumbnail"].get("source"):
                return jr["thumbnail"]["source"]
            if jr.get("originalimage", {}) and jr["originalimage"].get("source"):
                return jr["originalimage"]["source"]
        return None
    except Exception:
        return None

# -------------------------
# Layout
# -------------------------
col_main, col_visual = st.columns([2.3, 1])

with col_main:
    if st.button("🗑️ Clear Chat"):
        st.session_state.history = []
        st.session_state.last_visual = None
        st.srerun()

with col_main:
    st.subheader("Ask BiovynAI anything about biology 🌿")
    user_input = st.text_area("Your question", placeholder="E.g., Explain lac operon or Tell me about DNA replication", height=110)
    submit = st.button("Ask BiovynAI")

with col_visual:
    st.markdown("### Visual (on demand)")
    if st.session_state.last_visual:
        st.image(st.session_state.last_visual, use_column_width=True)
    else:
        st.image(svg_placeholder("Visual will appear here"), use_column_width=True)

with col_main:
    for i, msg in enumerate(st.session_state.history):
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'><strong>You:</strong> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'><strong>BiovynAI:</strong> {msg['content']}</div>", unsafe_allow_html=True)
            if st.button("🧠 Show Diagram", key=f"show_{i}"):
                last_user = None
                for j in range(i-1, -1, -1):
                    if st.session_state.history[j]["role"] == "user":
                        last_user = st.session_state.history[j]["content"]
                        break
                if last_user:
                    with st.spinner("Searching for a helpful diagram..."):
                        img_url = find_wikipedia_image(last_user.split(".")[0])
                        st.session_state.last_visual = img_url or svg_placeholder("No image found")
                        st.rerun()

if submit and user_input.strip():
    st.session_state.history.append({"role": "user", "content": user_input.strip()})
    with st.spinner("BiovynAI is thinking..."):
        try:
            prompt = compose_prompt(st.session_state.history, mode)
            reply = call_ollama_generate(prompt, model=st.session_state.get("ollama_model", "llama3:3b"))
            st.session_state.history.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error: {e}")
    st.rerun()

# -------------------------
# Footer
# -------------------------
st.write("---")
st.markdown("<div class='footer'>Powered by BiovynAI — Created with love by Gunjan 💚</div>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Made with curiosity • For learners • v2.1</div>", unsafe_allow_html=True)