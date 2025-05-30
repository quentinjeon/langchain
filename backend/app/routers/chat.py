from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..chains.qa_chain import build_chain
from ..deps import get_mongo
import logging
import traceback

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
chain = build_chain()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
def chat(req: ChatRequest, db = Depends(get_mongo)):
    try:
        logger.info(f"채팅 요청 받음: 세션={req.session_id}, 메시지 길이={len(req.message)}")
        
        # 메시지 이력 가져오기
        history = db.history.find_one({"_id": req.session_id}) or {"messages": []}
        logger.info(f"이전 대화 이력: {len(history['messages'])}개 메시지")
        
        # 임시 응답 (Pinecone 연결 오류 시 사용)
        if not req.message.strip():
            return {"answer": "메시지가 비어 있습니다. 질문을 입력해주세요."}
            
        try:
            # LangChain을 통한 응답 생성 시도
            logger.info("LangChain에 질문 전달 중...")
            response = chain({"question": req.message, "chat_history": history["messages"]})
            logger.info("응답 받음: 길이=" + str(len(response["answer"])))
            
            # 응답 저장
            history["messages"].append((req.message, response["answer"]))
            db.history.update_one({"_id": req.session_id}, {"$set": history}, upsert=True)
            
            return {"answer": response["answer"]}
            
        except Exception as e:
            # Pinecone 또는 OpenAI 연결 오류 처리
            error_msg = str(e)
            logger.error(f"외부 서비스 오류: {error_msg}")
            logger.error(traceback.format_exc())
            
            # 벡터 DB에 데이터가 없을 경우 안내 메시지
            if "SSLEOFError" in error_msg or "Max retries exceeded" in error_msg:
                return {
                    "answer": "Pinecone 벡터 DB 연결에 문제가 있습니다. PDF 문서가 업로드되었는지 확인해주세요. 지금은 일반 대화만 가능합니다."
                }
            
            # 기타 LangChain 오류
            raise HTTPException(
                status_code=500, 
                detail=f"AI 응답 생성 중 오류가 발생했습니다: {error_msg[:200]}"
            )
        
    except Exception as e:
        # 전체 예외 처리
        logger.error(f"채팅 처리 중 오류: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 