from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.config.config import VECTOR_DB, EMBEDDING_MODEL
import logging
import os

logger = logging.getLogger(__name__)

# Cached singleton — avoids reloading the model on every RAG call
_embeddings = None


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings



def build_vector_store():
    documents = []
    data_folder = "data"

    if not os.path.exists(data_folder):
        raise FileNotFoundError("data folder not found")

    for file in os.listdir(data_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_folder, file))
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=_get_embeddings(),
        persist_directory=VECTOR_DB
    )

    print("Vector DB created successfully")
    return vectordb


def _check_vectorstore():
    """Raise a clear error if the vector DB has not been built yet."""
    if not os.path.exists(VECTOR_DB) or not os.listdir(VECTOR_DB):
        raise RuntimeError(
            "Vector store not found. Run build_rag.py first to build the knowledge base."
        )


def retrieve_context(question: str) -> str:
    _check_vectorstore()
    db = Chroma(
        persist_directory=VECTOR_DB,
        embedding_function=_get_embeddings()
    )
    docs = db.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    logger.debug("retrieve_context returned %d docs", len(docs))
    return context


def ask_rag(question: str) -> str:
    _check_vectorstore()
    db = Chroma(
        persist_directory=VECTOR_DB,
        embedding_function=_get_embeddings()
    )
    docs = db.similarity_search(question, k=3)

    if not docs:
        return "I could not find relevant medical guidance in the knowledge base."

    return "\n\n".join(doc.page_content for doc in docs)