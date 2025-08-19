from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

def load_and_process_docs(data_dir="data/"):
    docs = []
    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_dir, file))
            docs.extend(loader.load())
    print(f"Loaded {len(docs)} pages from {len(os.listdir(data_dir))} documents.")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    # Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    # Save to FAISS
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vectorstore/fintech_index")
    print("Vectorstore saved at vectorstore/fintech_index")

if __name__ == "__main__":
    load_and_process_docs()
