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

# --- 2. ROBUST MODEL SELECTION ---
AVAILABLE_MODELS = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-1.5-flash']
model = None
current_engine = ""

for model_name in AVAILABLE_MODELS:
    try:
        test_model = genai.GenerativeModel(model_name)
        test_model.count_tokens("test") 
        model = test_model
        current_engine = model_name
        break
    except Exception:
        continue

if not model:
    st.error(f"No compatible Gemini models found. Check your API quota.")
    st.stop()

# --- 3. SESSION STATE INITIALIZATION (Crucial for fixing app state) ---
if 'recipes' not in st.session_state:
    st.session_state.recipes = []
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 4. UI STYLING ---
st.set_page_config(page_title="BiteBot.ai", page_icon="🍔")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF; color: #000000; }}
    .main-title {{ color: #FFCC00; font-size: 3rem; font-weight: 800; text-align: center; }}
    
    /* Collapsible Card Styling */
    .streamlit-expanderHeader {{
        font-weight: bold;
        font-size: 1.2rem;
        color: #333;
        border-left: 5px solid #FFCC00;
        background-color: #f9f9f9;
        border-radius: 8px;
    }}
    
    /* Cart Styling */
    .cart-container {{
        border: 2px dashed #FFCC00;
        padding: 20px;
        border-radius: 12px;
        background-color: #fffdf0;
        margin-top: 20px;
    }}
    .collected-item {{
        text-decoration: line-through;
        color: #888;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🍔 BiteBot.ai</h1>", unsafe_allow_html=True)
st.caption(f"Engine: {current_engine}")

# --- 5. INPUTS ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸 Photo Scan", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file), use_container_width=True)

with col2:
    text_items = st.text_input("🌶️ Type Ingredients")
    diet = st.selectbox("Diet", ["Non-veg", "Veg", "Jain", "Vegan"])
    prep_time = st.select_slider("Max Time", options=["5 min", "10 min", "15 min"])

# --- 6. GENERATION LOGIC ---
if st.button("GENERATE MY BITE"):
    if not (uploaded_file or text_items):
        st.warning("Upload a photo or type ingredients!")
    else:
        with st.spinner("⚡ Chef is cooking..."):
            prompt = f"""
            Act as an API. Analyze the inputs and return a JSON list of exactly 3 recipes.
            
            1. **Recipe 1 (Strict):** MUST use ONLY the provided/detected ingredients + basic pantry staples. 'missing_ingredients' list must be empty [].
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
                response = model.generate_content(inputs, generation_config={"response_mime_type": "application/json"})
                data = json.loads(response.text)
                
                # Save to Session State (So they persist!)
                st.session_state.recipes = data
                
                # Extract all missing ingredients for the cart
                all_missing = []
                for r in data:
                    all_missing.extend(r.get('missing_ingredients', []))
                
                # Update cart in session state (deduplicated)
                st.session_state.cart = list(set(all_missing))
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 7. DISPLAY RECIPES (COLLAPSIBLE) ---
if st.session_state.recipes:
    st.divider()
    st.subheader("🍳 Choose your Meal")
    
    for recipe in st.session_state.recipes:
        name = recipe['name']
        missing = recipe.get('missing_ingredients', [])
        
        # Add visual cue if ingredients are missing
        display_name = f"{name} *" if missing else name
        
        # Use Expander to hide details by default
        with st.expander(display_name):
            st.markdown(f"**⏱️ Time:** {recipe['time']}")
            st.markdown(f"**🛠️ Steps:** {recipe['steps']}")
            if missing:
                st.info(f"🛒 Needs: {', '.join(missing)}")
    
    st.caption("* Requires additional ingredients (added to cart below)")

# --- 8. SMART SHOPPING CART (PERSISTENT) ---
if st.session_state.cart:
    st.divider()
    st.markdown("### 🛒 Smart Shopping Cart")
    
    # Render the Dotted Box Container
    st.markdown("<div class='cart-container'>", unsafe_allow_html=True)
    
    # Initialize check states in session_state if new items appeared
    for item in st.session_state.cart:
        key = f"check_{item}"
        if key not in st.session_state:
            st.session_state[key] = False

    # Filter items into two lists based on their checkbox state
    to_buy = [item for item in st.session_state.cart if not st.session_state[f"check_{item}"]]
    collected = [item for item in st.session_state.cart if st.session_state[f"check_{item}"]]

    # 1. To Buy List (Unchecked)
    if to_buy:
        st.markdown("**To Buy:**")
        for item in to_buy:
            # When clicked, this updates st.session_state[key] and re-runs the script
            st.checkbox(item, key=f"check_{item}")
    else:
        if not collected:
            st.info("Cart is empty!")
        else:
            st.success("🎉 All items collected!")

    # 2. Collected List (Checked/Visual Separation)
    if collected:
        st.markdown("---")
        st.markdown("**✅ Collected:**")
        for item in collected:
            # We show these as checked. Unchecking them moves them back to 'To Buy'
            st.checkbox(f"~~{item}~~", value=True, key=f"check_{item}")
            
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.center = st.write("Made with ❤️ for Food x AI - Abhinav")
