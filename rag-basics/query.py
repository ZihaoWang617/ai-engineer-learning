import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key = api_key)
chroma_client = chromadb.PersistentClient(path = "./chroma_db")
collection = chroma_client.get_collection("immigration")

while True: 
    question = input("Enter your question: (or 'q' to quit) ")
    if question.lower() =='q':
        print("Exiting the program.")
        break
    embedding_response = openai_client.embeddings.create(
        input = question,
        model = "text-embedding-3-small"
    )
    question_vector = embedding_response.data[0].embedding
    results = collection.query(
        query_embeddings = [question_vector],
        n_results =3
    )
    context = "\n\n".join(results["documents"][0])
    messages = [
        {"role": "system", "content": "你是移民顾问，只根据提供的内容回答，不要编造。如果内容里没有答案，说'我没有相关信息'。"},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
    ]
    response = openai_client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages,
        temperature = 0.2
    )
    print("Answer: ", response.choices[0].message.content)

