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
def summarize(text: str, language: str):
    """Summarize text."""
    if language == "Japanese":
        summary_prompt = "製品やサービス名、会社名、使用事例、具体的なニーズ、それが満たすニーズ、新製品の特徴、製品の生産者とその歴史、競合との差別化、消費者への核心的な約束、そしてこの約束を信じるための情報を考慮して、セクションタイトルや記号なしで100文字以内で製品コンセプトを記述してください。コンセプトは日本語で書かれ、カタカナの借用語は最小限にとどめ、英語のアルファベットは使用しないこと。"
    else:
        summary_prompt = "Write a product concept in under 100 words, with no section titles or symbols; taking into account the product or service name, company name, the product or service use case, the specific need/s it meets, what is new about this product, who produced it and their history and right to make such a product, competitive differentiation, the core promise to the consumer and information that can help me believe this promise."

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

st.title("Generate Concept from URL")

# URL of the image you want to display
image_url = 'https://living-best.tech/wp-content/webp-express/webp-images/uploads/2023/07/LivingBest_Logo_CarterGroup-V2.jpg.webp'

# Use Streamlit's st.image function to display the image
st.image(image_url, caption='')


st.markdown(
    """Please enter the product or service URL below and press ENTER to generate its concept description.  
    You may also select Unstructured Text from the dropdown"""
)

language = st.selectbox("Select Language", ("English", "Japanese"))

selectbox = st.selectbox("URL or Unstructured Text source", ("URL", "Unstructured Text"))

if selectbox == "Raw text":
    raw_text = st.text_area(label="Text", height=300, max_chars=6000)
    if raw_text:
        summarize(raw_text, language)
        if st.session_state.summary:
            st.text_area(
                label="Raw text summary",
                value=st.session_state.summary,
                height=200,
            )
            logging.info(f"Text: {raw_text}\nSummary: {st.session_state.summary}")
            st.button(
                label="Regenerate summary",
                type="secondary",
                on_click=summarize,
                args=[raw_text, language],
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
            summarize(url_text, language)
            if st.session_state.summary:
                st.text_area(
                    label="URL summary", value=st.session_state.summary, height=200
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
                    args=[url_text, language],
                )

if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.summary:
    st.markdown("""---""")
    col1, col2 = st.columns(2)
