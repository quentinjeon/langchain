"""
PDF 폴더를 돌면서 텍스트 추출 → LangChain 문서 청크 → Pinecone 업로드
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import glob, os
import sys
from pinecone import Pinecone as PineconeClient

# 환경 변수 출력
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX")
host = os.getenv("PINECONE_HOST")

print(f"환경 변수 확인: PINECONE_INDEX={index_name}, PINECONE_HOST={host}")
print(f"API 키 길이: {len(api_key) if api_key else 'None'}")

try:
    # API 키와 환경 변수가 정확히 설정되었는지 확인
    if not api_key or not index_name or not host:
        print("⚠️ Pinecone 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # Pinecone 3.x 버전 API로 초기화
    pc = PineconeClient(api_key=api_key)
    print(f"✅ Pinecone 초기화 성공")
    
    # 인덱스 목록 확인
    indexes = pc.list_indexes()
    index_names = [idx.name for idx in indexes]
    print(f"사용 가능한 인덱스: {index_names}")
    
    if index_name not in index_names:
        print(f"⚠️ {index_name} 인덱스를 찾을 수 없습니다.")
        sys.exit(1)
    
    # 호스트 로깅
    print(f"✅ Pinecone 호스트 사용: {host}")
    
    # 인덱스 연결 - 3.x 버전 방식
    index = pc.Index(host=host)
    print(f"✅ 인덱스 연결 성공: {index_name}")
    
    # OpenAI 임베딩 초기화
    emb = OpenAIEmbeddings()
    print("✅ OpenAI 임베딩 초기화 성공")
    
    # 벡터스토어 직접 생성 - 최신 langchain-pinecone 버전 방식
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=emb,
        text_key="text"
    )
    print("✅ 벡터스토어 연결 성공")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    
    pdf_files = glob.glob("pdf/*.pdf")
    if not pdf_files:
        print("⚠️ PDF 파일을 찾을 수 없습니다. pdf/ 디렉토리에 PDF 파일이 있는지 확인하세요.")
        sys.exit(1)
    
    for path in pdf_files:
        print(f"처리 중: {path}")
        pages = PyPDFLoader(path).load_and_split(splitter)
        vectorstore.add_texts([p.page_content for p in pages], [{"source": os.path.basename(path), "id": i} for i, p in enumerate(pages)])
        print(f"✅ {path} → {len(pages)} chunks 업로드 완료")
    
except Exception as e:
    print(f"❌ 오류 발생: {str(e)}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1) 