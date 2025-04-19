from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
import os
import logging
import pinecone

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_chain():
    # 환경 변수 로깅
    env = os.getenv("PINECONE_ENV")
    index_name = os.getenv("PINECONE_INDEX")
    api_key = os.getenv("PINECONE_API_KEY")
    
    logger.info(f"QA 체인 빌드: Pinecone 환경={env}, 인덱스={index_name}")
    
    # Pinecone 초기화 (여기서 한 번 더 초기화)
    try:
        env = "us-east-1-aws"  # 강제 환경 설정
        logger.info(f"QA 체인에서 Pinecone 환경 강제 설정: {env}")
        
        pinecone.init(api_key=api_key, environment=env)
        indexes = pinecone.list_indexes()
        logger.info(f"사용 가능한 인덱스: {indexes}")
    except Exception as e:
        logger.error(f"Pinecone 초기화 오류: {str(e)}")
    
    # 구 버전의 OpenAI 임베딩 사용
    embeddings = OpenAIEmbeddings()
    logger.info("OpenAI 임베딩 초기화 완료")
    
    try:
        vectordb = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=embeddings
        )
        logger.info("Pinecone 벡터스토어 연결 성공")
        
        retriever = vectordb.as_retriever(search_kwargs={"k": 4})
        logger.info("Retriever 생성 완료")

        llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0
        )
        logger.info("ChatOpenAI 모델 초기화 완료")
        
        chain = ConversationalRetrievalChain.from_llm(llm, retriever)
        logger.info("대화형 검색 체인 생성 완료")
        
        return chain
    except Exception as e:
        logger.error(f"체인 생성 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise 