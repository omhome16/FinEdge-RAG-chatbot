import streamlit as st
from src.rag_pipeline import get_rag_chain
import os
from dotenv import load_dotenv

load_dotenv()

# Check for the Google API key
if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
    st.stop()

st.set_page_config(page_title="Fintech RAG Chatbot", layout="wide")
st.title("💹 Fintech RAG Chatbot")

# Initialize the chain once and store it in session state
if 'qa_chain' not in st.session_state:
    with st.spinner("Initializing RAG chain..."):
        st.session_state.qa_chain = get_rag_chain()

query = st.text_input("Ask a financial question based on uploaded documents:")

if query:
    qa_chain = st.session_state.qa_chain
    with st.spinner("Searching documents and generating answer..."):
        # V-- CORRECTED: Use the .invoke() method to run the LCEL chain
        response = qa_chain.invoke(query)

    st.write("### Answer")
    st.write(response["answer"])

    # Side panel for sources
    with st.sidebar:
        st.subheader("📑 Sources")
        if response.get("documents"):
            for doc in response["documents"]:
                st.write(f"**File:** {doc.metadata.get('source', 'Unknown')}")
                st.write(f"**Page:** {doc.metadata.get('page', 'N/A')}")
                st.write(doc.page_content[:300] + "...")
                st.write("---")
        else:
            st.write("No source documents found.")

