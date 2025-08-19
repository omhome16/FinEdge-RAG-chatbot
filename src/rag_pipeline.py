from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()


def get_retriever(index_path="vectorstore/fintech_index"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True  # Ensure you trust the source of the index
    )
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    return retriever


def get_rag_chain():

    retriever = get_retriever()

    template = """
    You are a highly knowledgeable financial analyst AI. Your role is to provide precise and professional answers based on the provided documents.

    Follow these rules:
    1.  Analyze the conversation history and the new question to understand the user's intent.
    2.  Answer the question using ONLY the context from the documents.
    3.  If the answer is not found in the context, state clearly: "I could not find information regarding this in the provided documents." Do not try to make up an answer.
    4.  Cite the source document and page number for your answer. Format citations as [source, page X].
    5.  Maintain a professional and formal tone throughout the conversation.

    Conversation History:
    {chat_history}

    Context from Documents:
    {context}

    Question:
    {question}

    Professional Answer:
    """

    prompt = PromptTemplate(
        input_variables=["chat_history", "context", "question"],
        template=template
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.1)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key='answer'
    )

    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    return rag_chain
