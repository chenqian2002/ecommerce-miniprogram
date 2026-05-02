import os
from dotenv import load_dotenv

from openai import OpenAI
from test_deepseek import response

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
def chat_once(user_input:str)->str:
    response=client.chat.completion.create(
          model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个友善的小助手，用繁体中文回答。"},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].messages.content

if __name__ == "__main__":
    print("小白")
    while True:
        user_input=input("你")
        if user_input in ["推出","extic"]:
            break
        reply = chat_once(user_input)
        print("AI:", reply)