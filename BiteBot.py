import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- 1. CONFIGURATION ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Missing GEMINI_API_KEY! Add it to Streamlit Cloud Secrets.")
    st.stop()

# Select Model (Using Flash for speed and good JSON handling)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. UI STYLING ---
st.set_page_config(page_title="BiteBot.ai", page_icon="🍔")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; color: #000000; }}
    .main-title {{ color: #FFCC00; font-size: 3rem; font-weight: 800; text-align: center; }}
    .recipe-card {{ 
        padding: 20px; 
        margin-bottom: 15px;
        border-radius: 12px; 
        background-color: #f9f9f9; 
        border-left: 6px solid #FFCC00; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .recipe-title {{ font-size: 1.5rem; font-weight: bold; color: #333; }}
    .cart-box {{ border: 2px dashed #FFCC00; padding: 15px; border-radius: 10px; margin-top: 20px; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🍔 BiteBot.ai</h1>", unsafe_allow_html=True)

# --- 3. INPUTS ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸 Photo Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), use_container_width=True)

with col2:
    text_items = st.text_input("🌶️ Type Ingredients")
    diet = st.selectbox("Diet", ["Non-veg", "Veg", "Jain", "Vegan"])
    prep_time = st.select_slider("Max Time", options=["5 min", "10 min", "15 min"])

# --- 4. RECIPE LOGIC ---
if st.button("GENERATE MY BITE"):
    if not (uploaded_file or text_items):
        st.warning("Upload a photo or type ingredients!")
    else:
        with st.spinner("⚡ analyzing pantry & checking prices..."):
            
            # --- AGENTIC PROMPT FOR JSON OUTPUT ---
            # We explicitly ask for JSON so we can separate missing ingredients programmatically
            prompt = f"""
            Act as an API. Analyze the inputs and return a JSON list of exactly 3 recipes.
            
            1. **Recipe 1 (Strict):** MUST use ONLY the provided/detected ingredients + basic pantry staples (Salt, Oil, Water, basic Spices). 'missing_ingredients' list must be empty [].
            2. **Recipe 2 (Creative):** Can use 1-2 extra ingredients. List them in 'missing_ingredients'.
            3. **Recipe 3 (Creative):** Can use different extra ingredients. List them in 'missing_ingredients'.
            
            Input Context: Diet: {diet}, Time: {prep_time}, Text: {text_items}.
            
            **Strict Output Format (JSON Array only):**
            [
              {{
                "name": "Recipe Name",
                "time": "10 min",
                "steps": "Step 1... Step 2...",
                "missing_ingredients": ["Item A", "Item B"] (or empty list for Recipe 1)
              }}
            ]
            """
            
            inputs = [prompt]
            if text_items: inputs.append(f"Ingredients text: {text_items}")
            if uploaded_file: inputs.append(Image.open(uploaded_file))

            try:
                # Force JSON response mode
                response = model.generate_content(inputs, generation_config={"response_mime_type": "application/json"})
                recipes_data = json.loads(response.text)
                
                # --- PROCESS & DISPLAY RECIPES ---
                cart_items = [] # To collect missing items
                
                for idx, recipe in enumerate(recipes_data):
                    name = recipe['name']
                    missing = recipe.get('missing_ingredients', [])
                    
                    # Logic: Add asterisk if missing ingredients exist
                    display_name = name
                    if missing:
                        display_name += " *"
                        cart_items.extend(missing) # Add to master cart list

                    # Render Card
                    st.markdown(f"""
                    <div class='recipe-card'>
                        <div class='recipe-title'>{display_name}</div>
                        <p>⏱️ {recipe['time']}</p>
                        <p>🛠️ {recipe['steps']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # --- FOOTNOTE ---
                st.caption("* Additional items required, added to your cart")

                # --- SMART SHOPPING CART ---
                if cart_items:
                    # Deduplicate items
                    unique_cart = list(set(cart_items))
                    
                    st.divider()
                    # The "Show Cart" dropdown
                    with st.expander(f"🛒 Show Cart ({len(unique_cart)} items added)"):
                        st.markdown("<div class='cart-box'>", unsafe_allow_html=True)
                        for item in unique_cart:
                            st.checkbox(item, value=True, key=item)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.button("Checkout / Save List")

            except Exception as e:
                st.error(f"Oof! The AI got confused. Try again. Error: {e}")

st.divider()
st.center = st.write("Made with ❤️ for Food x AI - Abhinav")
