from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import cohere
from pathlib import Path
import os

from langchain_pinecone import PineconeVectorStore

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)
INDEX_NAME = "jianuo-dev-v1"
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
)
retriever = vectorstore.as_retriever(search_kwargs={"k":3})

# BM25 从 knowledge_base.txt 重新切分,和 ingest 用同样的 chunking 参数
kb_loader = TextLoader("knowledge_base.txt")
kb_documents = kb_loader.load()
kb_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs_for_bm25 = kb_splitter.split_documents(kb_documents)
# 加 metadata(和 ingest 一致)
for i, chunk in enumerate(docs_for_bm25):
    chunk.metadata["source"] = "knowledge_base"
    chunk.metadata["chunk_index"] = i
bm25_retriever = BM25Retriever.from_documents(docs_for_bm25)
bm25_retriever.k = 3

prompt = ChatPromptTemplate.from_messages([
    ("system", """你是移民顾问，只根据提供的内容回答，不要编造。 如果内容里没有答案， 说‘我没有相关信息’。"""),
    MessagesPlaceholder(variable_name = "chat_history"),
    ("human", "Context: {context}\n\nQuestion: {question}")
]
)

def format_docs(docs):
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        chunk_index = doc.metadata.get("chunk_index", "?")
        parts.append(f"[来源：{source}, 第{chunk_index}块]\n{doc.page_content}")
    return "\n\n".join(parts)

rag_chain = prompt | llm | StrOutputParser()

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key= "question",
    history_messages_key= "chat_history"
)

def ask(question: str, session_id: str = "default") -> dict:
    try:
        docs = rerank_docs(question, hybrid_retriever(question, k=6), top_n=3)
        context = format_docs(docs)
        source_info = [
            f"{doc.metadata.get('source', 'unknown')} 第{doc.metadata.get('chunk_index', '?')}块"
            for doc in docs
        ]
        answer = conversational_chain.invoke({
            "context": context,
            "question": question
        },
            config = {
                "configurable": {
                    "session_id": session_id
                }
            })
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
    texts = [doc.page_content for doc in docs]

    response = co.rerank(
        model = "rerank-v3.5",
        query = question,
        documents = texts,
        top_n = top_n
    )
    reranked = [docs[result.index] for result in response.results]
    return reranked

def retrieve_kb_context(question: str) -> str:
    """
    Use to search the Canadian immigration policy knowledge base, which contains information about visa programs (Express Entry, BC PNP, CEC), eligibility criteria, application requirements, and policy updates.
    Use this tool when:
    - user asks about specific immigration programs, eligibility requirements, document checklists, or policy details
    
    Do NOT use this tool for:
    - Math calculations (use `calculate` instead)
    - Processing time queries (use `check_processing_time` instead)  
    - Eligibility scoring (use `validate_eligibility` instead)
    - Conversational small talk or greetings

    Args:
        question: A self-contained query string. Pronouns and references 
            must be resolved using prior conversation context before 
            calling this tool.
            
            Good: "What are the streams of BC PNP?"
            Bad:  "What are its streams?"  (pronoun "its" not resolved)

    Returns:
        Retrieved context chunks from the knowledge base, formatted with inline source citations.
    """
    try:
        docs = rerank_docs(question, hybrid_retriever(question, k=6), top_n=3)
        context = format_docs(docs)
        return f"Retrieved context from knowledge base:\n\n{context}"
    except (ConnectionError, TimeoutError):
        return ("知识库检索暂时不可用（网络连接问题）。"
            "请告诉用户该问题可能是临时的，建议稍后重试。")
    except Exception as e:
        print(f"[ERROR] retrieve_kb_context: {type(e).__name__}: {e}")
        return ("知识库检索遇到未知问题，请告诉用户系统暂时不可用，"
            "建议稍后重试或联系支持团队。")
if __name__ == "__main__":
    print("欢迎使用移民咨询系统！输入 'q' 退出。")
    while True:
        user_question = input("请输入你的问题: ")
        if user_question.lower() =='q':
            print("Exiting the program.")
            exit(0)
        answer = ask(user_question, session_id = "default")
        print(answer)


