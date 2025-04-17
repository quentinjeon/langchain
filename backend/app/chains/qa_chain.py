from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
import os

def build_chain():
    # 구 버전의 OpenAI 임베딩 사용
    embeddings = OpenAIEmbeddings()
    
    vectordb = Pinecone.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=embeddings
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(
        model_name="gpt-4o-mini", 
        temperature=0
    )
    return ConversationalRetrievalChain.from_llm(llm, retriever) 