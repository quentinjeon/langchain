from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
import os
import logging
from pinecone import Pinecone as PineconeClient
from langchain_core.prompts import ChatPromptTemplate

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_chain():
    # 환경 변수 로깅
    index_name = os.getenv("PINECONE_INDEX")
    api_key = os.getenv("PINECONE_API_KEY")
    host = os.getenv("PINECONE_HOST")
    
    logger.info(f"QA 체인 빌드: Pinecone 인덱스={index_name}, 호스트={host}")
    
    # Pinecone 3.x 버전 API로 초기화
    try:
        pc = PineconeClient(api_key=api_key)
        indexes = pc.list_indexes()
        logger.info(f"사용 가능한 인덱스: {[idx.name for idx in indexes]}")
        
        # 명시적 호스트 지정으로 인덱스 가져오기
        index = pc.Index(host=host)
        logger.info("Pinecone 인덱스 연결 성공")
    except Exception as e:
        logger.error(f"Pinecone 초기화 오류: {str(e)}")
        raise
    
    # OpenAI 임베딩 초기화 - 기본 1536 차원
    embeddings = OpenAIEmbeddings()
    logger.info("OpenAI 임베딩 초기화 완료")
    
    try:
        # Pinecone 벡터스토어 생성 - 최신 langchain-pinecone 버전 방식
        vectordb = PineconeVectorStore(
            index=index,
            embedding=embeddings,
            text_key="text"
        )
        logger.info("Pinecone 벡터스토어 연결 성공")
        
        retriever = vectordb.as_retriever(search_kwargs={"k": 4})
        logger.info("Retriever 생성 완료")

        llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0
        )
        logger.info("ChatOpenAI 모델 초기화 완료")
        
        # 문서 컨텍스트 형식 처리
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # 프롬프트 템플릿 정의
        prompt = ChatPromptTemplate.from_messages([
            ("system", "다음은 문서 기반 Q&A 시스템입니다. 관련 문서를 참고하여 사용자 질문에 답하세요.\n\n참고 문서:\n{context}"),
            ("user", "{question}")
        ])

        # 간단한 파이프라인 구성
        qa_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )

        logger.info("대화형 검색 체인 생성 완료")
       
        return qa_chain
    except Exception as e:
        logger.error(f"체인 생성 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise 