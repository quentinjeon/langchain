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

def build_report_chain():
    """
    PDF 문서를 기반으로 특정 주제에 관한 보고서를 생성하는 체인을 구축합니다.
    """
    # 환경 변수 로깅
    index_name = os.getenv("PINECONE_INDEX")
    api_key = os.getenv("PINECONE_API_KEY")
    host = os.getenv("PINECONE_HOST")
    
    logger.info(f"보고서 체인 빌드: Pinecone 인덱스={index_name}, 호스트={host}")
    
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
    
    # OpenAI 임베딩 초기화
    embeddings = OpenAIEmbeddings()
    logger.info("OpenAI 임베딩 초기화 완료")
    
    try:
        # Pinecone 벡터스토어 생성
        vectordb = PineconeVectorStore(
            index=index,
            embedding=embeddings,
            text_key="text"
        )
        logger.info("Pinecone 벡터스토어 연결 성공")
        
        # 관련 문서를 검색하는 retriever 생성 (k 값 증가)
        retriever = vectordb.as_retriever(search_kwargs={"k": 10})
        logger.info("Retriever 생성 완료")

        # 더 강력한 모델 사용 (보고서 생성에 적합)
        llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0.5  # 약간의 창의성 허용
        )
        logger.info("ChatOpenAI 모델 초기화 완료")
        
        # 문서 컨텍스트 형식 처리
        def format_docs(docs):
            return "\n\n".join([f"문서 출처: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs])
        
        # 보고서 생성을 위한 프롬프트 템플릿
        report_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 전문 보고서 작성자입니다. 주어진 문서와 주제를 기반으로 전문적이고 체계적인 보고서를 작성해야 합니다.
            
아래 문서에서 '주제'와 관련된 모든 정보를 추출하고, 다음 형식의 전문 보고서를 한글로 작성하세요:

1. 요약: 주제에 대한 간략한 요약 (1-2문단)
2. 주요 내용: 문서에서 발견된 주제 관련 주요 정보 (3-5개 섹션으로 구성)
3. 분석: 정보에 대한 분석 및 통찰
4. 결론: 주요 시사점 및 결론
5. 참고 자료: 사용된 문서 출처

주어진 문서 내용만 사용하고, 근거 없는 내용을 절대 작성하지 마세요. 객관적이고 사실에 기반한 보고서를 작성하세요.

참고 문서:
{context}"""),
            ("user", "다음 주제에 대한, 문서 내용만 사용하는 보고서를 작성해주세요: {topic}")
        ])

        # 보고서 생성 체인 구성
        report_chain = (
            {
                "context": retriever | format_docs,
                "topic": RunnablePassthrough()
            }
            | report_prompt
            | llm
            | StrOutputParser()
        )

        logger.info("보고서 생성 체인 구성 완료")
       
        return report_chain
    except Exception as e:
        logger.error(f"체인 생성 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise 