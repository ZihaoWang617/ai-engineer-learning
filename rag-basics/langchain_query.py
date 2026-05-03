
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import cohere
import os

load_dotenv()

embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
llm = ChatOpenAI(model = "gpt-4o-mini", temperature = 0.2)
vectorstore = Chroma(
    collection_name= "immigration_lc",
    embedding_function = embeddings,
    persist_directory = "./chroma_db_lc"
)

retriever = vectorstore.as_retriever(search_kwargs={"k":3})
stored = vectorstore.get(include = ["documents", "metadatas"])
docs_for_bm25 = [
    Document(page_content = text, metadata = meta)
    for text, meta in zip(stored["documents"], stored["metadatas"])
]
bm25_retriever = BM25Retriever.from_documents(docs_for_bm25)
bm25_retriever.k = 3

prompt = PromptTemplate(
    input_variables = ["context", "question", "chat_history"],
    template = """你是移民顾问，只根据提供的内容回答，不要编造。  
如果内容里没有答案，说'我没有相关信息'。
    chat history: {chat_history}
    
    Context: {context}

    Question: {question}

    Answer: """
)

def format_docs(docs):
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        chunk_index = doc.metadata.get("chunk_index", "?")
        parts.append(f"[来源：{source}, 第{chunk_index}块]\n{doc.page_content}")
    return "\n\n".join(parts)

chain = (
    {"context": lambda x: format_docs(hybrid_retriever(x["question"], k=3)),
     "question": lambda x: x["question"],
     "chat_history": lambda x: x["chat_history"],}
    | prompt
    | llm
    | StrOutputParser()
)

def ask(question: str, chat_history: list = []) -> dict[str, str | list[str]]:
    try:
        parts = [f"User: {user}\n AI: {ai}" for user, ai in chat_history]
        history_str = "\n".join(parts)
        docs = rerank_docs(question, hybrid_retriever(question, k=6), top_n=3)
        context = format_docs(docs)
        result = prompt | llm | StrOutputParser()
        answer = result.invoke({
            "context": context,
            "question": question,
            "chat_history": history_str
        })
        source_info = [f"{doc.metadata.get('source','unknown')} 第{doc.metadata.get('chunk_index','?')}块"
                       for doc in docs
        ]
        return {"answer": answer, "sources": source_info}
    except Exception as e:
        raise Exception(f"Error during question answering: {str(e)}")

def hybrid_retriever(question: str, k: int) -> list:
    semantic_docs = retriever.invoke(question)
    bm25_docs = bm25_retriever.invoke(question)
    seen = set()
    combined = []
    for doc in semantic_docs + bm25_docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            combined.append(doc)
    return combined[:k]

def rerank_docs(question: str, docs: list, top_n: int =3) -> list:
    co = cohere.ClientV2(api_key = os.getenv("COHERE_API_KEY"))

    texts = [doc.page_content for doc in docs]

    response = co.rerank(
        model = "rerank-v3.5",
        query = question,
        documents = texts,
        top_n = top_n
    )
    reranked = [docs[result.index] for result in response.results]
    return reranked

if __name__ == "__main__":
    print("欢迎使用移民咨询系统！输入 'q' 退出。")
    chat_history = []
    while True:
        user_question = input("请输入你的问题: ")
        if user_question.lower() =='q':
            print("Exiting the program.")
            exit(0)
        answer = ask(user_question, chat_history)
        print(answer)
        chat_history.append((user_question, answer["answer"]))



