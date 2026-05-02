import json
import requests
import os

SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")


# --- 定义谷歌搜索工具 ---
def search_google(query):
    # 1. 准备要去的地方 (URL)
    url = "https://google.serper.dev/search"
    
    # 2. 准备要带的数据 (Payload)
    payload = json.dumps({
        "q": query,
        "gl": "cn",
        "hl": "zh-cn"
    })
    
    # 3. 准备身份证明 (Headers)
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    # 4. 发送请求
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        # 5. 处理结果
        if response.status_code == 200:
            data = response.json()
            # 只取前 3 条结果
            organic = data.get("organic", [])[:3]
            
            # 如果没搜到
            if not organic: 
                return "未找到结果。"
            
            # 把结果拼成字符串
            results = []
            for item in organic:
                title = item.get("title", "无标题")
                snippet = item.get("snippet", "无摘要")
                results.append(f"标题：{title}\n内容：{snippet}\n")
            
            return "\n".join(results)
        else:
            return f"Error: {response.text}"
            
    except Exception as e:
        return f"Error: {e}"
"function": {
    "name": "search_google",
    "description": "搜索",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词"
            }
        },
        "required": ["query"]
    }
}