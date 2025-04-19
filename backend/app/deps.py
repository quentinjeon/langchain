from fastapi import Depends
from pymongo import MongoClient
import pinecone, os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mongo():
    client = MongoClient(os.getenv("MONGO_URL"))
    return client[os.getenv("MONGO_DB")]

def get_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    env = os.getenv("PINECONE_ENV") 
    index_name = os.getenv("PINECONE_INDEX")
    host = os.getenv("PINECONE_HOST")
    
    logger.info(f"Pinecone 초기화: 환경={env}, 인덱스={index_name}, 호스트={host}, API 키 길이={len(api_key) if api_key else 'None'}")
    
    # 명시적으로 실제 region 설정
    env = "us-east-1"
    logger.info(f"환경 변수 강제 설정: {env}")
    
    # 구 버전 Pinecone: host 파라미터 미지원
    pinecone.init(api_key=api_key, environment=env)
    
    # 사용 가능한 인덱스 출력
    try:
        indexes = pinecone.list_indexes()
        logger.info(f"사용 가능한 Pinecone 인덱스: {indexes}")
    except Exception as e:
        logger.error(f"인덱스 목록 가져오기 실패: {str(e)}")
    
    # 호스트 로깅 (참고용)
    logger.info(f"Pinecone 호스트 참고용: {host}")
    
    return pinecone.Index(index_name) 