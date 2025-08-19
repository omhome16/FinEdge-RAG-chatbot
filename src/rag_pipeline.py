from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from .retriever import get_retriever
from dotenv import load_dotenv

load_dotenv()


def format_docs(docs):
    """Helper function to format documents for the context."""
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain():
    retriever = get_retriever()

    template = """
    You are a professional financial assistant. 
    Answer the user query ONLY using the provided context.
    If the answer is not in the documents, say "The provided documents do not contain an answer."
    Always cite the document name and page number in the answer.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Use Google's Gemini model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

    # This is the modern LCEL (LangChain Expression Language) way to build chains
    rag_chain_from_docs = (
            {
                "context": lambda input: format_docs(input["documents"]),
                "question": lambda input: input["question"],
            }
            | prompt
            | llm
            | StrOutputParser()
    )

    # This chain retrieves documents and then passes them to the generation chain
    rag_chain_with_source = RunnableParallel(
        {"documents": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    return rag_chain_with_source
