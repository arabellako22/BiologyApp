import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API Configuration
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key missing! Check your .streamlit/secrets.toml file.")

# 2. Smart Model Selection Logic
# This function automatically finds the correct model name for your account.
@st.cache_resource
def load_biology_model():
    # Find all models that support generating content
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Priority: Look for Gemini 3 Flash, then Gemini 1.5 Flash, then pick the first one.
    target_model = next((m for m in available_models if "gemini-3-flash" in m), 
                    next((m for m in available_models if "gemini-1.5-flash" in m), 
                    available_models[0]))
    
    return genai.GenerativeModel(
        model_name=target_model,
        system_instruction=(
            "You are an expert A-Level Biology Examiner. "
            "Use the provided Google Drive documents to provide definitive model answers. "
            "Focus on mark scheme accuracy, bold essential keywords, and use LaTeX for mathematical expressions, statistical symbols, and biological pathways."
        )
    )

# Initialize the smart model
model = load_biology_model()

# 3. User Interface
st.set_page_config(page_title="A-Level Biology Solver", layout="centered")
st.title("🧬 A-Level Biology Revision Tool")
st.write(f"Connected to Model: **{model.model_name}**")

uploaded_file = st.file_uploader("Upload a question photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Question Preview', use_container_width=True)
    
    if st.button('Generate Model Answer'):
        with st.spinner('Accessing database...'):
            try:
                # The model generates content based on the photo
                response = model.generate_content([
                    "Provide the A-level model answer for this question. Reference the mark schemes in my drive.", 
                    image
                ])
                st.success("Analysis Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Technical Error: {e}")