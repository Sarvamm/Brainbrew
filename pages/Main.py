import time
import streamlit as st


def streamer(text: str, speed: float = 0.01):
    for char in text:
        time.sleep(speed)
        yield char


subheader = """
Tired of endless note-taking? **Brainbrew** leverages modern AI to transform your study lists into a dynamic learning experience.

**Here's how it works:**

1. **Enter Your Topics:** Type or paste your list of subjects or concepts below.
2. **AI Generation:** Brainbrew processes your input to generate:
   * **Detailed Notes:** Comprehensive summaries with math formula support.
   * **Q&A Pairs:** Smart questions and step-by-step explanations.
   * **Custom Quizzes:** Interactive multiple-choice tests with scoring analytics.
"""

st.title("🧠 BrainBrew ")

if st.session_state.first_time:
    st.write_stream(streamer(subheader, speed=0.001))
    st.session_state.first_time = False
else:
    st.markdown(subheader)

st.divider()

with st.form("topics_form"):
    user_topics = st.text_area(
        "Enter comma-separated topics here:",
        value=st.session_state.user_input,
        placeholder="e.g., Quantum Mechanics, Matrix Multiplication, Special Relativity",
        height=120,
    )
    submitted = st.form_submit_button("Submit Topics")
    if submitted:
        st.session_state.user_input = user_topics.strip()
        # Reset cached content when topics change
        st.session_state.notes = None
        st.session_state.messages = []
        st.session_state.quiz_questions = None
        st.session_state.quiz_completed = False
        st.session_state.current_question_idx = 0
        st.session_state.score = 0
        st.session_state.attempted_questions = set()

if st.session_state.user_input and st.session_state.groq_api_key:
    st.success("Topics saved!")
    st.write_stream(
        streamer(
            "Head over to the sidebar tabs (Notes, Q&A, or Quiz) to start generating!",
            speed=0.01,
        )
    )
elif not st.session_state.groq_api_key:
    st.warning(
        "Please configure your Groq API key in `.streamlit/secrets.toml` under `API`."
    )
