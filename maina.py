import json
import os
import requests  # 👈 这次我们用最稳的请求库
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# ================= 配置区 (请修改这里) =================

# 1. 你的 Serper API Key (刚才网站上复制的)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# 2. 你的代理端口 (v2rayN一般是10809, Clash是7890)
PROXY_PORT = "10809"

# ====================================================

# 配置网络环境
os.environ["http_proxy"] = f"http://127.0.0.1:{PROXY_PORT}"
os.environ["https_proxy"] = f"http://127.0.0.1:{PROXY_PORT}"
print(f"🌍 网络代理已配置: 127.0.0.1:{PROXY_PORT}")



client = OpenAI(
    api_key=os.getenv("Qwen_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# --- 定义谷歌搜索工具 (Serper版) ---
def search_google(query):
    print(f"\n🔍 (正在调用 Google 搜索：{query}...)")
    
    url = "https://google.serper.dev/search"
    #json.dumps将python转换为json格式以便发送请求
    payload = json.dumps({
        #搜索地区（geo location），query = 搜索关键词，搜索语言（host language），
        # gl = 搜索地区，hl = 语言
        "q": query,
        "gl": "cn",   # 搜索地区：中国 (你可以改成 "us" 搜美国)
        "hl": "zh-cn" # 语言：简体中文
    })
    #headers = HTTP 请求头
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        #告诉服务器：我发送的数据是 JSON 格式
        'Content-Type': 'application/json'
    }

    try:
        # 发送请求 (这里的 verify=False 是为了避免SSL报错，proxies会自动走环境变量)
        # requests.post() 是 Python 用来：
        #👉 向网站发送 POST 请求 的函数
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        # 解析结果
        #response.status_code 是 HTTP 响应状态码，200 表示成功 
        if response.status_code == 200:
            #response.json() 将响应内容转换为 Python 字典
            data = response.json()
            #organic = 有机搜索结果
            # 提取前 3 条有机搜索结果
            organic_results = data.get("organic", [])[:3]
            
            if not organic_results:
                return "Google 未返回相关结果。"
                
            # 把结果整理成好看的文本
            results_text = []
            for item in organic_results:
                title = item.get("title", "无标题")
                snippet = item.get("snippet", "无摘要")
                link = item.get("link", "")
                results_text.append(f"【标题】{title}\n【摘要】{snippet}\n【链接】{link}\n")
            
            return "\n".join(results_text)
        else:
            return f"Serper API 报错: {response.text}"
            
    except Exception as e:
        return f"搜索请求失败: {str(e)}"

# --- 工具说明书 ---
tool_schema = [{
    "type": "function",
    "function": {
        "name": "search_google",
        "description": "使用 Google 搜索互联网实时信息（天气、股价、新闻等）",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]

# --- 聊天历史 ---
history = [
    {"role": "system", "content": "你是一个AI助手。请利用 search_google 工具获取实时信息来回答用户。"}
]

print("==========================================")
print("🤖 Google 联网助手已启动！(输入 'exit' 退出)")
print("==========================================")

# --- 主循环 ---
while True:
    try:
        user_input = input("\n👉 你: ")
    except KeyboardInterrupt:
        break
        
    if not user_input.strip(): continue
    if user_input.strip().lower() in ["exit", "quit", "退出"]:
        print("👋 再见！")
        break

    history.append({"role": "user", "content": user_input})
    print("⏳ AI 思考中...")

    try:
        # 第一次呼叫
        response = client.chat.completions.create(
            model="qwen3-max",
            messages=history,
            tools=tool_schema,
        )
        msg = response.choices[0].message

        # 判断是否要搜
        if msg.tool_calls:
            print("🤖 AI 决定搜索...")
            tool_call = msg.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            
            # 执行谷歌搜索
            search_result = search_google(args["query"])
            
            print(f"✅ 搜索成功！(内容长度: {len(search_result)} 字符)")
            #print(search_result) # 如果你想看具体搜到了什么，把这行注释解开
            
            # 把结果给 AI
            history.append(msg)
            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": search_result
            })
            
            # 第二次呼叫 (总结)
            print("⏳ 正在整理答案...")
            response = client.chat.completions.create(
                model="qwen3-max",
                messages=history
            )
            msg = response.choices[0].message

        print(f"🤖 AI: {msg.content}")
        history.append(msg)

    except Exception as e:
        print(f"❌ 发生错误: {e}")