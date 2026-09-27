# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
import streamlit as st

VERSION: str = "0.0.2"
LOGO: str = "assets/logo.png"

# Page configuration MUST be the first Streamlit command executed
st.set_page_config(
    page_title="BrainBrew",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------- Session State Defaults -------------------------- #
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "attempted_questions" not in st.session_state:
    st.session_state.attempted_questions = set()
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 1
if "groq_api_key" not in st.session_state:
    # Safe retrieval with fallback if API key is not yet set in secrets
    st.session_state.groq_api_key = st.secrets.get("API", "")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "notes" not in st.session_state:
    st.session_state.notes = None
if "first_time" not in st.session_state:
    st.session_state.first_time = True

# -------------------------------- Navigation -------------------------------- #
HomePage = st.Page(page="pages/Main.py", icon="🔥", title="Get started", default=True)
NotesPage = st.Page(page="pages/Notes.py", icon="📝", title="Notes")
QuizPage = st.Page(page="pages/Quiz.py", icon="❓", title="Quiz")

pg = st.navigation([HomePage, NotesPage, QuizPage])

try:
    st.logo(LOGO, size="large")
except Exception:
    pass

with st.sidebar:
    st.markdown(22 * "<br>", unsafe_allow_html=True)
    st.caption(f"Version: {VERSION}")

pg.run()
