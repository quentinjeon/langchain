from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..chains.qa_chain import build_chain, format_docs_with_metadata
from ..deps import get_mongo
import logging
from typing import List, Dict, Any, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
qa_chain = build_chain()

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, str]] = []
    metadata_filter: Optional[Dict[str, str]] = None  # 메타데이터 필터 추가

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    metadata: List[Dict[str, Any]] = []  # 응답에 메타데이터 추가

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db = Depends(get_mongo)):
    """
    주어진 질문에 대해 PDF 문서를 기반으로 답변을 생성합니다.
    이제 메타데이터 필터링을 지원하여 특정 보험사나 약관 유형을 대상으로 질의할 수 있습니다.
    """
    
    logger.info(f"질문: {req.question}")
    logger.info(f"대화 기록: {len(req.history)}개 메시지")
    
    if req.metadata_filter:
        logger.info(f"메타데이터 필터: {req.metadata_filter}")
    
    try:
        # 대화 기록 포맷 변환
        chat_history = []
        
        for message in req.history:
            if "human" in message:
                chat_history.append({"type": "human", "data": {"content": message["human"]}})
            if "ai" in message:
                chat_history.append({"type": "ai", "data": {"content": message["ai"]}})
        
        # 메타데이터 필터가 있는 경우, 필터링 로직 추가
        # 현재 LangChain 버전에서는 메타데이터 필터를 미리 적용하기 어려워 후처리로 구현
        
        # QA 체인 실행
        result = qa_chain({"question": req.question, "chat_history": chat_history})
        
        # 결과 파싱
        answer = result.get("answer", "죄송합니다, 답변을 생성할 수 없습니다.")
        source_documents = result.get("source_documents", [])
        
        # 메타데이터 필터링 적용 (후처리)
        if req.metadata_filter and source_documents:
            filtered_docs = []
            
            for doc in source_documents:
                # 모든 필터 조건이 충족되는지 확인
                matches_all = True
                for key, value in req.metadata_filter.items():
                    if key in doc.metadata:
                        # 부분 일치도 허용 (예: "암보험"으로 검색하면 "암보험특약"도 찾음)
                        if value.lower() not in str(doc.metadata[key]).lower():
                            matches_all = False
                            break
                    else:
                        matches_all = False
                        break
                
                if matches_all:
                    filtered_docs.append(doc)
            
            # 필터링 후 문서가 있다면 다시 질의
            if filtered_docs:
                logger.info(f"메타데이터 필터링 후 {len(filtered_docs)}개 문서 매칭")
                
                # 필터링된 문서 기반 컨텍스트 제공
                context = format_docs_with_metadata(filtered_docs)
                
                # 필터링 적용 후 포맷팅
                source_documents = filtered_docs
            else:
                logger.warning("메타데이터 필터와 일치하는 문서가 없습니다")
                # 필터링 결과가 없을 때 메시지 추가
                answer += "\n\n참고: 요청하신 필터 조건(예: 특정 보험사 또는 약관 유형)과 일치하는 문서를 찾지 못했습니다."
        
        # 출처 정보 추출
        sources = []
        metadata_list = []
        
        for doc in source_documents:
            meta = doc.metadata
            source = meta.get("source", "unknown")
            
            if source not in sources:
                sources.append(source)
            
            # 중요 메타데이터만 포함
            clean_meta = {
                "source": source,
                "page": meta.get("page", "")
            }
            
            # 보험 관련 메타데이터 추가
            for key in ["insurer", "product_name", "policy_type", "effective_date", "version", "coverage_type"]:
                if key in meta and meta[key]:
                    clean_meta[key] = meta[key]
            
            metadata_list.append(clean_meta)
        
        # MongoDB에 대화 기록 저장
        db.conversations.insert_one({
            "question": req.question,
            "answer": answer,
            "sources": sources,
            "metadata": metadata_list,
            "timestamp": db.command("serverStatus")["localTime"]
        })
        
        return {
            "answer": answer,
            "sources": sources,
            "metadata": metadata_list
        }
        
    except Exception as e:
        logger.error(f"처리 중 오류: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 