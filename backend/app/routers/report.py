from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..chains.report_chain import build_report_chain
from ..deps import get_mongo
import logging
import traceback
from typing import Optional
import uuid
from bson import ObjectId

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
report_chain = build_report_chain()

class ReportRequest(BaseModel):
    """보고서 생성 요청 모델"""
    session_id: Optional[str] = None
    topic: str
    max_length: Optional[int] = 2000  # 보고서 최대 길이 (기본값 2000자)

class ReportResponse(BaseModel):
    """보고서 응답 모델"""
    report: str
    sources: list = []  # 출처 정보
    reportId: Optional[str] = None  # 보고서 ID

@router.post("/report", response_model=ReportResponse)
def generate_report(req: ReportRequest, db = Depends(get_mongo)):
    """
    주어진 주제에 대한 보고서를 생성합니다.
    PDF 문서에서 관련 정보를 추출하여 체계적인 보고서를 작성합니다.
    """
    try:
        # session_id가 없는 경우 기본값 생성
        if not req.session_id:
            req.session_id = str(uuid.uuid4())
            
        logger.info(f"보고서 생성 요청: 세션={req.session_id}, 주제={req.topic}")
        
        # 주제가 비어있는지 확인
        if not req.topic.strip():
            return {"report": "주제가 비어 있습니다. 보고서를 생성할 주제를 입력해주세요.", "sources": []}
            
        try:
            # 보고서 생성 체인 실행
            logger.info("보고서 생성 체인 실행 중...")
            report = report_chain.invoke(req.topic)
            
            # 너무 긴 경우 잘라내기
            if req.max_length and len(report) > req.max_length:
                report = report[:req.max_length] + "... (보고서가 너무 길어 일부 내용이 생략되었습니다)"
            
            logger.info(f"보고서 생성 완료: 길이={len(report)}")
            
            # 보고서 저장
            report_record = {
                "session_id": req.session_id,
                "topic": req.topic,
                "report": report,
                "timestamp": db.command("serverStatus")["localTime"]
            }
            
            result = db.reports.insert_one(report_record)
            report_id = str(result.inserted_id)
            logger.info(f"보고서 저장 완료: ID={report_id}")
            
            return {"report": report, "sources": [], "reportId": report_id}
            
        except Exception as e:
            # 외부 서비스 오류 처리
            error_msg = str(e)
            logger.error(f"외부 서비스 오류: {error_msg}")
            logger.error(traceback.format_exc())
            
            # 오류 메시지에 따른 적절한 응답
            if "SSLEOFError" in error_msg or "Max retries exceeded" in error_msg:
                return {
                    "report": "Pinecone 벡터 DB 연결에 문제가 있습니다. PDF 문서가 업로드되었는지 확인해주세요.",
                    "sources": []
                }
            
            # 기타 오류
            raise HTTPException(
                status_code=500, 
                detail=f"보고서 생성 중 오류가 발생했습니다: {error_msg[:200]}"
            )
        
    except Exception as e:
        # 전체 예외 처리
        logger.error(f"보고서 처리 중 오류: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{report_id}")
def get_report(report_id: str, db = Depends(get_mongo)):
    """
    보고서 ID로 저장된 보고서를 조회합니다.
    """
    try:
        logger.info(f"보고서 조회 요청: ID={report_id}")
        
        # ObjectId로 변환하여 MongoDB에서 조회
        try:
            report = db.reports.find_one({"_id": ObjectId(report_id)})
        except Exception as e:
            logger.error(f"ObjectId 변환 오류: {str(e)}")
            raise HTTPException(status_code=400, detail=f"잘못된 보고서 ID 형식: {report_id}")
        
        if not report:
            logger.warning(f"보고서를 찾을 수 없음: ID={report_id}")
            raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다")
        
        # MongoDB ObjectId를 문자열로 변환
        report["id"] = str(report["_id"])
        report["_id"] = str(report["_id"])
        report["content"] = report["report"]  # 프론트엔드의 예상 필드 이름과 일치시킴
        report["createdAt"] = report["timestamp"]
        
        logger.info(f"보고서 조회 성공: ID={report_id}")
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"보고서 조회 중 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"보고서 조회 중 오류가 발생했습니다: {str(e)}") 