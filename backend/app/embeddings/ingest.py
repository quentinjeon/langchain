"""
PDF 폴더를 돌면서 텍스트 추출 → LangChain 문서 청크 → Pinecone 업로드
메타데이터 구조화 지원 (보험 약관 전용)
"""
import json
import argparse
import os
import glob
import pinecone
from datetime import datetime
from typing import Dict, Any, List, Optional

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

# 명령행 인자 파싱
parser = argparse.ArgumentParser(description='PDF 문서를 Pinecone에 업로드하는 스크립트')
parser.add_argument('--metadata', type=str, help='JSON 형식의 메타데이터 파일 경로')
parser.add_argument('--pdf_dir', type=str, default='pdf', help='PDF 파일이 있는 디렉토리 (기본값: pdf)')
args = parser.parse_args()

# Pinecone 초기화
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))

# OpenAI 임베딩 초기화
emb = OpenAIEmbeddings()

# Pinecone 벡터스토어 초기화
vectorstore = Pinecone.from_existing_index(index_name=os.getenv("PINECONE_INDEX"), embedding=emb)

# 텍스트 스플리터 설정
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

# 메타데이터 로드 (있는 경우)
metadata_mapping = {}
if args.metadata and os.path.exists(args.metadata):
    try:
        with open(args.metadata, 'r', encoding='utf-8') as f:
            metadata_mapping = json.load(f)
        print(f"📋 메타데이터 파일 로드 완료: {len(metadata_mapping)} 파일 정보 포함")
    except Exception as e:
        print(f"⚠️ 메타데이터 파일 로드 실패: {e}")

def get_metadata_for_file(filename: str) -> Dict[str, Any]:
    """파일 이름에 해당하는 메타데이터를 반환합니다."""
    base_filename = os.path.basename(filename)
    
    # 메타데이터 매핑에서 찾기
    if base_filename in metadata_mapping:
        return metadata_mapping[base_filename]
    
    # 파일명으로 메타데이터 추측 (필요한 경우)
    return {
        "source": base_filename,
        "upload_date": datetime.now().isoformat()
    }

def enhance_metadata(base_metadata: Dict[str, Any], page_num: int) -> Dict[str, Any]:
    """기본 메타데이터에 페이지 정보 등을 추가합니다."""
    enhanced = base_metadata.copy()
    enhanced["page"] = page_num
    return enhanced

# PDF 파일 목록 가져오기
pdf_dir = args.pdf_dir
pdf_pattern = os.path.join(pdf_dir, "*.pdf")
pdf_files = glob.glob(pdf_pattern)

if not pdf_files:
    print(f"⚠️ {pdf_pattern} 경로에 PDF 파일이 없습니다.")
    exit(1)

print(f"🔍 {len(pdf_files)}개의 PDF 파일을 찾았습니다.")

# 메타데이터 입력 도우미 함수
def prompt_for_metadata(filename: str) -> Dict[str, Any]:
    """사용자에게 메타데이터 입력을 요청합니다."""
    print(f"\n📄 파일: {filename}에 대한 메타데이터 입력")
    
    metadata = {
        "source": os.path.basename(filename),
        "upload_date": datetime.now().isoformat()
    }
    
    # 기본 메타데이터 필드
    fields = [
        ("insurer", "보험사명 (예: 교보생명)"),
        ("product_name", "상품명 (예: 표적항암보장보험)"),
        ("policy_type", "약관종류 (예: 주계약/특약/갱신형)"),
        ("effective_date", "시행일자 (YYYY-MM-DD)"),
        ("version", "버전 (예: v1.3)"),
        ("coverage_type", "보장유형 (예: 암보험/상해보험/생명보험)")
    ]
    
    # 각 필드 입력 받기
    for field_name, description in fields:
        value = input(f"{description}: ").strip()
        if value:  # 값이 있을 때만 저장
            metadata[field_name] = value
    
    return metadata

# 각 PDF 처리
for pdf_path in pdf_files:
    filename = os.path.basename(pdf_path)
    
    # 이미 메타데이터가 있는지 확인
    if filename not in metadata_mapping:
        # 없으면 사용자에게 입력 요청
        print(f"\n🆕 새 파일: {filename}에 대한 메타데이터가 필요합니다.")
        file_metadata = prompt_for_metadata(pdf_path)
        
        # 메타데이터 매핑에 추가 (나중에 저장)
        metadata_mapping[filename] = file_metadata
    else:
        # 있으면 기존 메타데이터 사용
        file_metadata = metadata_mapping[filename]
        print(f"\n📋 {filename}에 대한 메타데이터를 로드했습니다.")
    
    try:
        # PDF 로드 및 분할
        print(f"📖 {pdf_path} 로드 중...")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split(splitter)
        
        # 각 페이지별 메타데이터 강화
        enhanced_metadata = []
        for i, page in enumerate(pages):
            page_metadata = enhance_metadata(file_metadata, i + 1)
            enhanced_metadata.append(page_metadata)
        
        # Pinecone에 업로드
        vectorstore.add_texts(
            [p.page_content for p in pages],
            enhanced_metadata
        )
        
        print(f"✅ {pdf_path} → {len(pages)} chunks 업로드 완료")
        
        # 메타데이터 세부 정보 출력
        meta_info = ", ".join([f"{k}: {v}" for k, v in file_metadata.items() if k != "source"])
        print(f"📊 적용된 메타데이터: {meta_info}")
        
    except Exception as e:
        print(f"❌ {pdf_path} 처리 실패: {e}")

# 업데이트된 메타데이터 저장
if args.metadata:
    try:
        with open(args.metadata, 'w', encoding='utf-8') as f:
            json.dump(metadata_mapping, f, ensure_ascii=False, indent=2)
        print(f"\n💾 메타데이터 파일 저장 완료: {args.metadata}")
    except Exception as e:
        print(f"⚠️ 메타데이터 파일 저장 실패: {e}")

print("\n🎉 모든 처리가 완료되었습니다!") 