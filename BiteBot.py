import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION & ERROR HANDLING ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Missing GEMINI_API_KEY! Add it to Streamlit Cloud Secrets.")
    st.stop()

# Robust Model Selection
# We try Gemini 3 Flash Preview first. If not found, we fallback to 2.5 Flash.
AVAILABLE_MODELS = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-1.5-flash']
model = None

for model_name in AVAILABLE_MODELS:
    try:
        model = genai.GenerativeModel(model_name)
        # Quick test call to verify availability
        model.count_tokens("test") 
        current_engine = model_name
        break
    except Exception:
        continue

if not model:
    st.error("No compatible Gemini models found. Check your API quota/region.")
    st.stop()

# --- 2. UI STYLING ---
st.set_page_config(page_title="BiteBot.ai", page_icon="⚡")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; color: #000000; }}
    .main-title {{ color: #FFCC00; font-size: 3rem; font-weight: 800; text-align: center; }}
    .stButton>button {{ background-color: #FFCC00; color: #000; font-weight: bold; width: 100%; border-radius: 8px; }}
    .recipe-card {{ padding: 20px; border-radius: 12px; background-color: #1a1c24; border-left: 6px solid #FFCC00; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚡ BiteBot.ai</h1>", unsafe_allow_html=True)
st.caption(f"Engine: {current_engine}")

# --- 3. INPUTS ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸 Photo Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), use_container_width=True)

with col2:
    text_items = st.text_input("✍️ Type Ingredients")
    diet = st.selectbox("Diet", ["Standard", "Vegetarian", "Jain", "Vegan"])
    prep_time = st.select_slider("Max Time", options=["5 min", "10 min", "15 min"])

# --- 4. RECIPE GENERATION ---
if st.button("GENERATE MY BITE"):
    if not (uploaded_file or text_items):
        st.warning("Upload a photo or type ingredients!")
    else:
        with st.spinner("⚡ Crunching..."):
            prompt = f"Act as BiteBot.ai. Create a {diet} Indian recipe in {prep_time}. Use max 4 steps. Format: ## Dish Name, ⏱️ Time, 🛒 Ingredients, 🛠️ Steps, 💡 Speed-Hack."
            
            inputs = [prompt]
            if text_items: inputs.append(f"Ingredients: {text_items}")
            if uploaded_file: inputs.append(Image.open(uploaded_file))

            try:
                response = model.generate_content(inputs)
                recipe = response.text
                st.markdown(f"<div class='recipe-card'>{recipe}</div>", unsafe_allow_html=True)
                
                st.download_button("📥 Save Recipe", data=recipe, file_name="bitebot_recipe.txt")
            except Exception as e:
                st.error(f"Generation Error: {e}")

st.divider()
st.center = st.write("BiteBot.ai - Fast Food, Faster.")

