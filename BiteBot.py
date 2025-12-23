import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
# Using st.secrets for safety on Streamlit Cloud
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API Key not found! Please add GEMINI_API_KEY to your Streamlit Secrets.")

# We use gemini-1.5-flash for maximum speed (ideal for BiteBot.ai)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. UI SETUP ---
st.set_page_config(page_title="BiteBot.ai | Fast Food, Faster", page_icon="⚡", layout="centered")

# Custom CSS for the 'Fast World' tech theme
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    h1 { color: #FFD700; font-family: 'Helvetica', sans-serif; text-align: center; }
    .stButton>button { 
        background-color: #FFD700; color: black; font-weight: bold; 
        border-radius: 10px; height: 3em; width: 100%; border: none;
    }
    .recipe-card { 
        padding: 20px; border-radius: 15px; background-color: #1e2130; 
        border-left: 8px solid #FFD700; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ BiteBot.ai")
st.markdown("<p style='text-align: center;'>No time to cook? BiteBot has you covered.</p>", unsafe_allow_html=True)

# --- 3. INPUTS ---
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📸 Scan Pantry/Fridge", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption="Analyzing these...", use_container_width=True)

with col2:
    text_input = st.text_input("✍️ Or type ingredients", placeholder="e.g. Bread, Egg, Maggi")
    diet = st.selectbox("Diet", ["Standard", "Vegetarian", "Vegan", "Jain"])
    speed = st.select_slider("Speed Mode", options=["5 min", "10 min", "15 min"])

# --- 4. GENERATION LOGIC ---
if st.button("GET MY BITE 🍴"):
    if not uploaded_file and not text_input:
        st.warning("Please upload a photo or type ingredients first!")
    else:
        with st.spinner("⚡ Crunching data..."):
            # System instructions focused on "BiteBot" speed theme
            system_prompt = f"""
            Act as BiteBot.ai, an AI chef for busy people. Create a {diet} Indian recipe 
            ready in exactly {speed}. 
            
            Guidelines:
            - Focus on SPEED and EASE.
            - Use common Indian pantry items (poha, bread, besan, frozen peas, etc).
            - Keep instructions to maximum 4 bullet points.
            - Format: 
              ## [Name of Dish]
              **Time:** {speed}
              **Ingredients:** (Include common Indian names in brackets)
              **Steps:** (Short and snappy)
              **Bite-Hack:** (A one-sentence shortcut)
            """
            
            # Prepare content for Gemini
            prompt_content = [system_prompt]
            if uploaded_file:
                prompt_content.append(Image.open(uploaded_file))
            if text_input:
                prompt_content.append(f"Ingredients: {text_input}")

            try:
                response = model.generate_content(prompt_content)
                recipe_text = response.text
                
                # Store in session state for downloading
                st.session_state['last_recipe'] = recipe_text
                
                # Display Recipe
                st.markdown(f'<div class="recipe-card">{recipe_text}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 5. DOWNLOAD FEATURE ---
if 'last_recipe' in st.session_state:
    st.download_button(
        label="📥 Download Recipe to Phone",
        data=st.session_state['last_recipe'],
        file_name="bitebot_recipe.txt",
        mime="text/plain",
    )

st.sidebar.markdown("---")
st.sidebar.write("Developed by **BiteBot.ai**")
