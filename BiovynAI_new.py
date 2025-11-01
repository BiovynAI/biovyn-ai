import streamlit as st
import requests
from openai import OpenAI
import base64
import io

# ─────────────────────────────
# 🌿 SETUP
# ─────────────────────────────
st.set_page_config(page_title="BiovynAI", page_icon="🧬", layout="wide")

# Initialize OpenAI client using Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Ollama Local Model URL
OLLAMA_URL = st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")

# ─────────────────────────────
# 🌈 CUSTOM STYLING
# ─────────────────────────────
st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #b3f3b3, #b3e0f5);
    color: white;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #d7f9d7, #d7ecf9);
}

/* Sidebar text readability fix */
[data-testid="stSidebar"] * {
    color: #003366 !important;
    font-weight: 500;
}

[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #002244 !important;
    font-weight: 700;
}

/* Chat bubble styles */
.user-bubble {
    background-color: #176d4e;
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 5px;
    width: fit-content;
    max-width: 80%;
}
.bot-bubble {
    background-color: #1e3a8a;
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 5px;
    width: fit-content;
    max-width: 80%;
}

/* Study mode button fix */
button[kind="primary"] {
    color: white !important;
    background-color: #2563eb !important;
    border-radius: 10px !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# 🧭 SIDEBAR
# ─────────────────────────────
st.sidebar.markdown("## 🧬 BiovynAI — Your Biology Study Companion")
st.sidebar.write("Hello explorer! 🌱 I'm BiovynAI — your pocket biologist trained to make every concept in life science crystal clear 🧠✨")
st.sidebar.divider()
st.sidebar.write("✨ **Pro version** with interactive quiz & visual modules *coming soon!* 🌿💡")
st.sidebar.markdown("<br><sub>💚 Powered by BiovynAI — Created with love by Gunjan 💚</sub>", unsafe_allow_html=True)

# ─────────────────────────────
# 💬 CHAT UI HEADER
# ─────────────────────────────
st.markdown("<h2 style='text-align:center;'>BiovynAI 🧬🧠</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Ask BiovynAI anything about Biology 🧬</p>", unsafe_allow_html=True)

# ─────────────────────────────
# 🌱 SESSION STATE SETUP
# ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "study_mode" not in st.session_state:
    st.session_state.study_mode = False

# ─────────────────────────────
# 🧠 AI RESPONSE FUNCTION
# ─────────────────────────────
def get_biovyn_response(prompt, study_mode=False):
    """Hybrid AI: First tries Ollama, falls back to OpenAI."""
    try:
        # Try Ollama (local)
        response = requests.post(OLLAMA_URL, json={
            "model": "llama3:3b",
            "prompt": prompt,
        })
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass

    # Fallback: OpenAI GPT-4o-mini
    if study_mode:
        prompt = f"Explain this in a more educational and structured way: {prompt}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are BiovynAI, a biology expert who explains clearly and kindly."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content

# ─────────────────────────────
# 🔬 DIAGRAM GENERATION FUNCTION
# ─────────────────────────────
def generate_bio_diagram(prompt):
    """Generate a biology-related diagram using OpenAI image API."""
    with st.spinner("Generating diagram... 🧬"):
        try:
            image_prompt = f"Detailed labeled biology diagram of {prompt}, educational, colorful, clean layout"
            result = client.images.generate(
                model="gpt-image-1",
                prompt=image_prompt,
                size="512x512"
            )
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            st.image(image_bytes, caption=f"Diagram: {prompt}", use_column_width=False)
        except Exception as e:
            st.warning("Hmm... can't draw that one right now 🧩")

# ─────────────────────────────
# 💬 MAIN CHAT AREA
# ─────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# ─────────────────────────────
# 🧠 USER INPUT SECTION
# ─────────────────────────────
with st.container():
    user_input = st.text_input("You:", placeholder="Ask BiovynAI anything about Biology 🧬", key="input")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        study_mode = st.toggle("🎓 Study Mode", value=st.session_state.study_mode)
    with col2:
        clear_chat = st.button("🗑️ Clear Chat")
    with col3:
        show_diagram_button = False  # will be updated dynamically

# ─────────────────────────────
# 🧠 HANDLE INPUT & CHAT LOGIC
# ─────────────────────────────
if clear_chat:
    st.session_state.messages = []
    st.rerun()

if user_input:
    st.session_state.study_mode = study_mode
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = get_biovyn_response(user_input, study_mode)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    
    # --- Safe Input Reset Fix ---
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state["messages"] = []
    # safely clear the input field
    if "user_input" in st.session_state:
        st.session_state["user_input"] = ""
     st.rerun()

# ─────────────────────────────
# 🌿 SMART DIAGRAM BUTTON
# ─────────────────────────────
bio_keywords = ["cell", "dna", "rna", "photosynthesis", "mitochondria", "nucleus",
                "chloroplast", "neuron", "heart", "brain", "respiration", "ecosystem",
                "enzyme", "protein", "gene", "plant", "virus", "bacteria"]

if st.session_state.messages:
    last_msg = st.session_state.messages[-1]["content"].lower()
    if any(word in last_msg for word in bio_keywords):
        show_diagram_button = True

if show_diagram_button:
    if st.button("🧠 Show Diagram"):
        generate_bio_diagram(last_msg)

# ─────────────────────────────
# 💚 FOOTER
# ─────────────────────────────
st.markdown("<br><hr><p style='text-align:center;'>💚 Powered by BiovynAI — Created with love by Gunjan 💚</p>", unsafe_allow_html=True)