import streamlit as st
from src.rag_pipeline import get_rag_chain
from src.utils import render_pdf_page_to_image
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Fintech Analyst Chatbot", layout="wide")


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if not os.getenv("GOOGLE_API_KEY"):
    st.error("🔴 GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
    st.stop()

st.title("💹 Financial Analyst Chatbot")
st.caption("An AI assistant powered by your documents")


if 'rag_chain' not in st.session_state:
    with st.spinner("Initializing AI assistant... This may take a moment."):
        st.session_state.rag_chain = get_rag_chain()
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How can I help you with your financial documents today?"}]

display_chat_history()


if prompt := st.chat_input("Ask a question about your documents..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing documents and generating response..."):
        rag_chain = st.session_state.rag_chain

        response = rag_chain({"question": prompt})

        answer = response.get("answer", "Sorry, I encountered an issue and could not generate a response.")

        st.session_state.messages.append({"role": "assistant", "content": answer})

        with st.chat_message("assistant"):
            st.markdown(answer)

    with st.sidebar:
        st.subheader("📑 Source Documents")
        if response.get("source_documents"):
            
            unique_sources = {(doc.metadata['source'], doc.metadata['page']) for doc in response["source_documents"]}

            for source, page in sorted(list(unique_sources)):
                with st.expander(f"**File:** {os.path.basename(source)} - **Page:** {page + 1}"):

                    image_data = render_pdf_page_to_image(source, page)
                    if image_data:
                        st.image(image_data, caption=f"Page {page + 1}")
                    else:
                        st.warning("Could not render page image.")
        else:
            st.info("No source documents were cited for this response.")