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
AVAILABLE_MODELS = ['gemini-2.0-flash-exp', 'gemini-1.5-flash'] # Updated for latest models
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

# --- 3. SESSION STATE INITIALIZATION ---
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
    
    /* Custom Strikethrough for collected items */
    .stCheckbox p {{ font-size: 1rem; }}
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
                
                # Save to Session State
                st.session_state.recipes = data
                
                # Update cart in session state (deduplicated)
                new_items = []
                for r in data:
                    new_items.extend(r.get('missing_ingredients', []))
                
                # Only add items that aren't already tracked
                current_items = [item['name'] for item in st.session_state.cart]
                for item in list(set(new_items)):
                    if item not in current_items:
                        st.session_state.cart.append({"name": item, "checked": False})
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 7. DISPLAY RECIPES (COLLAPSIBLE) ---
if st.session_state.recipes:
    st.divider()
    st.subheader("🍳 Choose your Meal")
    
    for recipe in st.session_state.recipes:
        name = recipe['name']
        missing = recipe.get('missing_ingredients', [])
        
        display_name = f"{name} *" if missing else name
        
        with st.expander(display_name):
            st.markdown(f"**⏱️ Time:** {recipe['time']}")
            st.markdown(f"**🛠️ Steps:** {recipe['steps']}")
            if missing:
                st.info(f"🛒 Needs: {', '.join(missing)}")
    
    st.caption("* Requires additional ingredients")

# --- 8. SMART SHOPPING CART (FIXED & BORDERED) ---
if st.session_state.cart:
    st.divider()
    st.markdown("### 🛒 Smart Shopping Cart")
    
    # USE NATIVE CONTAINER (Fixes the visual bug)
    with st.container(border=True):
        
        # 1. Helper function to toggle state
        def toggle_item(index):
            st.session_state.cart[index]['checked'] = not st.session_state.cart[index]['checked']

        # 2. Sort items: Unchecked first, then Checked
        # We use indices to map back to the original list
        sorted_indices = sorted(
            range(len(st.session_state.cart)), 
            key=lambda i: st.session_state.cart[i]['checked']
        )

        # 3. Render Items
        has_items_to_buy = False
        
        st.caption("To Buy")
        for i in sorted_indices:
            item = st.session_state.cart[i]
            
            # If we hit the first checked item, render a separator
            if item['checked'] and not has_checked_section:
                st.divider()
                st.caption("✅ Collected")
                has_checked_section = True
            
            # Render Checkbox
            # Note: We use the index 'i' in the key to ensure uniqueness
            label = f"~~{item['name']}~~" if item['checked'] else item['name']
            st.checkbox(
                label, 
                value=item['checked'], 
                key=f"item_{i}", 
                on_change=toggle_item,
                args=(i,)
            )
            
            if not item['checked']:
                has_items_to_buy = True

        if not has_items_to_buy and len(st.session_state.cart) > 0:
            st.success("🎉 All items collected!")

st.divider()
st.center = st.write("Made with ❤️ for Food x AI - Abhinav")
