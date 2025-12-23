import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIGURATION ---
genai.configure(api_key="AIzaSyBFReqedPRF_LQaFeTwT5AlPwLN8drWnLQ")
model = genai.GenerativeModel('gemini-1.5-pro')

st.set_page_config(page_title="BiteBot.ai | Fast Food, Faster", page_icon="⚡")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #FF4B4B; font-family: 'Ubuntu', sans-serif; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 20px; width: 100%; }
    .recipe-card { padding: 20px; border-radius: 15px; background-color: #1e2130; border-left: 5px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("⚡ BiteBot.ai")
st.subheader("Instant Indian Recipes for the Fast-Paced World.")

# --- INPUT SECTION ---
col1, col2 = st.columns([1, 1])

with col1:
    st.write("### 📸 Scan your fridge")
    uploaded_file = st.file_uploader("Upload or Snap", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

with col2:
    st.write("### ✍️ Or type it out")
    text_ingredients = st.text_input("What ingredients are ready?", placeholder="Bread, eggs, onion...")
    
    speed_mode = st.select_slider(
        "Max Cooking Time",
        options=["5 min (Flash)", "10 min (Quick)", "15 min (Standard)"],
        value="10 min (Quick)"
    )

# --- LOGIC ---
if st.button("GET MY BITE 🍴"):
    with st.spinner("BiteBot is crunching the data..."):
        
        # Construct the specialized prompt
        system_prompt = f"""
        You are BiteBot.ai, an AI specialized in 15-minute Indian 'Quick-Bites'.
        User wants a {speed_mode} recipe.
        
        Rules:
        1. Use common Indian ingredients/shortcuts (Poha, Maggi, Bread, Paneer).
        2. Steps must be 'Lazy-friendly' (Microwave, One-pan, No grinding).
        3. Output must include:
           - ⚡ Dish Name
           - ⏱️ BiteTime (Total minutes)
           - 🛒 What you need
           - 🛠️ BiteSteps (Maximum 4 short steps)
           - 💡 Pro Hack (A shortcut to save 2 minutes)
        """
        
        content_to_send = [system_prompt]
        
        if uploaded_file:
            content_to_send.append(Image.open(uploaded_file))
        
        if text_ingredients:
            content_to_send.append(f"Ingredients provided: {text_ingredients}")

        if not uploaded_file and not text_ingredients:
            st.error("Give me something to work with! (Image or Text)")
        else:
            response = model.generate_content(content_to_send)
            
            st.markdown("---")
            st.markdown(f'<div class="recipe-card">{response.text}</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.sidebar.info("BiteBot.ai: Stop Thinking. Start Eating.")