import streamlit as st
import google.generativeai as genai
from PIL import Image

# ── Access Control ──────────────────────────────────────────────────────────────
def is_authenticated():
    return st.session_state.get("bio_auth", False)

def show_access_gate():
    st.set_page_config(page_title="Kodari Biology", layout="centered")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🧬 Kodari Biology")
        st.markdown("*A-Level Biology Revision*")
        st.markdown("---")
        st.markdown("#### Enter your access code")
        code = st.text_input(
            label="Access Code",
            placeholder="e.g. BIO-A001",
            label_visibility="collapsed",
        )
        if st.button("Access →", type="primary", use_container_width=True):
            if not code:
                st.error("Please enter your access code.")
            else:
                try:
                    valid_codes = [c.strip().upper() for c in st.secrets["BIO_ACCESS_CODES"]]
                    if code.strip().upper() in valid_codes:
                        st.session_state["bio_auth"] = True
                        st.rerun()
                    else:
                        st.error("Invalid access code. Please check your code and try again.")
                except Exception:
                    st.error("Access code system error. Please contact your teacher.")
        try:
            purchase_url = st.secrets.get("BIO_STRIPE_URL", "")
        except Exception:
            purchase_url = ""
        if purchase_url:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align:center'>"
                f"<a href='{purchase_url}' target='_blank'>🛒 Get Biology Access</a>"
                f"</div>",
                unsafe_allow_html=True
            )

# ── Gate Check ──────────────────────────────────────────────────────────────────
if not is_authenticated():
    show_access_gate()
    st.stop()

# ── 원본 코드 (한 줄도 수정 없음) ────────────────────────────────────────────────

# 1. API Configuration
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key missing! Check your .streamlit/secrets.toml file.")

# 2. Smart Model Selection Logic
@st.cache_resource
def load_biology_model():
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
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
                response = model.generate_content([
                    "Provide the A-level model answer for this question. Reference the mark schemes in my drive.", 
                    image
                ])
                st.success("Analysis Complete!")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Technical Error: {e}")

# ── Logout ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    if st.button("Log out", use_container_width=True):
        st.session_state["bio_auth"] = False
        st.rerun()
