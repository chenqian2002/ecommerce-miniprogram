import json
import os
from duckduckgo_search import DDGS
from openai import OpenAI
from dotenv import load_dotenv

proxy_url = "http://127.0.0.1:10809" 

os.environ["http_proxy"] = proxy_url
os.environ["https_proxy"] = proxy_url
print(f"🌍 已配置网络代理：{proxy_url}")
# 👆👆👆 代理配置结束 👆👆👆

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def search_web(query):
    print(f"Searching for: {query}")
    try:
        #搜索最多返回2条结果
        results = DDGS().text(query,max_results=2)
        #将结果转换为JSON格式，确保中文不乱码
        return json.dumps(results,ensure_ascii=False)
    except Exception as e: 
        return f"Error searching: {str(e)}"
#告诉ai有什么工具 这是json格式
tool_schema = [
    {
        "type": "function",
        "function": {
            "name":"search_web",
            "description":"搜索网络信息",
            "parameters":{
                "type":"object",
                "properties":{
                    "query": {"type": "string", "description": "搜索用的关键词"}
                },
                "required": ["query"]
            }
        }
    }
]

# --- 1. 设置问题 ---
user_question ="比特币今天多少钱"
print(f"🙋‍♂️ 用户提问：{user_question}")
messages=[
    {"role":"system","content":"你是一个专业的网络信息搜索助手，如果需要实时信息请你搜索网络"},
    {"role":"user","content":user_question}
]
# --- 2. 第一次问 AI ---
response=client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tool_schema,
    tool_choice="auto"

)

msg =response.choices[0].message

# --- 3. 检查 AI 是否想用工具 ---
# ... (前面的代码都不用动) ...

# --- 3. 检查 AI 是否想用工具 ---
if msg.tool_calls:
    print("🤖 AI 决定要搜索！")
    
    # 获取 AI 想要的搜索词
    tool_call = msg.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    query = args["query"]
    
    # 执行搜索
    search_result = search_web(query)
    
    # 💡 新增：打印一下到底搜到了什么？这样你就知道 AI 看到了什么
    print(f"🔍 搜到的内容摘要: {search_result[:100]}......") 
    
    # --- 4. 把搜索结果返回给 AI ---
    messages.append(msg)  # 必须带上 AI 之前的提问
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": search_result
    })
    
    print("⏳ 正在根据搜索结果组织语言...")

    # --- 5. 再次问 AI ---
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    
    print("\n🎉 AI 最终回答：")
    print(final_response.choices[0].message.content)

else:
    # 👇 这里是你之前乱掉的地方，要注意缩进！
    print("🤖 AI 觉得不用搜索，直接回答：")
    print(msg.content)