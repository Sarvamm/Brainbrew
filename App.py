# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
import streamlit as st
import requests
import subprocess
import time
from streamlit_extras.buy_me_a_coffee import button

# ---------------------------------------------------------------------------- #
version: str = "0.0.1"
logo: str = "assets/logo.png"
coffee_username: str = "astrayn"

# ---------------------------------------------------------------------------- #
def is_ollama_running() -> bool:
    """_summary_
    Check if ollama is running or not
    Returns:
        bool: True if it is, False in any other case.
    """
    try:
        response = requests.get("http://localhost:11434", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# ---------------------------------------------------------------------------- #
def start_ollama() -> None | str:
    """_summary_
    Try to start ollama.
    Returns:
        None | str: _description_
    """
    try:
        subprocess.Popen(
            ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        time.sleep(3)
        st.session_state.status = "Online"
        return None
    except Exception as e:
        return "Failed to start Ollama:" + str(e)
    
    
if "status" not in st.session_state:
    st.session_state["status"] = "Offline"

if not is_ollama_running():
    start_ollama()
    if st.session_state["status"] == "Online":
        st.sidebar.success("ollama is running")

if "user_input" not in st.session_state:
    st.session_state.user_input = None

if 'quiz_questions' not in st.session_state:
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
    st.session_state.groq_api_key = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "notes" not in st.session_state:
    st.session_state.notes = None
if "first_time" not in st.session_state:
    st.session_state.first_time = True

#Page setup
HomePage = st.Page(
    page="pages/Main.py",
    icon="🔥",
    title = "Get started",
    default = True,
    
)
AboutPage = st.Page(
    page="pages/About.py",
    icon="👤",    
    title = "About"
)

QuizPage = st.Page(
    page="pages/Quiz.py",
    icon="❓",
    title="Quiz"
)

NotesPage = st.Page(
    page="pages/Notes.py",
    icon="📝",
    title="Notes"
)
QnaPage = st.Page(
    page="pages/QnA.py",
    icon="🤔",
    title="Question/Answers"
)

# Navigation Bar
pg = st.navigation([HomePage, NotesPage, QnaPage, QuizPage, AboutPage ])

st.logo(logo, size='large')
st.set_page_config(
    page_title="BrainBrew",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    )

with st.sidebar:
    st.markdown(10*"<br>", unsafe_allow_html=True)
    st.caption("Support me by clicking on this button 👇")
    button(username=coffee_username, floating=False, width=221)
    st.caption(version)
pg.run()