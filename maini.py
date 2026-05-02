import json
import os
from duckduckgo_search import DDGS
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. 配置代理 (保持你原来的设置) ---
proxy_url = "http://127.0.0.1:10809" 
os.environ["http_proxy"] = proxy_url
os.environ["https_proxy"] = proxy_url
print(f"🌍 已配置网络代理：{proxy_url}")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("Qwen_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/api/v1"
)
# deepseek:"https://api.deepseek.com"
#qwen:"https://dashscope.aliyuncs.com/api/v1"
# --- 2. 定义搜索工具 ---
def search_web(query):
    print(f"\n🔍 (正在帮您搜：{query}...)")
    try:
        ddgs = DDGS(proxy=proxy_url, timeout=20)
        results = ddgs.text(query, max_results=5)
        if not results: return "未找到结果"
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return f"搜索报错: {str(e)}"

tool_schema = [{
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "搜索互联网实时信息",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]

# --- 3. 初始化聊天历史 ---
history = [
    {"role": "system", "content": "你是一个乐于助人的AI助手，遇到不懂的实时问题会主动搜索。"}
]

print("==========================================")
print("🤖 AI 联网助手已启动！(输入 'exit' 退出)")
print("==========================================")

# --- 4. 聊天主循环 ---
while True:
    # 1. 获取输入
    user_input = input("\n👉 你: ")
    
    # 如果输入为空，重新输入
    if user_input.strip() == "": continue
    # 退出指令
    if user_input.strip().lower() in ["exit", "quit", "退出"]:
        print("👋 再见！")
        break

    # 2. 存入历史
    history.append({"role": "user", "content": user_input})

    # 3. 呼叫 AI
    print("⏳ AI 思考中...")
    
    try:
        # 👇👇👇 注意：从这里开始都在 while 循环里面 👇👇👇
        response = client.chat.completions.create(
            model="qwen3-max",
            messages=history,
            tools=tool_schema,
        )
        
        msg = response.choices[0].message

        # 4. 判断是否要搜
        if msg.tool_calls:
            print("🤖 AI 决定要搜索！")
            tool_call = msg.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            
            # 执行搜索
            search_result = search_web(args["query"])
            print(f"✅ 搜到了: {search_result[:50]}...") # 只打印前50个字
            
            # 把中间过程存入历史 (很重要！否则AI会报错)
            history.append(msg)
            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": search_result
            })
            
            # 再次呼叫 AI 总结
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=history
            )
            msg = response.choices[0].message

        # 5. 输出回答
        print(f"🤖 AI: {msg.content}")

        # 6. 把 AI 的回答存入历史 (这样它才有记忆)
        history.append(msg)
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")