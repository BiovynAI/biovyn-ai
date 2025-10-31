
import streamlit as st
from openai import OpenAI

st.markdown("""
    <style>
        /* 🌿 Background gradient */
        .stApp {
            background: linear-gradient(180deg, #e8f9f2 0%, #d8efff 100%) !important;
        }

        /* ✨ Universal text color + font */
        html, body, [class*="st"], h1, h2, h3, h4, p, span, div {
            color: #114b3e !important;
            font-family: 'Segoe UI', sans-serif !important;
        }

        /* 💚 Title styling */
        h1 {
            text-align: center;
            color: #10684a !important;
            font-size: 2.4rem;
            margin-bottom: 0.2rem;
            font-weight: 600;
        }

        h3, .stCaption {
            text-align: center;
            color: #2d5d83 !important;
            font-weight: normal;
            font-size: 1rem;
            margin-top: 0;
        }

        /* 💬 Chat bubbles */
        div[data-testid="stChatMessage"] {
            border-radius: 18px !important;
            padding: 12px 16px !important;
            margin-bottom: 10px !important;
            max-width: 80%;
            word-wrap: break-word;
            font-size: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        /* User message bubble */
        div[data-testid="stChatMessage"][data-testid="user"] {
            background-color: #c2f0d4 !important;
            align-self: flex-end !important;
            margin-left: auto !important;
        }

        /* Assistant message bubble */
        div[data-testid="stChatMessage"][data-testid="assistant"] {
            background-color: #ffffff !important;
            align-self: flex-start !important;
            margin-right: auto !important;
        }

        /* 🌿 Chat input area */
        div[data-testid="stChatInputContainer"] {
            background-color: #f6fff9 !important;
            border-top: 2px solid #bce8d6 !important;
            padding: 10px 16px !important;
        }

        /* 🩵 Actual text input field */
        textarea[data-testid="stChatInputTextArea"] {
            background-color: #ffffff !important;
            color: #114b3e !important;
            border: 1.5px solid #bce8d6 !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            padding: 10px !important;
        }

        /* 🌸 Placeholder color */
        textarea[data-testid="stChatInputTextArea"]::placeholder {
            color: #6b8e7b !important;
            opacity: 0.8 !important;
        }

        /* 💚 Send button styling */
        button[kind="secondaryFormSubmit"] {
            background-color: #bce8d6 !important;
            color: #114b3e !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: 0.2s ease !important;
        }
        button[kind="secondaryFormSubmit"]:hover {
            background-color: #9bdcc3 !important;
        }

        /* 🌼 Footer */
        footer {visibility: hidden;}
        .footer {
            text-align: center;
            color: #2e3f48 !important;
            font-size: 0.9rem;
            margin-top: 3rem;
            opacity: 0.8;
        }
    </style>
""", unsafe_allow_html=True)

# --- SETUP ---
st.set_page_config(page_title="Biobot Chat", page_icon="🤖", layout="centered")
import os

# ✅ Load key securely from Streamlit secrets or environment variable
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    st.error("⚠️ OpenAI API key not found. Please add it in Streamlit → Settings → Secrets.")
else:
    # ✅ Create the OpenAI client safely
    client = OpenAI(api_key=OPENAI_KEY)

st.markdown("<h1>🌿 Biovyn AI</h1>", unsafe_allow_html=True)
st.markdown("<h3>Your Intelligent Biology Companion</h3>", unsafe_allow_html=True)

# --- MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello ! I'm Biovyn AI — your biology companion 💚"}
    ]

# --- DISPLAY CHAT ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask Biobot something..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking like a biologist 🧬..."):
            # ✅ Now 'client' exists, no NameError!
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Biobot, a kind, smart biology tutor for students. Explain clearly and naturally."},
                    *st.session_state.messages,
                ],
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# --- CLEAR CHAT BUTTON ---
if st.button("🧹 Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Chat cleared! Hello again, I'm Biovyn AI 💚"}
    ]
    st.rerun()  # ✅ fixed typo (was srerun)

# --- FOOTER ---
st.markdown(
    """
    <div class='footer'>
        🌿 Powered by <b>Biovyn AI</b> — Created with love by Gunjan 💚
    </div>
    """,
    unsafe_allow_html=True
)