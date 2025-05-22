# ---------------------------------------------------------------------------- #
#                                 I M P O R T S                                #
# ---------------------------------------------------------------------------- #
import streamlit as st
from pydantic import Field, BaseModel
from typing import Dict
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# ------------------------- Initializing Chat Models ------------------------- #
qwq = ChatGroq(
    model="qwen-qwq-32b",
    temperature=0.6,
    api_key=st.session_state.groq_api_key,
    model_kwargs={
        "reasoning_format" : "hidden"
    }
)
model = qwq

# ----------------------- Preparing structured outputs ----------------------- #
class quiz_output(BaseModel):
    """Response to the prompt in the following format only"""

    class QuestionItem(BaseModel):
        question: str = Field(description="Question to be asked")
        options: Dict[str, bool] = Field(
            description="A dictionary with string options each pointing to a bool, True if the option is correct and false otherwise"
        )

    thinking_content: str = Field(description="All the reasoning/thinking content here")
    response_content: list[QuestionItem] = Field(
        description="A list containing questions items"
    )


# ---------------- Modified models that give structured output --------------- #
model_quiz = model.with_structured_output(quiz_output)


# ---------------------------------------------------------------------------- #
QUIZ_PROMPT_TEMPLATE = r"""
You are a college professor tasked with creating a multiple choice question (MCQs) quiz on these topics:
{topic}
Generate at least 10 MCQs.
The output should be json formatted  like this:


[[
  {{
    "question": "If a train travels 120 miles in 2 hours, what is its average speed?",

    "options": {{
      "60 mph": true, #true if the option is correct false otherwise
      "40 mph": false,
      "100 mph": false,
      "240 mph": false
    }}
  }},
  
  and so on..
  
]]
"""
quiz_prompt = PromptTemplate.from_template(QUIZ_PROMPT_TEMPLATE)


def process(x: list) -> list:
    return list(map(dict, x))


to_quiz_questions = lambda x: process(x.response_content)  # noqa: E731

# ---------------------------------- Chains ---------------------------------- #
quiz_chain = quiz_prompt | model_quiz | to_quiz_questions

# ---------------------------------------------------------------------------- #

# ----------------------------------- QUIZ ----------------------------------- #
def quiz():
    import plotly.express as px
    questions = st.session_state.quiz_questions
    st.session_state.total_questions = len(questions)
    total_questions = st.session_state.total_questions
    st.progress(len(st.session_state.attempted_questions) / total_questions)
    st.write(
        f"Questions attempted: {len(st.session_state.attempted_questions)}/{total_questions}"
    )
        
    # Main quiz interface
    if not st.session_state.quiz_completed:
        if st.session_state.current_question_idx < total_questions:
            current_question = questions[st.session_state.current_question_idx]

            # Display question
            st.markdown(f"### {current_question['question']}") # type: ignore

            # Create two columns for options
            col1, col2 = st.columns(2)

            # Get the options
            options = current_question["options"]
            option_items = list(options.keys())
            st.divider()
            # Display options in columns
            with col1:
                c1 = st.container(border=True)
                c2 = st.container(border=True)
                c1.markdown("A: " + option_items[0])
                c2.markdown("B: " + option_items[1])
            with col2:
                c1 = st.container(border=True)
                c2 = st.container(border=True)
                c1.markdown("C: " + option_items[2])
                c2.markdown("D: " + option_items[3])

            choice = st.radio("Select an option", ["A", "B", "C", "D"])

            if st.button("Next Question"):
                if choice:
                    answer = (
                        option_items[0]
                        if choice == "A"
                        else option_items[1]
                        if choice == "B"
                        else option_items[2]
                        if choice == "C"
                        else option_items[3]
                        if choice == "D"
                        else None
                    )
                    if options[answer]:
                        st.session_state.score += 1
                        st.session_state.attempted_questions.add(
                            st.session_state.current_question_idx
                        )
                    else:
                        st.session_state.attempted_questions.add(
                            st.session_state.current_question_idx
                        )
                    st.session_state.current_question_idx += 1
                st.rerun()

        # Check if quiz is complete
        if st.session_state.current_question_idx >= total_questions:
            st.session_state.quiz_completed = True
            st.rerun()

    # End screen
    if st.session_state.quiz_completed:
        st.header("Quiz Complete! 🎉", divider=True)

        fig = px.pie(
            names=["Correct", "Incorrect"],
            values=[
                st.session_state.score,
                total_questions - st.session_state.score,
            ],
            hole=0.6,
            color_discrete_sequence=["#43E6B5", "#BB054E"],
            title=f"You scored {st.session_state.score} out of {total_questions} questions right!",
        )
        st.plotly_chart(fig)

# ---------------------------------------------------------------------------- #
if st.session_state.quiz_questions is None:
    ph = st.empty()
    if ph.button("Generate Quiz"):
        ph.empty()
        st.session_state.quiz_questions = quiz_chain.invoke(
                {"topic": st.session_state.user_input}
        )
        st.success("Quiz generated!")
        quiz()
    st.markdown("""
Click generate quiz to generate a quiz""")
else:
    quiz()
    

    
