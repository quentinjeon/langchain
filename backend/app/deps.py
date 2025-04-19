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
    
    logger.info(f"Pinecone 초기화: 환경={env}, 인덱스={index_name}, API 키 길이={len(api_key) if api_key else 'None'}")
    
    # 강제로 올바른 환경 사용 (디버깅용)
    env = "us-east-1-aws"
    logger.info(f"환경 변수 강제 설정: {env}")
    
    pinecone.init(api_key=api_key, environment=env)
    
    # 사용 가능한 인덱스 출력
    try:
        indexes = pinecone.list_indexes()
        logger.info(f"사용 가능한 Pinecone 인덱스: {indexes}")
    except Exception as e:
        logger.error(f"인덱스 목록 가져오기 실패: {str(e)}")
    
    return pinecone.Index(index_name) 