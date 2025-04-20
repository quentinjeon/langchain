from fastapi import Depends
from pymongo import MongoClient
from pinecone import Pinecone
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mongo():
    client = MongoClient(os.getenv("MONGO_URL"))
    return client[os.getenv("MONGO_DB")]

def get_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX")
    host = os.getenv("PINECONE_HOST")
    
    logger.info(f"Pinecone 초기화: 인덱스={index_name}, 호스트={host}, API 키 길이={len(api_key) if api_key else 'None'}")
    
    # Pinecone 3.x 버전 API로 초기화
    pc = Pinecone(api_key=api_key)
    
    # 사용 가능한 인덱스 출력
    try:
        indexes = pc.list_indexes()
        logger.info(f"사용 가능한 Pinecone 인덱스: {[idx.name for idx in indexes]}")
    except Exception as e:
        logger.error(f"인덱스 목록 가져오기 실패: {str(e)}")
    
    # 호스트 로깅
    logger.info(f"Pinecone 호스트 사용: {host}")
    
    # 명시적으로 호스트 지정
    return pc.Index(host=host) 