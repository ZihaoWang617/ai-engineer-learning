import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OpenAI_API_KEY")

client = OpenAI(api_key = api_key)
messages = [{"role": "system", "content": "You are an immigration assistant in Canada. You will help users with their immigration questions about BCPNP and Express Entry. Respond in Chinese and within 5 sentences. Just answer the question clearly and concisely and like human. for the uncertain information, just say: 建议咨询持牌顾问确认"},]
while True:
    question = input("请问您有什么移民方面的问题吗？（输入 'q' 退出程序）")
    if question.lower() == 'q':
        print("退出程序。")
        break
    try:
        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
        )
        ai_reply = response.choices[0].message.content
        print(ai_reply)
        messages.append({"role": "assistant", "content": ai_reply})
    except Exception as e:
        print(f"Error: {e}")
        break