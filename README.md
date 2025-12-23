⚡ BiteBot.ai
Instant Indian Recipes for the Fast-Paced World.

🔗 Live App: https://bitebotai.streamlit.app/

📖 The Story
BiteBot.ai was born out of a real-world "emergency." While visiting my hometown, my mother left town for a day, leaving me in charge of the kitchen. Faced with a random mix of ingredients and zero desire for a 60-minute cooking session, I decided to build a solution.

Instead of cooking lunch, I "cooked" BiteBot.ai—an AI assistant that turns fridge photos into 10-minute Indian meals.

✨ Key Features
📸 Visual Pantry: Snap a photo of your fridge, and the AI "sees" what you have using Gemini Vision.

⏱️ Speed-First: Every recipe is optimized for 5, 10, or 15-minute prep times.

🥘 Desi Hacks: Expertly handles Indian spices and suggests shortcuts (like microwave par-boiling).

🥗 Dietary Logic: Supports Non-Veg, Veg, Jain, and Vegan preferences.

📱 Kitchen-Ready: A clean, light-mode UI designed for quick reading on mobile while you cook.

🛠️ The Tech Stack
🧠 AI Engine: Google Gemini 3 Flash (Low-latency multimodal model).

🏗️ Framework: Streamlit (For the web interface).

🐍 Language: Python 3.10+.

☁️ Hosting: Streamlit Community Cloud.

🧠 AI Product Insights
Latency over Logic: I chose the Flash model because for a hungry user, a 2-second response is better than a 20-second "perfect" response.

Prompt Guardrails: Engineered system instructions to ensure the AI never suggests long-drawn processes like "slow-cooking" or "overnight marination."

Frictionless UX: By using Computer Vision, I removed the need for users to type out long lists of ingredients.

💻 How to Run Locally
Clone the Repo: git clone https://github.com/your-username/bitebot-ai.git

Install Libraries: pip install streamlit google-generativeai Pillow

Add API Key: Create a .streamlit/secrets.toml file and add: GEMINI_API_KEY = "your_key_here"

Launch: streamlit run bitebot.py

Made with ❤️ for Food x AI — Abhinav
