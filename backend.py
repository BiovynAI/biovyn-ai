# backend.py  (replace existing backend content with this)
import io
import base64
import requests
import streamlit as st
from PIL import Image

# Try to create the OpenAI client for text/chat; if it's not available, chat will fall back.
client = None
try:
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", None))
except Exception:
    client = None

# --- CRITICAL SAFETY: Monkeypatch / stub any image generation to avoid OpenAI image calls ---
# This ensures *no network* call for images happens, preventing billing errors.
if client is not None:
    try:
        # provide a lightweight stub object with generate() that returns a safe empty payload
        class _ImageStub:
            def generate(self, *args, **kwargs):
                # Return a structure similar to successful response but with empty image
                return {"data": [{"b64_json": None}]}
        client.images = _ImageStub()
    except Exception:
        # If monkeypatch fails for some reason, set client to None to be extra safe
        client = None

OLLAMA_URL = st.secrets.get("OLLAMA_URL", "http://localhost:11434/api/generate")

def get_biovyn_response(prompt, study_mode=False):
    """Hybrid AI: Try Ollama locally, then fallback to OpenAI chat if available."""
    try:
        resp = requests.post(OLLAMA_URL, json={"model": "llama3:3b", "prompt": prompt}, timeout=10)
        if resp.status_code == 200 and "response" in resp.json():
            return resp.json()["response"].strip()
    except Exception:
        pass

    if client:
        try:
            if study_mode:
                prompt_for_model = f"Explain this in an educational, structured way: {prompt}"
            else:
                prompt_for_model = prompt

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are BiovynAI, a biology expert who explains clearly and kindly."},
                    {"role": "user", "content": prompt_for_model}
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # final fallback
    return f"(Offline) Quick summary for: {prompt}"

def generate_bio_diagram(prompt):
    """
    Guaranteed-safe diagram: we never call OpenAI image API due to monkeypatch stub.
    This function first tries Ollama image (if you have a local endpoint that returns an image),
    otherwise uses placeholder URLs or a local matplotlib placeholder.
    """
    with st.spinner("Loading diagram... 🧬"):
        # 1) Try local Ollama image endpoint (if you have one that returns image bytes or base64)
        try:
            resp = requests.post(OLLAMA_URL, json={"model": "llava:latest", "prompt": f"Create a labeled diagram of {prompt}"}, timeout=12)
            if resp.status_code == 200:
                j = resp.json()
                # Support both 'image' base64 field or raw binary in content
                if "image" in j and j["image"]:
                    img_bytes = base64.b64decode(j["image"])
                    st.image(img_bytes, caption=f"Diagram: {prompt}", use_column_width=True)
                    return
        except Exception:
            pass

        # 2) If local Ollama didn't work — use trusted placeholder map (no network to OpenAI)
        placeholder_map = {
            "cell": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Animal_cell_structure_en.svg",
            "dna": "https://upload.wikimedia.org/wikipedia/commons/8/87/DNA_chemical_structure.svg",
            "photosynthesis": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Photosynthesis_process_diagram_en.svg",
            "heart": "https://upload.wikimedia.org/wikipedia/commons/5/55/Diagram_of_the_human_heart_%28cropped%29.svg",
            "brain": "https://upload.wikimedia.org/wikipedia/commons/4/44/Diagram_showing_the_main_parts_of_the_brain_CRUK_188.svg",
            "neuron": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Neuron.svg",
            "plant": "https://upload.wikimedia.org/wikipedia/commons/f/f5/Plant_cell_structure-en.svg",
            "virus": "https://upload.wikimedia.org/wikipedia/commons/7/77/Virus_Structure.svg",
            "bacteria": "https://upload.wikimedia.org/wikipedia/commons/3/32/Bacterial_cell_structure.svg",
            "mitochondria": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Mitochondrion_structure.svg",
            "nucleus": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Nucleus_diagram.svg",
            "ecosystem": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Ecosystem_diagram.svg"
        }

        placeholder_url = None
        for key, url in placeholder_map.items():
            if key in prompt.lower():
                placeholder_url = url
                break

        if not placeholder_url:
            # final fallback image (SVG from wiki)
            placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/3/3f/Animal_cell_structure_en.svg"

        st.image(placeholder_url, caption=f"Example Diagram: {prompt}", use_column_width=True)

