import streamlit as st
import time

def streamer(text: str, speed: float = 0.01):
    for char in text:
        time.sleep(speed)
        yield char

subheader = """
Tired of endless note-taking? Lit-Notes leverages the power of AI, built within a Streamlit application, to transform your study lists into a dynamic learning experience.
We've harnessed the capabilities of Large Language Models (LLMs) within a Python environment.

**Here's how it works:**

1.  **Enter Your Topics:** Simply type or paste your list of subjects or concepts.

2.  **Python-Powered Generation:** Lit-Notes uses Python to interface with the LLMs, processing your input and generating:

    *   **Detailed Notes:** Comprehensive summaries created by the LLM.
    *   **Q&A Pairs:** Intelligent questions and answers generated for knowledge testing.
    *   **Custom Quizzes:** Generate quizzes to reinforce your learning - all driven by Python logic.

Get your Groq API key [here](https://console.groq.com/home)

"""

if st.session_state.first_time:
    st.write_stream(streamer(subheader, speed=0.001))
    st.session_state.first_time = False
else:
    st.write(subheader)
    
with st.form("form"):
        st.session_state.groq_api_key = st.text_input("Enter Groq API key here")
        st.session_state.user_input = st.text_area("Start by entering comma separated list of topics here")
        st.form_submit_button("Submit")
        
if st.session_state.user_input and st.session_state.groq_api_key:
    st.write_stream(streamer("Great! now head over to the sidebar and start generating!", speed=0.01))