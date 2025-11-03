# backend.py



import requests
import base64
import streamlit as st
from openai import OpenAI
from PIL import Image
import io

# Initialize clients
client = None
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    pass

OLLAMA_URL = st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")


def get_biovyn_response(prompt, study_mode=False):
    """Hybrid AI: Try Ollama locally, then fall back to OpenAI."""
    try:
        response = requests.post(OLLAMA_URL, json={"model": "llama3:3b", "prompt": prompt}, timeout=10)
        if response.status_code == 200 and "response" in response.json():
            return response.json()["response"].strip()
    except Exception:
        pass

    if client:
        try:
            if study_mode:
                prompt = f"Explain this in a clear, educational way: {prompt}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are BiovynAI, a biology expert who explains clearly and kindly."},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Local fallback if everything fails
    return f"(Offline Mode) Here's a short summary about {prompt}. Diagram placeholders will still work!"


def generate_bio_diagram(prompt):
    """Always show a valid diagram (never error)."""
    with st.spinner("Generating diagram... 🧬"):

        # 🧩 Try Ollama local generation first (optional)
        try:
            ollama_response = requests.post(
                OLLAMA_URL,
                json={"model": "llava:latest", "prompt": f"Generate a simple labeled biology diagram of {prompt}"},
                timeout=15,
            )
            if ollama_response.status_code == 200 and "image" in ollama_response.json():
                img_data = base64.b64decode(ollama_response.json()["image"])
                st.image(img_data, caption=f"Diagram: {prompt}", use_column_width=True)
                return
        except Exception:
            pass

        # 🧠 Try OpenAI image generation (if available)
        if client:
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
                    st.image(image_bytes, caption=f"Diagram: {prompt}", use_column_width=True)
                    return
            except Exception:
                pass

        # 🧬 100% working placeholder fallback
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

        placeholder_url = None
        for key, url in placeholder_map.items():
            if key in prompt.lower():
                placeholder_url = url
                break

        if not placeholder_url:
            placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/3/3f/Animal_cell_structure_en.svg"

        st.image(placeholder_url, caption=f"Example Diagram: {prompt}", use_column_width=True)
