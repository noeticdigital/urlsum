"""Streamlit app to summarize URLs"""

# Import from standard library
import logging

# Import from 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components

# Import modules
import scrape as scr
import oai

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)


# Define functions
def summarize(text: str):
    """Summarize text."""
    summary_prompt = "\n\Write a concept summary for this product or service in less than 120 words:\n\n"
    openai = oai.Openai()
    flagged = openai.moderate(text)
    if flagged:
        st.session_state.error = "Input flagged as inappropriate."
        return
    st.session_state.error = ""
    st.session_state.summary = (
        openai.complete(prompt=text + summary_prompt)
        .strip()
        .replace("\n", " ")
        .replace('"', "")
    )


# Render streamlit page
st.set_page_config(page_title="Noetic URL Summariser")
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "error" not in st.session_state:
    st.session_state.error = ""

st.title("Summarize web content")
st.markdown(
    """This mini-app scrapes the paragraphs from a web page and generates a concept summary statement using OpenAI's API"""
)

selectbox = st.selectbox("Raw text or URL source", ("URL", "Raw text"))

if selectbox == "Raw text":
    raw_text = st.text_area(label="Text", height=300, max_chars=6000)
    if raw_text:
        summarize(raw_text)
        if st.session_state.summary:
            st.text_area(
                label="Raw text summary",
                value=st.session_state.summary,
                height=100,
            )
            logging.info(f"Text: {raw_text}\nSummary: {st.session_state.summary}")
            st.button(
                label="Regenerate summary",
                type="secondary",
                on_click=summarize,
                args=[raw_text],
            )

elif selectbox == "URL":
    url = st.text_input(label="URL")
    if url:
        scraper = scr.Scraper()
        response = scraper.request_url(url)
        if "invalid" in str(response).lower():
            st.error(str(response))
        elif response.status_code != 200:
            st.error(f"Response status {response.status_code}")
        else:
            url_text = (
                scraper.extract_content(response)[:6000].strip().replace("\n", " ")
            )
            summarize(url_text)
            if st.session_state.summary:
                st.text_area(
                    label="URL summary", value=st.session_state.summary, height=100
                )
                logging.info(f"URL: {url}\nSummary: {st.session_state.summary}")
                # Force responsive layout for columns also on mobile
                st.write(
                    """<style>
                    [data-testid="column"] {
                        width: calc(50% - 1rem);
                        flex: 1 1 calc(50% - 1rem);
                        min-width: calc(50% - 1rem);
                    }
                    </style>""",
                    unsafe_allow_html=True,
                )
                st.button(
                        label="Regenerate summary",
                        type="secondary",
                        on_click=summarize,
                        args=[url_text],
                    )

if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.summary:
    st.markdown("""---""")
    col1, col2 = st.columns(2)
