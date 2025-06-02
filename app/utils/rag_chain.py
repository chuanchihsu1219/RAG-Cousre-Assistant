# app/utils/rag_chain.py
import os
import json
from langchain_community.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 初始化向量資料庫（假設本地 embedding 已存在 ./persist/chroma_data）
def load_retriever():
    vectorstore = Chroma(persist_directory="./persist/chroma_data", embedding_function=OpenAIEmbeddings())
    return vectorstore.as_retriever(search_kwargs={"k": 10})

def recommend_course(query: str):
    retriever = load_retriever()

    prompt = ChatPromptTemplate.from_template(                                            
    """
    課程訊息：
    {context}

    學生的問題：
    {question}

    你是個專業的學習規劃師，請根據學生的問題，從課程訊息中選出最適合的幾門課，並說明推薦原因。
    請提供課程名稱、流水號與上課時間。
    """)

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)

    def format_docs(docs):
        return "\\n\\n".join([doc.page_content for doc in docs])

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(query)
