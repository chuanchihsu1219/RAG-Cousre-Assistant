# app/utils/rag_chain.py
import os
import json
from typing import List
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 讀取環境變數
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# 確保 OPENAI_API_KEY 和 OPENAI_MODEL 已正確設置
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY 未設置，請檢查環境變數。")

if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL 未設置，請檢查環境變數。")

# 將 OPENAI_API_KEY 包裝為 SecretStr
api_key_secret = SecretStr(OPENAI_API_KEY)

# 初始化 embedding 模型與向量庫
embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Prompt 設定
template = """
你是個專業的課程顧問，會根據學生的需求從課程描述中推薦最適合的課。
以下是學生的需求：
{question}

以下是可能的課程資訊：
{context}

請根據上述資訊推薦最適合的課，說明原因，並提供課名、時間與流水號。
"""
prompt = PromptTemplate.from_template(template)

# 修正 ChatOpenAI 的初始化方式
llm = ChatOpenAI(model="gpt-4o", api_key=api_key_secret, temperature=0.3)


# 建立函式（依 schedule 限制檢索課程）
def recommend_course(question: str, user_slots: List[str]) -> str:
    vectordb = Chroma(persist_directory="./persist/chroma_data", embedding_function=embedding)

    # 加入 schedule metadata filter
    retriever = vectordb.as_retriever(search_kwargs={"k": 5, "filter": {"schedule_slots": {"$in": user_slots}}})

    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True, chain_type_kwargs={"prompt": prompt})

    return qa_chain.run(question)
