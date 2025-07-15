import chromadb
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.schema import Document
from app.config import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

chromadb.telemetry.capture = lambda *args, **kwargs: None
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=settings.gemini_api_key
)
vectorstore = Chroma(
    collection_name="hotlineai_kb",
    embedding_function=embeddings,
    persist_directory=settings.chroma_dir
)

def ingest_documents(path: str):
    loader = DirectoryLoader(path, glob="**/*.*", use_multithreading=True)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    
async def search_knowledge(query: str) -> list[str]:
    docs = vectorstore.similarity_search(query, k=settings.top_k)
    return [d.page_content.strip() for d in docs]