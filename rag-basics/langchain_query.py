from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
llm = ChatOpenAI(model = "gpt-4o-mini", temperature = 0.2)
vectorstore = Chroma(
    collection_name= "immigration_lc",
    embedding_function = embeddings,
    persist_directory = "./chroma_db_lc"
)

retriever = vectorstore.as_retriever(search_kwargs={"k":3})
prompt = PromptTemplate(
    input_variables = ["context", "question"],
    template = """你是移民顾问，只根据提供的内容回答，不要编造。
每个内容块开头都有来源标注，格式为[来源：xxx, 第n块]。回答时先给出答案，然后在句子末尾加上来源标注。
如果内容里没有答案，说'我没有相关信息'。
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
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def ask(question: str) -> str:
    try:
        result = chain.invoke(question)
        return result
    except Exception as e:
        raise Exception(f"Error during question answering: {str(e)}")

if __name__ == "__main__":
    print("欢迎使用移民咨询系统！输入 'q' 退出。")
    while True:
        user_question = input("请输入你的问题: ")
        if user_question.lower() =='q':
            print("Exiting the program.")
            exit(0)
        print(ask(user_question))



