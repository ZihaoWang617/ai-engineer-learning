import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key = api_key)
chroma_client = chromadb.PersistentClient(path = "./chroma_db")
collection = chroma_client.get_collection("immigration")
def ask(question: str) -> str:
        embedding_response = openai_client.embeddings.create(
            input = question,
            model = "text-embedding-3-small"
        )
        question_vector = embedding_response.data[0].embedding
        results = collection.query(
            query_embeddings = [question_vector],
            n_results = 3
        )
        context_parts = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_parts.append(f"[来源：{meta['source']}, 第{meta['chunk_index']}块]\n{doc}")
        context = "\n\n".join(context_parts)
        messages = [
            {"role": "system", "content": "你是移民顾问，只根据提供的内容回答，不要编造。回答时请标注资料来源。如果内容里没有答案，说'我没有相关信息'。"},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
        ]
        try:
            response = openai_client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            temperature = 0.2
        )
            print("Answer: ", response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error during question answering: {str(e)}")


if __name__ == "__main__":
    print("欢迎使用移民咨询系统！输入 'q' 退出。")
    while True:
        user_question = input("请输入你的问题: ")
        if user_question.lower() =='q':
            print("Exiting the program.")
            exit(0)
        ask(user_question)