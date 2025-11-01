


# BiovynAI_new.py — v2.3 (Hybrid Gradient Compact Edition)
# Hybrid: Ollama local (default) + OpenAI cloud (via secrets)
# Visual: full blue->green gradient, compact chat, dark chat bubbles with white text
# Features: Study Mode, Show Diagram (on-demand), Clear Chat, Sidebar with Pro note

import streamlit as st
import requests
import json
import os
from urllib.parse import quote_plus

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="BiovynAI 🧬🧠", page_icon="🧬", layout="wide")

# -------------------------
# CSS / Theme
# Full-page gradient + sidebar softer gradient + chat bubble styles
# -------------------------
st.markdown(
    """
    <style>
    /* Full app gradient */
    .stApp {
        background: linear-gradient(135deg, #E8F5E9 0%, #BBDEFB 100%);
        min-height: 100vh;
    }

    /* Center header */
    .bio-header {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #063E2B;
        padding-top: 8px;
        margin-bottom: 6px;
    }

    /* Subtitle under header */
    .bio-sub {
        text-align: center;
        color: #104E34;
        font-size: 13px;
        margin-bottom: 8px;
    }

    /* Chat layout custom */
    .chat-box { display:flex; flex-direction:column; gap:6px; padding:6px; }

    .user-msg {
        background: linear-gradient(90deg, #0D47A1, #1565C0);
        color: #ffffff;
        padding: 10px 14px;
        border-radius: 14px;
        max-width: 78%;
        align-self: flex-end;
        word-wrap: break-word;
    }
    .ai-msg {
        background: linear-gradient(90deg, #1B5E20, #2E7D32);
        color: #ffffff;
        padding: 10px 14px;
        border-radius: 14px;
        max-width: 78%;
        align-self: flex-start;
        word-wrap: break-word;
    }

    /* Visual column placeholder image style */
    .visual-placeholder { border-radius: 8px; border: 1px solid rgba(0,0,0,0.06); padding: 6px; background: rgba(255,255,255,0.7); }

    /* Sidebar softer gradient */
    .sidebar .stMarkdown {
        background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(232,245,233,0.85));
        border-radius: 10px;
        padding: 12px;
    }

    /* Footer */
    .bio-footer { text-align:center; color:#0b3b2e; margin-top:14px; font-size:14px; }

    /* Buttons spacing */
    .btn-row { display:flex; gap:8px; align-items:center; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Header
# -------------------------
st.markdown("<div class='bio-header'>BiovynAI 🧬🧠</div>", unsafe_allow_html=True)
st.markdown("<div class='bio-sub'>Ask BiovynAI anything about Biology 🧬</div>", unsafe_allow_html=True)
st.write("---")

# -------------------------
# Sidebar (soft gradient) — playful text + pro note + footer
# -------------------------
with st.sidebar:
    st.markdown("## BiovynAI 🧬🧠")
    st.markdown("_Your friendly biology study companion_")
    st.markdown("---")
    st.markdown("**✨ Pro version — coming soon!**")
    st.markdown(
        """
        Interactive quizzes, progress tracking, downloadable study packs, and advanced visual modules will be part of Pro.
        Stay tuned — we'll add early access for testers. 🎓🌿
        """
    )
    st.markdown("---")
    st.markdown("<div style='font-size:13px; color:#114B36'>Tip: Run locally with Ollama for free. Use OpenAI on Cloud for hosted inference.</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:12px; font-weight:600; color:#0b3b2e'>Powered by BiovynAI — Created with love by Gunjan 💚</div>", unsafe_allow_html=True)

# -------------------------
# Session state
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role": "user"/"assistant", "content": str}
if "last_visual" not in st.session_state:
    st.session_state.last_visual = None
if "loading" not in st.session_state:
    st.session_state.loading = False

# -------------------------
# Hybrid config (secrets + env)
# -------------------------
# Priority: ENV var OLLAMA_URL -> st.secrets OLLAMA_URL -> default localhost
OLLAMA_URL = os.environ.get("OLLAMA_URL") or st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")
USE_OPENAI = st.secrets.get("USE_OPENAI", False)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None) or os.environ.get("OPENAI_API_KEY", None)

# Try modern OpenAI client if requested
openai_client = None
if USE_OPENAI:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        openai_client = None  # fallback will use HTTP

# -------------------------
# Helpers: Ollama, OpenAI (modern client + HTTP fallback)
# -------------------------
def call_ollama_generate(prompt, model="llama3:3b", timeout=60):
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout)
        r.raise_for_status()
        # try JSON parse
        try:
            j = r.json()
            if isinstance(j, dict) and "response" in j:
                return j["response"].strip()
            # fallback: try to extract first textual field
            return json.dumps(j)
        except Exception:
            return r.text
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")

def call_openai_chat(prompt, system_prompt, model="gpt-4o-mini", timeout=60):
    # Try modern OpenAI client
    if openai_client is not None:
        try:
            resp = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=700,
                temperature=0.2,
            )
            # Try safe accessing of response text:
            try:
                # Some clients return structured objects
                return resp.choices[0].message["content"]
            except Exception:
                return resp.choices[0].message.content
        except Exception as e:
            # fall through to HTTP fallback
            client_err = str(e)
    else:
        client_err = "modern client not available"

    # HTTP fallback
    if OPENAI_API_KEY is None:
        raise RuntimeError("OpenAI API key not found in secrets (OPENAI_API_KEY).")
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 700,
            "temperature": 0.2,
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"]
    except Exception as e_http:
        raise RuntimeError(f"OpenAI request failed. Client error: {locals().get('client_err','')}; HTTP error: {e_http}")

# -------------------------
# Compose system+conversation prompt
# -------------------------
def compose_prompt(history, user_question, study_mode=True):
    if study_mode:
        system_preface = (
            "You are BiovynAI, a friendly and patient biology tutor. Explain concepts step-by-step, "
            "use simple analogies, provide a short 'Summary' line at the end, and suggest 1 quick follow-up question."
        )
    else:
        system_preface = "You are BiovynAI, a concise biology assistant."

    convo_text = ""
    for m in history:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "user":
            convo_text += f"User: {content}\n"
        else:
            convo_text += f"Assistant: {content}\n"
    convo_text += f"User: {user_question}\nAssistant:"
    full_prompt = convo_text
    return system_preface, full_prompt

# -------------------------
# Wikipedia image finder (cached)
# -------------------------
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
        # fallback: search API
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json&srlimit=1"
        rs = requests.get(search_url, timeout=8)
        if rs.ok:
            js = rs.json()
            hits = js.get("query", {}).get("search", [])
            if hits:
                title = hits[0]["title"]
                title_q = quote_plus(title)
                summary2 = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title_q}"
                r2 = requests.get(summary2, timeout=8)
                if r2.ok:
                    j2 = r2.json()
                    if "thumbnail" in j2 and j2["thumbnail"].get("source"):
                        return j2["thumbnail"]["source"]
                    if j2.get("originalimage", {}) and j2["originalimage"].get("source"):
                        return j2["originalimage"]["source"]
        return None
    except Exception:
        return None

def svg_placeholder(text="No image"):
    return f"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'><rect width='100%' height='100%' fill='#ffffff'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='16' fill='#2E7D32'>{quote_plus(text)}</text></svg>"

# -------------------------
# Layout columns (compact)
# -------------------------
col_main, col_visual = st.columns([2.6, 1])

# Top action row: study toggle + clear chat
with col_main:
    cols = st.columns([0.4, 0.6, 2.0])
    # small spacer, toggle, clear
    with cols[0]:
        pass
    with cols[1]:
        study_mode = st.checkbox("🎓 Study Mode", value=True, help="Study Mode explains step-by-step.")
    with cols[2]:
        if st.button("🗑️ Clear Chat"):
            st.session_state.history = []
            st.session_state.last_visual = None
            st.rerun()

# Main chat input & button
with col_main:
    user_question = st.text_area("Your question", placeholder="E.g., Explain the lac operon, or: Teach me photosynthesis for NEET level", height=110)
    send = st.button("Ask BiovynAI")

# Display visual column (placeholder or last_visual)
with col_visual:
    st.markdown("### Visual (on demand)")
    if st.session_state.last_visual:
        st.image(st.session_state.last_visual, use_column_width=True)
    else:
        st.image(svg_placeholder("Visual will appear here"), use_column_width=True)

# Show chat history as bubbles
with col_main:
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    for i, msg in enumerate(st.session_state.history):
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'><strong>You:</strong> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-msg'><strong>BiovynAI:</strong> {msg['content']}</div>", unsafe_allow_html=True)
            # Show Diagram button per assistant reply
            key = f"show_diagram_{i}"
            if st.button("🧠 Show Diagram", key=key):
                # find last user message prior to this assistant reply
                last_user = None
                for j in range(i-1, -1, -1):
                    if st.session_state.history[j]["role"] == "user":
                        last_user = st.session_state.history[j]["content"]
                        break
                if last_user:
                    with st.spinner("Searching for diagram..."):
                        img = find_wikipedia_image(last_user.split(".")[0].split("?")[0])
                        st.session_state.last_visual = img or svg_placeholder("No image found")
                        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# On submit: call model (hybrid)
if send and user_question and user_question.strip():
    st.session_state.loading = True
    st.session_state.history.append({"role": "user", "content": user_question.strip()})
    try:
        system_prompt, prompt_text = compose_prompt(st.session_state.history, user_question.strip(), study_mode=study_mode)
        # Decide engine
        if USE_OPENAI:
            reply = call_openai_chat(prompt_text, system_prompt)
        else:
            # Ollama: model passed inside call_ollama_generate
            reply = call_ollama_generate(f"{system_prompt}\n\n{prompt_text}", model="llama3:3b")
        st.session_state.history.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Error generating response: {e}")
    finally:
        st.session_state.loading = False
        st.rerun()

# Re-render visual column if updated
with col_visual:
    if st.session_state.last_visual:
        st.image(st.session_state.last_visual, use_column_width=True)

# Footer in main area
st.write("---")
st.markdown("<div class='bio-footer'>Powered by BiovynAI — Created with love by Gunjan 💚</div>", unsafe_allow_html=True)