# app/routes/utils/rag_chain.py
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
你是個專業的課程顧問，會根據學生的需求從課程描述中推薦最適合的課。請使用 **標準 Markdown 語法與縮排** 回覆，勿在清單項目前後使用多餘縮排或空行，因為之後會再被渲染。
以下是學生的需求：
{question}

以下是可能的課程資訊：
{context}

請根據上述資訊推薦最適合的5門課，說明原因，並提供課名、時間與流水號。
"""
prompt = PromptTemplate.from_template(template)
llm = ChatOpenAI(model=OPENAI_MODEL, api_key=SecretStr(OPENAI_API_KEY), temperature=0.3)

qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True, chain_type_kwargs={"prompt": prompt})


def clean_markdown(text: str) -> str:
    # import re

    # # 1. 多空格變兩格
    # text = re.sub(r"[ ]{3,}", "  ", text)

    # # 2. 多重換行變一行
    text = re.sub(r"\n\s*\n+", "\n", text)

    # # 3. 去除 list 前的空白
    # text = re.sub(r"\n[ ]+(?=- )", "\n- ", text)

    # # 4. 合併被分成多行的 list item 描述（關鍵！）
    # # 意即：list 後面跟著的下一行不是新的 list，就直接合併
    # text = re.sub(r"(- [^\n]+)\n(?!- )", r"\1 ", text)

    # # 5. 修正連續多個 list item 沒換行分開的情況（optional）
    # # text = re.sub(r"(?<=\n- .+?)\n(?=- )", "\n\n", text)

    return text.strip()


def recommend_course(question, schedule):
    # Step 1：初步相似度檢索
    raw_docs = vectordb.similarity_search(question, k=15)

    # Step 2：過濾符合「課程時間 ⊆ 使用者 schedule」的課
    filtered_docs = []
    user_set = set(schedule)

    for doc in raw_docs:
        time_slots_str = doc.metadata.get("time_slots", "")
        course_slots = time_slots_str.split(",") if time_slots_str else []
        if set(course_slots).issubset(user_set):
            filtered_docs.append(doc)

    # Step 3：如果沒有符合的課程
    if not filtered_docs:
        return "找不到符合您時段的課程，請嘗試調整時間或提問內容。"

    # Step 4：傳入 QA chain，但改成用 filtered_docs 當 context
    context = "\n\n".join(doc.page_content for doc in filtered_docs[:5])
    filled_prompt = prompt.format(question=question, context=context)
    result = llm.invoke(filled_prompt)

    # Step 5：標準化 markdown，移除清單前多餘空白（最多三格）
    print("🧪 result.content (initial):", repr(result.content))
    cleaned = clean_markdown(result.content)
    print()
    print("🧪 result.content (cleaned):", repr(cleaned))
    return cleaned
