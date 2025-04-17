"""
PDF 폴더를 돌면서 텍스트 추출 → LangChain 문서 청크 → Pinecone 업로드
"""
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import glob, os, pinecone

pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))

# 구 버전 OpenAI 임베딩 사용
emb = OpenAIEmbeddings()

vectorstore = Pinecone.from_existing_index(index_name=os.getenv("PINECONE_INDEX"), embedding=emb)

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

for path in glob.glob("pdf/*.pdf"):
    pages = PyPDFLoader(path).load_and_split(splitter)
    vectorstore.add_texts([p.page_content for p in pages], [{"source": os.path.basename(path), "id": i} for i, p in enumerate(pages)])
    print(f"✅ {path} → {len(pages)} chunks 업로드 완료") 