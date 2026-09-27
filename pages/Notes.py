import streamlit as st
from duckduckgo_search import DDGS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

st.set_page_config(page_title="Study Notes", page_icon="📝", layout="wide")


# -------------------------- Check API Key & Topics -------------------------- #
if "groq_api_key" not in st.session_state or not st.session_state.groq_api_key:
    st.error("Missing Groq API Key. Please set it in the sidebar on the home page.")
    st.stop()

if "user_input" not in st.session_state or not st.session_state.user_input.strip():
    st.info(" Please enter your study topics on the 'Get started' home page first.")
    st.stop()

topics = st.session_state.user_input.strip()


# ------------------------ Fetch Online Search Results ----------------------- #
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_online_resources(query: str, max_results: int = 4) -> list[dict]:
    """Fetches web search results using DuckDuckGo Search."""
    results = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(keywords=query, max_results=max_results))
            for r in raw_results:
                results.append(
                    {
                        "title": r.get("title", "No Title"),
                        "link": r.get("href", "#"),
                        "snippet": r.get("body", "No description available."),
                    }
                )
    except Exception as e:
        st.warning(f"Unable to fetch online search results: {e}")
    return results


# ---------------------- Display Web Search Results Section ---------------------- #
st.subheader("🌐 Relevant Web Search Results & Resources")
st.caption(f"Fetching real-time online references for: **{topics}**")

with st.spinner("Searching the web for latest articles and resources..."):
    search_results = fetch_online_resources(topics)

if search_results:
    cols = st.columns(2)
    for idx, item in enumerate(search_results):
        col = cols[idx % 2]
        with col:
            with st.container(border=True):
                st.markdown(f"#### [{item['title']}]({item['link']})")
                st.write(item["snippet"])
                st.caption(f"🔗 [Visit Source]({item['link']})")
else:
    st.info("No online search results found. Proceeding with AI generation.")

st.divider()

# --------------------------- Generate Notes Prompt --------------------------- #
NOTES_SYSTEM_PROMPT = r"""You are an elite university professor crafting comprehensive study notes.

CRITICAL LATEX FORMATTING RULES:
1. ALWAYS use double dollar signs ($$) on their own lines for block/display equations.
2. ALWAYS use single dollar signs ($) for inline math (e.g., $E=mc^2$).
3. NEVER use square brackets like [ ... ] or \[ ... \] to enclose math equations.

Formatting Guidelines:
- Organize notes into clear Markdown headings (##, ###).
- Use bullet points, bold key terms, and summary blocks for readability.
- Cover core concepts, theoretical foundations, key definitions, and real-world applications."""

notes_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", NOTES_SYSTEM_PROMPT),
        (
            "human",
            "Generate detailed study notes for the following topic(s):\n{topics}",
        ),
    ]
)

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.4,
    api_key=st.session_state.groq_api_key,
)

notes_chain = notes_prompt | model | StrOutputParser()

# ----------------------------- Notes Generation UI ----------------------------- #
if st.session_state.notes is None:
    if st.button("✨ Generate Notes", use_container_width=True):
        with st.spinner("Synthesizing comprehensive notes..."):
            notes_stream = notes_chain.stream({"topics": topics})
            # st.write_stream streams to the UI and returns the complete text string
            st.session_state.notes = st.write_stream(notes_stream)

# Always show the latest notes, even after unrelated reruns
elif st.session_state.get("notes"):
    st.write(st.session_state.notes)
