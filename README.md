# RAG-Based NTU Course Assistant

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://rag-course-ai.zeabur.app/)

A full-stack educational assistant system based on **Retrieval-Augmented Generation (RAG)** architecture, designed to provide intelligent, personalized course recommendations for National Taiwan University (NTU) students. This project demonstrates practical integration of LLM-based semantic search, Azure cloud storage, and full-stack web development.

---

## 🎯 Project Objectives

- Solve the complexity of course discovery and selection using natural language.
- Build a scalable **RAG system** using **LangChain + Chroma VectorDB + OpenAI embeddings**.
- Integrate with **Azure Blob Storage** and **Supabase** for scalable cloud-native deployment.
- Enable **filtering based on time slots** and potential future enhancements like clustering similar courses.

---

## 🧠 Tech Stack

| Layer            | Technology                     |
|------------------|---------------------------------|
| Frontend         | HTML, Bootstrap, markdown-it   |
| Backend          | Flask, Python                   |
| Vector Search    | Chroma (HNSW index)             |
| Embedding Model  | OpenAI `text-embedding-ada-002` |
| Cloud Storage    | Azure Blob Storage              |
| User Data Store  | Supabase                        |
| LLM              | OpenAI GPT-4o via API           |
| Deployment       | Zeabur with Docker image        |

---

## 🌟 Key Features

- **RAG-based Recommendation Engine**: Combines semantic retrieval with generative answers.
- **Markdown Rendering**: Supports user-friendly output via markdown-it in-browser rendering.
- **Time Slot Filtering**: Matches course recommendations with user-defined time constraints.
- **User Query Logging**: Logs interaction history in Supabase (auth + database).
- **Azure Cloud Integration**: Embeddings and vector store persist on Azure Blob for scalable access.

---

## 🧭 Real-World Relevance to Microsoft TAI

| TAI Focus Area             | This Project Delivers                                   |
|----------------------------|----------------------------------------------------------|
| Azure Integration          | Azure Blob used for cloud embedding storage             |
| AI Deployment              | End-to-end RAG pipeline using OpenAI & vector search    |
| Cloud-First Architecture   | Blob loading, Supabase, and Zeabur cloud deployment     |
| Real Use Case Focus        | Used real NTU course data & built for students' needs   |

---

## 🧑‍🏫 Acknowledgement

- This project was inspired by [Benson Chiu](https://github.com/imbensonchiu)'s teachings at the NTU Data Analytics Club, where he shared the vital foundation and real-world applications of RAG.
- Special thanks to ChatGPT, which provided extensive assistance in project design, debugging, and discussion throughout development.

---

## 🔭 Future Enhancements

- Add semantic deduplication to exclude already taken or highly similar courses.
- Integrate course metadata filtering with student preference models.
- Further optimize the UI design, improving accessibility and responsiveness.
- Incorporate career-driven data such as skill tags or career cluster metadata to help students align course choices with long-term goals.
- Introduce course reputation scoring based on aggregated web reviews and NTU course feedback forums.

---

## 🚀 Demo & Deployment

Hosted on [Zeabur](https://rag-course-ai.zeabur.app/), the app fetches vector data from Azure Blob at runtime, initializes Chroma for vector search, and uses Flask for serving user interactions.
Welcome to sign up and try!

---

## 📂 Repository Structure

```bash
├── app/
│   ├── routes/        # Flask route controllers
│   ├── utils/         # RAG chain & blob loader logic
│   └── templates/     # HTML & Markdown rendering
├── persist/           # Local chroma index fallback
├── requirements.txt   # Python dependency definitions
└── main.py             # App entrypoint
```

---

## 💬 Contact

For any feedback, feel free to reach me.
