import streamlit as st
from langchain_groq import ChatGroq
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

# -------------------------- Constructing runnables -------------------------- #
NOTES_PROMPT_TEMPLATE = r"""
You are a professional college professor. Generate a set of comprehensive notes based on the topic provided.
The notes should be detailed, well-structured, and easy to understand. 
Use $...$ to wrap *every* mathematical expression, including equations, formulas, or symbols.
The notes should be suitable for students in their final year of high school or the first year of university.
Use proper markdown formatting where necessary. Use headers, subheader, dividers etc. 
For math or physics related topics, use Latex in inline markdown using the $ symbol. For example: $E=mc^2$.
Wrap full LaTeX blocks like matrices in $$...$$.
Example: $$A = \begin{{bmatrix}} 1 & 2 \\ 3 & 4 \end{{bmatrix}}$$
Wrap inline formulas like $a_{{ij}}$ or $x^2 + y^2 = z^2$.
Do not forget to include both dollar signs.

Here are the topics:
{topics}
    """

notes_prompt = PromptTemplate.from_template(NOTES_PROMPT_TEMPLATE)

# ---------------------------------------------------------------------------- #
output_parser = StrOutputParser()
notes_chain = notes_prompt | model | output_parser

# ---------------------------------------------------------------------------- #

        
# ---------------------------------------------------------------------------- #

if st.session_state.user_input != "":
    
    if st.session_state.notes is None:
        ph = st.empty()
        if ph.button("Generate Notes"):
            ph.empty()
            con = st.container(border=True)

            st.session_state.notes = con.write_stream(
                notes_chain.stream({"topics": st.session_state.user_input}),
            )
            st.divider()
    else:
        con = st.container(border=True)
        con.markdown(st.session_state.notes)
else:
    st.write("""Please enter some topics to get started.
             Enter comma separated topics for better results.""")