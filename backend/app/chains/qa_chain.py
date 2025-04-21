from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
import os
import logging
import pinecone
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 메타데이터 정보를 포함하는 프롬프트 템플릿
CONDENSE_QUESTION_PROMPT = """
주어진 대화와 후속 질문을 바탕으로, 후속 질문을 독립적인 질문으로 재구성하세요.

대화 내역:
{chat_history}

후속 질문: {question}

독립적인 질문:
"""

QA_PROMPT_WITH_METADATA = """
당신은 보험 약관 전문가입니다. 문서의 내용만을 기반으로 답변하세요.

질문: {question}

다음 문서 조각들을 통해 답변을 생성하세요. 각 문서에는 보험 약관 관련 메타데이터가 포함되어 있습니다:

{context}

메타데이터를 활용하여 정보의 출처와 적용 범위를 명확히 언급해주세요. 예를 들어, "교보생명의 암보험 약관(2023년 버전)에 따르면..."과 같이 출처를 명시하세요.

여러 보험사나 약관 버전이 있다면, 차이점을 명확히 설명해주세요. 시행일자가 다른 경우, 최신 정보를 우선적으로 제공하되 변경 사항을 언급하는 것이 좋습니다.

모르는 내용이나 문서에 없는 정보에 대해서는 "제공된 약관에서 해당 정보를 찾을 수 없습니다"라고 정직하게 답변하세요.

답변:
"""

def format_docs_with_metadata(docs):
    """문서와 메타데이터를 포맷팅합니다."""
    formatted_docs = []
    
    for i, doc in enumerate(docs):
        # 메타데이터 추출
        metadata = doc.metadata
        source = metadata.get("source", "알 수 없는 출처")
        insurer = metadata.get("insurer", "")
        product_name = metadata.get("product_name", "")
        policy_type = metadata.get("policy_type", "")
        effective_date = metadata.get("effective_date", "")
        version = metadata.get("version", "")
        coverage_type = metadata.get("coverage_type", "")
        page = metadata.get("page", "")
        
        # 메타데이터 문자열 구성
        meta_parts = []
        if insurer:
            meta_parts.append(f"보험사: {insurer}")
        if product_name:
            meta_parts.append(f"상품: {product_name}")
        if policy_type:
            meta_parts.append(f"약관종류: {policy_type}")
        if effective_date:
            meta_parts.append(f"시행일: {effective_date}")
        if version:
            meta_parts.append(f"버전: {version}")
        if coverage_type:
            meta_parts.append(f"보장유형: {coverage_type}")
        if page:
            meta_parts.append(f"페이지: {page}")
            
        meta_str = ", ".join(meta_parts)
        if meta_str:
            meta_str = f"[{meta_str}]"
        
        # 문서 내용과 메타데이터 결합
        formatted_doc = f"\n문서 {i+1} {meta_str}\n{doc.page_content}\n"
        formatted_docs.append(formatted_doc)
    
    return "\n".join(formatted_docs)

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
    
    # OpenAI 임베딩 사용
    embeddings = OpenAIEmbeddings()
    logger.info("OpenAI 임베딩 초기화 완료")
    
    try:
        vectordb = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=embeddings
        )
        logger.info("Pinecone 벡터스토어 연결 성공")
        
        # 검색 시 메타데이터 반환 설정
        retriever = vectordb.as_retriever(
            search_kwargs={
                "k": 6,
                "fetch_k": 10  # 더 많은 후보를 검색하여 다양한 메타데이터 확보
            }
        )
        logger.info("Retriever 생성 완료 (메타데이터 반환 활성화)")

        # 더 정확한 답변을 위해 향상된 모델 사용
        llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            temperature=0
        )
        logger.info("ChatOpenAI 모델 초기화 완료")
        
        # 메모리 초기화
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 프롬프트 템플릿 설정
        qa_prompt = PromptTemplate(
            template=QA_PROMPT_WITH_METADATA,
            input_variables=["context", "question"]
        )
        
        # QA 체인 생성
        qa_chain = load_qa_chain(
            llm=llm,
            chain_type="stuff",
            prompt=qa_prompt,
            verbose=True
        )
        
        # 최종 체인 생성
        chain = ConversationalRetrievalChain(
            retriever=retriever,
            combine_docs_chain=qa_chain,
            question_generator=llm,
            memory=memory,
            get_chat_history=lambda h: h,
            return_source_documents=True,  # 출처 문서 반환
            return_generated_question=True  # 생성된 질문도 반환
        )
        
        logger.info("메타데이터 활용 대화형 체인 생성 완료")
        
        return chain
    except Exception as e:
        logger.error(f"체인 생성 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise 