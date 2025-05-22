# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
import streamlit as st
import time
from langchain_groq import ChatGroq
from pydantic import Field, BaseModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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
class questions_output(BaseModel):
    """Response to the prompt in the following format only"""

    thinking_content: str = Field(description="All the reasoning/thinking content here")
    response_content: list[str] = Field(
        description="Generate questions in the format of list of strings"
    )


model_questions = model.with_structured_output(questions_output)


# ---------------------------------------------------------------------------- #
def streamer(text: str, speed: float = 0.01):
    for char in text:
        time.sleep(speed)
        yield char


# -------------------------- Constructing runnables -------------------------- #
QUESTIONS_PROMPT_TEMPLATE = r"""
You are a professional college professor. And you are creating a test paper.
Generate a set of questions that challenge the students' understanding of the given topic.
The questions should be clear, concise, and relevant to the given topics.
Use $...$ to wrap *every* mathematical expression, including equations, formulas, or symbols.
For math or physics related topics, use LaTeX in inline markdown using the $ symbol. For example: $E=mc^2$.
Wrap full LaTeX blocks like matrices in $$...$$.
Example: $$A = \begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}$$
Wrap inline formulas like $a_{{ij}}$ or $x^2 + y^2 = z^2$.
Do not forget to include both dollar signs.
wrap response questions in list of strings, wrap each question in triple quotes.
Respond only with a list of questions of the format:
[["Question1", "Question2", "Question3"]]

Here are the topics:
{topics}
"""

questions_prompt = PromptTemplate.from_template(QUESTIONS_PROMPT_TEMPLATE)

to_list = lambda question_output: question_output.response_content  # noqa: E731

# ---------------------------------------------------------------------------- #
ANSWER_PROMPT_TEMPLATE = r"""
You are a professional college professor. And based on the notes you provided, the students have 
come up with some questions, your job is to provide answers for each question.
The answers should be detailed and well-explained. 
Use $...$ to wrap *every* mathematical expression, including equations, formulas, or symbols.
Use proper markdown formatting where necessary. Use headers, subheader, dividers etc. 
For math or physics related topics, use Latex in inline markdown using the $ symbol. For example: $E=mc^2$.
Wrap full LaTeX blocks like matrices in $$...$$.
Example: $$A = \begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}$$
Wrap inline formulas like $a_{{ij}}$ or $x^2 + y^2 = z^2$.
Do not forget to include both dollar signs.

Here is the question: 
{question}
    """

answer_prompt = PromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)

# ---------------------------------------------------------------------------- #
questions_chain = questions_prompt | model_questions | to_list
output_parser = StrOutputParser()
answer_chain = answer_prompt | model | output_parser

# ---------------------------------------------------------------------------- #
if st.session_state.user_input != "":
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    con = st.container(border=True)
                    con.markdown(message["content"])

    ph = st.empty()

    if ph.button("Generate Question Answers"):
        ph.empty()

        @st.cache_data
        def cache_questions() -> list[str]:
            return questions_chain.invoke({"topics": st.session_state.user_input})

        def generate_qna() -> None:
            questions = cache_questions()[1::]

            for ques in questions:
                st.session_state.messages.append({"role": "assistant", "content": ques})

                with st.chat_message("user"):
                    st.write_stream(streamer(ques, speed=0.005))

                with st.chat_message("assistant"):
                    con = st.container(border=True)

                    answer = con.write_stream(answer_chain.stream({"question": ques}))

                    st.session_state.messages.append(
                        {"role": "user", "content": answer}
                    )

                    st.divider()

        generate_qna()
else:
    st.write("""Please enter some topics to get started.
             Enter comma separated topics for better results.""")
# ------------------------------------ End ----------------------------------- #