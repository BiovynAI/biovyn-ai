# backend.py
import io
import base64
import requests
import matplotlib.pyplot as plt
from PIL import Image
from openai import OpenAI
import streamlit as st

# ─────────────────────────────
# 🌱 CONFIG
# ─────────────────────────────
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
OLLAMA_URL = st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")

# ─────────────────────────────
# 💬 CHAT RESPONSE HANDLER
# ─────────────────────────────
def get_biovyn_response(prompt, study_mode=False):
    """Hybrid AI: Try Ollama first, fallback to OpenAI."""
    try:
        response = requests.post(OLLAMA_URL, json={"model": "llama3:3b", "prompt": prompt}, timeout=10)
        if response.status_code == 200 and "response" in response.json():
            return response.json()["response"].strip()
    except Exception:
        pass

    if study_mode:
        prompt = f"Explain this in a more educational and structured way: {prompt}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are BiovynAI, a biology expert who explains clearly and kindly."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content.strip()


# ─────────────────────────────
# 🔬 DIAGRAM GENERATION HANDLER
# ─────────────────────────────
def generate_bio_diagram(prompt):
    """Generate a biology diagram or reliable placeholder."""
    try:
        image_prompt = f"Detailed labeled biology diagram of {prompt}, educational, colorful, clean layout"
        result = client.images.generate(
            model="gpt-image-1",
            prompt=image_prompt,
            size="1024x1024"
        )
        image_base64 = result.data[0].b64_json
        if image_base64:
            image_bytes = base64.b64decode(image_base64)
            return image_bytes  # return raw image bytes for frontend to display
    except Exception as e:
        print(f"⚠️ Diagram generation failed: {e}")

    # 📌 Fallback placeholder logic
    placeholder_map = {
        "cell": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Animal_cell_structure_en.svg",
        "dna": "https://upload.wikimedia.org/wikipedia/commons/8/87/DNA_chemical_structure.svg",
        "photosynthesis": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Photosynthesis_process_diagram_en.svg",
        "heart": "https://upload.wikimedia.org/wikipedia/commons/5/55/Diagram_of_the_human_heart_%28cropped%29.svg",
        "brain": "https://upload.wikimedia.org/wikipedia/commons/4/44/Diagram_showing_the_main_parts_of_the_brain_CRUK_188.svg",
        "neuron": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Neuron.svg",
        "plant": "https://upload.wikimedia.org/wikipedia/commons/f/f5/Plant_cell_structure-en.svg",
        "virus": "https://upload.wikimedia.org/wikipedia/commons/7/77/Virus_Structure.svg",
        "bacteria": "https://upload.wikimedia.org/wikipedia/commons/3/32/Bacterial_cell_structure.svg"
    }

    for key, url in placeholder_map.items():
        if key in prompt.lower():
            return url

    # 🧩 Final fallback: a small locally generated placeholder
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.text(0.5, 0.5, f"Diagram Placeholder:\n{prompt}",
            ha='center', va='center', fontsize=10)
    ax.axis('off')
    plt.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf
