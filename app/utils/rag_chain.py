# app/utils/rag_chain.py
import os
import re
from app.utils.blob_loader import download_and_extract_chroma_data
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr
import markdown

# 設定
BLOB_CONNECTION_STRING = os.environ["AZURE_BLOB_CONNECTION_STRING"]
BLOB_CONTAINER_NAME = os.environ["AZURE_BLOB_CONTAINER"]
BLOB_FILE_NAME = os.environ["BLOB_NAME"]
CHROMA_LOCAL_DIR = "./persist/chroma_data"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# 全域變數（延遲初始化）
vectordb = None
qa_chain = None
prompt = PromptTemplate.from_template(
    """
你是個專業的課程顧問，會根據學生的需求從課程描述中推薦最適合的課。請使用 **標準 Markdown 語法與縮排** 回覆，勿在清單項目前後使用多餘縮排或空行，因為之後會再被渲染。
以下是學生的需求：
{question}

以下是可能的課程資訊：
{context}

請根據上述資訊推薦最適合的5門課，說明原因，並提供課名、時間與流水號。
"""
)


def initialize_vectordb():
    global vectordb, qa_chain

    if vectordb is not None:
        return  # 已初始化過就跳過

    # 若向量資料尚未下載與解壓，先處理
    if not os.path.exists(CHROMA_LOCAL_DIR):
        download_and_extract_chroma_data(container_name=BLOB_CONTAINER_NAME, blob_name=BLOB_FILE_NAME, download_dir=CHROMA_LOCAL_DIR, connection_string=BLOB_CONNECTION_STRING)

    embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=CHROMA_LOCAL_DIR, embedding_function=embedding)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=SecretStr(OPENAI_API_KEY), temperature=0.3)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True, chain_type_kwargs={"prompt": prompt})


def clean_markdown(text: str) -> str:
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = re.sub(r"\n[ ]+(?=- )", "\n- ", text)
    text = re.sub(r"(- [^\n]+)\n(?!- )", r"\1 ", text)
    return text.strip()


def recommend_course(question, schedule):
    if vectordb is None or qa_chain is None:
        raise RuntimeError("請先呼叫 initialize_vectordb() 初始化向量資料庫。")

    raw_docs = vectordb.similarity_search(question, k=15)
    user_set = set(schedule)

    filtered_docs = []
    for doc in raw_docs:
        time_slots_str = doc.metadata.get("time_slots", "")
        course_slots = time_slots_str.split(",") if time_slots_str else []
        if set(course_slots).issubset(user_set):
            filtered_docs.append(doc)

    if not filtered_docs:
        return "找不到符合您時段的課程，請嘗試調整時間或提問內容。"

    context = "\n\n".join(doc.page_content for doc in filtered_docs[:5])
    filled_prompt = prompt.format(question=question, context=context)

    result = qa_chain.llm.invoke(filled_prompt)
    cleaned = clean_markdown(result.content)

    print("🧪 result.content (initial):", repr(result.content))
    print("🧪 result.content (cleaned):", repr(cleaned))
    return cleaned
