# app/utils/rag_chain.py
import os
import re
import markdown
from app.utils.blob_loader import download_and_extract_chroma_data
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 環境設定
BLOB_CONNECTION_STRING = os.environ["AZURE_BLOB_CONNECTION_STRING"]
BLOB_CONTAINER_NAME = os.environ["AZURE_BLOB_CONTAINER"]
BLOB_FILE_NAME = os.environ["BLOB_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

CHROMA_LOCAL_DIR = "persist"

# 全域變數
vectordb = None
qa_chain = None

# Prompt 模板
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
    print("🔄 初始化向量資料庫...", flush=True)

    global vectordb, qa_chain

    if vectordb is not None:
        return

    if not os.path.exists(CHROMA_LOCAL_DIR):
        download_and_extract_chroma_data(container_name=BLOB_CONTAINER_NAME, blob_name=BLOB_FILE_NAME, download_dir=CHROMA_LOCAL_DIR, connection_string=BLOB_CONNECTION_STRING)

    embedding = OpenAIEmbeddings(api_key=SecretStr(OPENAI_API_KEY))
    vectordb = Chroma(persist_directory=CHROMA_LOCAL_DIR, embedding_function=embedding)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    # Debug 向量筆數
    try:
        print("📊 向量資料筆數：", len(vectordb.get()["documents"]))
        print("✅ 向量資料庫初始化完成！")
    except Exception as e:
        print("❌ 向量讀取失敗：", e)

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=SecretStr(OPENAI_API_KEY), temperature=0.3)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True, chain_type_kwargs={"prompt": prompt})


def clean_markdown(text: str) -> str:
    # text = re.sub(r"\n\s*\n+", "\n", text)
    # text = re.sub(r"\n[ ]+(?=- )", "\n- ", text)
    # text = re.sub(r"(- [^\n]+)\n(?!- )", r"\1 ", text)
    return text.strip()


def recommend_course(question, schedule):
    if vectordb is None or qa_chain is None:
        raise RuntimeError("請先呼叫 initialize_vectordb() 初始化向量資料庫。")

    print("✅ 使用者問題：", question)
    print("✅ 使用者時段（schedule）:", schedule)

    # 初步檢索
    raw_docs = vectordb.similarity_search(question, k=15)
    print(f"🔍 初步相似課程數量：{len(raw_docs)}")

    user_set = set(schedule)
    filtered_docs = []

    for i, doc in enumerate(raw_docs):
        metadata = doc.metadata
        print(f"\n📘 課程 {i+1} metadata:", metadata)

        course_slots = metadata.get("time_slots", "").split(",") if metadata.get("time_slots") else []
        print("🕒 課程時段：", course_slots)
        print("📋 是否符合使用者時段？", set(course_slots).issubset(user_set))

        if set(course_slots).issubset(user_set):
            filtered_docs.append(doc)

    print(f"\n✅ 通過時段過濾的課程數量：{len(filtered_docs)}")

    if not filtered_docs:
        return "找不到符合您時段的課程，請嘗試調整時間或提問內容。"

    context = "\n\n".join(doc.page_content for doc in filtered_docs[:5])
    filled_prompt = prompt.format(question=question, context=context)

    result = qa_chain.invoke(filled_prompt)
    raw_output = result.get("result", "")
    cleaned = clean_markdown(raw_output)

    print("🧪 result.content (initial):", repr(raw_output))
    print("🧪 result.content (cleaned):", repr(cleaned))

    return cleaned
