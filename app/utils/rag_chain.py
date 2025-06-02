import os
from app.utils.blob_loader import download_and_extract_chroma_data
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 設定
BLOB_CONNECTION_STRING = os.environ["AZURE_BLOB_CONNECTION_STRING"]
BLOB_CONTAINER_NAME = "your-container-name"
BLOB_FILE_NAME = "course_vector.zip"
CHROMA_LOCAL_DIR = "./persist/chroma_data"

# 下載並解壓
# download_and_extract_chroma_data(container_name=BLOB_CONTAINER_NAME, blob_name=BLOB_FILE_NAME, download_dir=CHROMA_LOCAL_DIR, connection_string=BLOB_CONNECTION_STRING)

# 初始化
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
vectordb = Chroma(persist_directory=CHROMA_LOCAL_DIR, embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# Prompt
template = """
你是個專業的課程顧問，會根據學生的需求從課程描述中推薦最適合的課。
以下是學生的需求：
{question}

以下是可能的課程資訊：
{context}

請根據上述資訊推薦最適合的課，說明原因，並提供課名、時間與流水號。
"""
prompt = PromptTemplate.from_template(template)
llm = ChatOpenAI(model=OPENAI_MODEL, api_key=SecretStr(OPENAI_API_KEY), temperature=0.3)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True, chain_type_kwargs={"prompt": prompt})


def recommend_course(question: str) -> str:
    return qa_chain.run(question)
