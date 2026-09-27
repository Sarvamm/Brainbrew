from typing import Dict
import plotly.express as px
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

st.header("❓ Interactive Quiz", divider=True)

if not st.session_state.groq_api_key:
    st.error("Missing Groq API Key.")
    st.stop()


# ----------------------- Structured Output Schema ----------------------- #
class QuestionItem(BaseModel):
    question: str = Field(description="The question text.")
    options: Dict[str, bool] = Field(
        description="A dict mapping 4 option strings to boolean (True for the correct answer, False otherwise)."
    )


class QuizOutput(BaseModel):
    """Structured output schema for generated quiz questions."""

    thinking_content: str = Field(
        description="Reasoning process for question formation."
    )
    questions: list[QuestionItem] = Field(
        description="List of multiple choice question items."
    )


# ------------------------- Initializing Model ------------------------- #
model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.5,
    api_key=st.session_state.groq_api_key,
)

model_quiz = model.with_structured_output(QuizOutput)

quiz_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a college professor. Create a 5-question multiple choice quiz on the requested topics. "
            "Each question MUST have exactly 4 options with exactly 1 correct answer.",
        ),
        ("human", "Create a multiple-choice quiz on these topics:\n{topic}"),
    ]
)

quiz_chain = (
    quiz_prompt | model_quiz | (lambda res: [q.model_dump() for q in res.questions])
)


# ------------------------------- Quiz Logic ------------------------------- #
def render_quiz():
    questions = st.session_state.quiz_questions
    st.session_state.total_questions = len(questions)
    total_questions = st.session_state.total_questions

    progress_val = min(len(st.session_state.attempted_questions) / total_questions, 1.0)
    st.progress(progress_val)
    st.caption(
        f"Progress: {len(st.session_state.attempted_questions)}/{total_questions} questions attempted"
    )

    if not st.session_state.quiz_completed:
        if st.session_state.current_question_idx < total_questions:
            current = questions[st.session_state.current_question_idx]

            st.subheader(f"Question {st.session_state.current_question_idx + 1}")
            st.markdown(f"**{current['question']}**")

            options_dict = current["options"]
            option_keys = list(options_dict.keys())

            if len(option_keys) < 4:
                st.error("Invalid question format received. Skipping...")
                st.session_state.current_question_idx += 1
                st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**A:** {option_keys[0]}")
                st.info(f"**B:** {option_keys[1]}")
            with col2:
                st.info(f"**C:** {option_keys[2]}")
                st.info(f"**D:** {option_keys[3]}")

            choice = st.radio(
                "Select your answer:",
                ["A", "B", "C", "D"],
                key=f"q_{st.session_state.current_question_idx}",
            )

            if st.button("Submit Answer"):
                idx_map = {"A": 0, "B": 1, "C": 2, "D": 3}
                selected_text = option_keys[idx_map[choice]]

                if options_dict.get(selected_text, False):
                    st.session_state.score += 1
                    st.toast("Correct!", icon="✅")
                else:
                    st.toast("Incorrect!", icon="❌")

                st.session_state.attempted_questions.add(
                    st.session_state.current_question_idx
                )
                st.session_state.current_question_idx += 1

                if st.session_state.current_question_idx >= total_questions:
                    st.session_state.quiz_completed = True

                st.rerun()

    if st.session_state.quiz_completed:
        st.header("Quiz Completed! 🎉", divider=True)
        score = st.session_state.score
        incorrect = total_questions - score

        fig = px.pie(
            names=["Correct", "Incorrect"],
            values=[score, incorrect],
            hole=0.6,
            color_discrete_sequence=["#2ecc71", "#e74c3c"],
            title=f"Final Score: {score} / {total_questions}",
        )
        st.plotly_chart(fig, use_container_width=True)

        if st.button("Retake Quiz"):
            st.session_state.quiz_completed = False
            st.session_state.current_question_idx = 0
            st.session_state.score = 0
            st.session_state.attempted_questions = set()
            st.rerun()


# -------------------------------- UI Flow -------------------------------- #
if st.session_state.user_input:
    if st.session_state.quiz_questions is None:
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz questions..."):
                st.session_state.quiz_questions = quiz_chain.invoke(
                    {"topic": st.session_state.user_input}
                )
            st.rerun()
        else:
            st.write("Click above to generate a new quiz based on your study topics.")
    else:
        render_quiz()
else:
    st.info("Please enter your study topics on the 'Get started' page first.")
