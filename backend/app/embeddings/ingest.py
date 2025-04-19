"""
PDF 폴더를 돌면서 텍스트 추출 → LangChain 문서 청크 → Pinecone 업로드
"""
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import glob, os, pinecone
import sys

# 환경 변수 출력
api_key = os.getenv("PINECONE_API_KEY")
env = os.getenv("PINECONE_ENV")
index_name = os.getenv("PINECONE_INDEX")
host = os.getenv("PINECONE_HOST")

print(f"환경 변수 확인: PINECONE_ENV={env}, PINECONE_INDEX={index_name}, PINECONE_HOST={host}")
print(f"API 키 길이: {len(api_key) if api_key else 'None'}")

try:
    # API 키와 환경 변수가 정확히 설정되었는지 확인
    if not api_key or not env or not index_name:
        print("⚠️ Pinecone 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 명시적으로 실제 region 설정
    env = "us-east-1"
    print(f"환경 변수 강제 설정: {env}")
    
    # Pinecone 초기화
    pinecone.init(api_key=api_key, environment=env)
    print(f"✅ Pinecone 초기화 성공 - 환경: {env}")
    
    # 인덱스 목록 확인
    indexes = pinecone.list_indexes()
    print(f"사용 가능한 인덱스: {indexes}")
    
    if index_name not in indexes:
        print(f"⚠️ {index_name} 인덱스를 찾을 수 없습니다.")
        sys.exit(1)
    
    # 호스트 로깅 (참고용)
    print(f"✅ Pinecone 호스트 참고용: {host}")
    
    # 인덱스 연결 - 구 버전 Pinecone 방식
    index = pinecone.Index(index_name)
    print(f"✅ 인덱스 연결 성공: {index_name}")
    
    # 구 버전 OpenAI 임베딩 사용
    emb = OpenAIEmbeddings()
    print("✅ OpenAI 임베딩 초기화 성공")
    
    # 벡터스토어 직접 생성 - 구 버전 방식
    vectorstore = Pinecone.from_existing_index(
        index_name=index_name, 
        embedding=emb
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