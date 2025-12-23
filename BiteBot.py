import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
# Robust setup to handle key and model availability
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
    st.stop()

# Auto-selection logic: Uses Gemini 3 Flash for maximum speed
# Using the 'models/' prefix ensures the 404 error is bypassed
MODEL_NAME = 'models/gemini-3-flash' 
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. UI STYLING (The BiteBot.ai Identity) ---
st.set_page_config(page_title="BiteBot.ai", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0f1116; color: #e0e0e0; }
    .main-title { color: #FFCC00; font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0px; }
    .sub-title { color: #888; text-align: center; margin-bottom: 30px; }
    .stButton>button { 
        background-color: #FFCC00; color: #000; border-radius: 8px; 
        font-weight: bold; width: 100%; border: none; padding: 10px;
    }
    .recipe-card { 
        padding: 25px; border-radius: 12px; background-color: #1a1c24; 
        border-left: 6px solid #FFCC00; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚡ BiteBot.ai</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Indian recipes for a fast-moving world.</p>", unsafe_allow_html=True)

# --- 3. INPUT SECTION ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.write("### 📸 Photo Pantry")
    uploaded_file = st.file_uploader("Snap what you have...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        display_img = Image.open(uploaded_file)
        st.image(display_img, use_container_width=True, caption="BiteBot is looking...")

with col2:
    st.write("### ✍️ Quick Type")
    text_items = st.text_input("List ingredients", placeholder="Bread, dahi, chilli...")
    diet = st.selectbox("Diet", ["All", "Vegetarian", "Jain", "Vegan"])
    prep_time = st.select_slider("Max Time", options=["5 min", "10 min
