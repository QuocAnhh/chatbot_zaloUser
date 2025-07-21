import chromadb
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from app.config import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import glob
import re

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
    # load hết các file txt và md trong folder data
    file_paths = glob.glob(os.path.join(path, "**/*.md"), recursive=True)
    file_paths.extend(glob.glob(os.path.join(path, "**/*.txt"), recursive=True))
    
    docs = []
    for file_path in file_paths:
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            docs.extend(loader.load())
        except Exception as e:
            print(f"Lỗi khi load file {file_path}: {e}")
            continue
    
    if not docs:
        print("Không tìm thấy document nào để ingest!")
        return
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print(f"Đã ingest {len(chunks)} chunks từ {len(docs)} documents!")

def keyword_search(query: str, all_chunks: list) -> list:
    """Tìm kiếm bằng keyword matching cho các truy vấn về giá"""
    price_keywords = [
        'giá', 'bảng giá', 'chi phí', 'phí', 'tiền', 'đồng',
        'BV120', 'BV500', '1.200.000', '6.000.000', 'gói',
        'tư vấn giá', 'giá dịch vụ', 'giá cả', 'bao nhiêu tiền',
        'cơ bản', 'nâng cao', 'dùng thử', 'miễn phí', 'callbot'
    ]
    
    query_lower = query.lower()
    
    # check nếu query liên quan đến giá
    if any(keyword in query_lower for keyword in price_keywords):
        matching_chunks = []
        for chunk in all_chunks:
            chunk_lower = chunk.lower()
            # tìm chunks chứa các thông tin liên quan đến giá
            pricing_indicators = [
                'bv120', 'bv500', '1.200.000', '6.000.000', 'gói bổ sung',
                'gói dùng thử', 'gói cơ bản', 'gói nâng cao', 'miễn phí',
                '1.000.000đ/tháng', '7.000.000đ/tháng', '60 phút/tháng',
                'các gói dịch vụ', 'bảng giá'
            ]
            
            if any(indicator in chunk_lower for indicator in pricing_indicators):
                matching_chunks.append(chunk)
        
        if matching_chunks:
            return matching_chunks[:settings.top_k]
    
    return []
    
async def search_knowledge(query: str) -> list[str]:
    # test với similarity search
    docs = vectorstore  .similarity_search(query, k=settings.top_k)
    similarity_results = [d.page_content.strip() for d in docs]
    
    # nếu không thấy thì thử search bằng keyword
    if not any('BV120' in result or '1.200.000' in result or 'gói bổ sung' in result for result in similarity_results):
        # lấyy all chunks để  search bằng keyword
        collection = vectorstore._collection
        all_results = collection.get()
        all_chunks = all_results['documents']
        
        keyword_results = keyword_search(query, all_chunks)
        if keyword_results:
            print(f"Fallback to keyword search - found {len(keyword_results)} results")
            return keyword_results
    
    return similarity_results