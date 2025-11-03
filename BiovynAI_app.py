# BiovynAI_app.py
import streamlit as st
from backend import get_biovyn_response, generate_bio_diagram

st.sidebar.success("✅ Frontend ↔ Backend connection confirmed")



# ─────────────────────────────
# 🌿 SETUP
# ─────────────────────────────
st.set_page_config(page_title="BiovynAI", page_icon="🧬", layout="wide")

# ─────────────────────────────
# 🌈 CUSTOM STYLING
# ─────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #b3f3b3, #b3e0f5);
    color: white;
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
# 💬 HEADER
# ─────────────────────────────
st.markdown("<h2 style='text-align:center; color:#003366;'>BiovynAI 🧬🧠</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#1a1a1a;'>Ask BiovynAI anything about Biology 🧬</p>", unsafe_allow_html=True)

# ─────────────────────────────
# 🌱 SESSION STATE
# ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "study_mode" not in st.session_state:
    st.session_state.study_mode = False
if "loading" not in st.session_state:
    st.session_state.loading = False
if "clear_input_next_run" not in st.session_state:
    st.session_state.clear_input_next_run = False

if st.session_state.get("clear_input_next_run", False):
    st.session_state["user_input"] = ""
    st.session_state["clear_input_next_run"] = False

# ─────────────────────────────
# 💬 CHAT DISPLAY
# ─────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# ─────────────────────────────
# 🧠 USER INPUT
# ─────────────────────────────
with st.container():
    disabled = st.session_state.loading
    user_input = st.text_input(
        "You:",
        placeholder="Ask BiovynAI anything about Biology 🧬",
        key="user_input",
        disabled=disabled
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        study_mode = st.toggle("🎓 Study Mode", value=st.session_state.study_mode, disabled=disabled)
    with col2:
        clear_chat = st.button("🗑️ Clear Chat", disabled=disabled)
    with col3:
        show_diagram_button = False

# ─────────────────────────────
# 🧠 CHAT LOGIC
# ─────────────────────────────
if clear_chat:
    st.session_state.messages = []
    st.session_state["user_input"] = ""
    st.rerun()

if user_input and not st.session_state.loading:
    st.session_state.loading = True
    st.session_state.study_mode = study_mode
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking... 🧠"):
        reply = get_biovyn_response(user_input, study_mode)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state["clear_input_next_run"] = True
    st.session_state.loading = False
    st.rerun()

# ─────────────────────────────
# 🌿 SMART DIAGRAM BUTTON
# ─────────────────────────────
bio_keywords = [
    "cell", "dna", "rna", "photosynthesis", "mitochondria", "nucleus",
    "chloroplast", "neuron", "heart", "brain", "respiration", "ecosystem",
    "enzyme", "protein", "gene", "plant", "virus", "bacteria"
]

if st.session_state.messages:
    last_msg = st.session_state.messages[-1]["content"]
    last_msg_lower = last_msg.lower()

    if any(word in last_msg_lower for word in bio_keywords):
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧠 Show Diagram for Last Topic"):
            diagram = generate_bio_diagram(last_msg)
            if isinstance(diagram, bytes):
                st.image(diagram, caption=f"Diagram: {last_msg}", use_column_width=True)
            elif isinstance(diagram, str):
                st.image(diagram, caption=f"Example Diagram: {last_msg}", use_column_width=True)
            else:
                st.image(diagram, caption=f"Fallback Diagram: {last_msg}", use_column_width=True)


# --- Add export/download chat button (place where you want it in the UI) ---
def _format_messages_for_export(messages):
    lines = []
    for m in messages:
        role = "You" if m["role"] == "user" else "BiovynAI"
        lines.append(f"{role}: {m['content']}\n")
    return "\n".join(lines)

if st.session_state.get("messages"):
    # Show a small download button to export the current chat
    chat_text = _format_messages_for_export(st.session_state.messages)
    st.download_button(
        label="📥 Download Chat (TXT)",
        data=chat_text,
        file_name="biovynai_chat.txt",
        mime="text/plain"
    )




# ─────────────────────────────
# 💚 FOOTER
# ─────────────────────────────
st.markdown("<br><hr><p style='text-align:center;'>💚 Powered by BiovynAI — Created with love by Gunjan 💚</p>", unsafe_allow_html=True)
