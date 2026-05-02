import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. 引入相關型別
from typing import Annotated, TypedDict

# LangGraph 相關引入
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# 載入環境變數
load_dotenv()

# 2. 定義 State
class AgentState(TypedDict):
    # add_messages 會自動處理訊息的 append 邏輯
    messages: Annotated[list, add_messages]

# 初始化 DeepSeek 客戶端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def chat_node(state: AgentState):
    # 【修正點】 TypedDict 必須用 ["key"] 存取，不能用 .key
    messages_for_model = [
        {"role": "system", "content": "你是個友善的小助手，用繁體中文回覆。記住用戶告訴你的資訊，例如名字。"},
        *state["messages"]  # 這裡原本是 state.messages (錯誤)
    ]
    
    # 呼叫 DeepSeek 模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages_for_model,
        temperature=0.7,
        max_tokens=200
    )
    
    ai_reply = {
        "role": "assistant",
        "content": response.choices[0].message.content
    }
    
    # 回傳字典，LangGraph 會透過 add_messages 自動將其加入列表
    return {"messages": [ai_reply]}

# 建立流程圖
workflow = StateGraph(AgentState)

workflow.add_node("chat", chat_node)
workflow.set_entry_point("chat")
workflow.add_edge("chat", END)

# 設定記憶體 (Checkpointer)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 設定 Thread ID (這是記憶的關鍵，同一個 ID 會共享記憶)
config = {"configurable": {"thread_id": "qiang-chat-1"}}

print("\n=== 開始聊天！輸入 'exit' 或 '結束' 來結束 ===")
print("（試試告訴我你的名字，然後問我你叫什麼～）\n")

while True:
    try:
        user_input = input("你: ")
        if user_input.strip().lower() in ["exit", "結束", "quit", "q"]:
            print("聊天結束～拜拜！")
            break
        
        inputs = {"messages": [{"role": "user", "content": user_input}]}
        
        print("AI: ", end="", flush=True)
        
        # 執行 Graph
        # stream_mode="values" 會回傳每一步驟更新後的 State
        for event in app.stream(inputs, config, stream_mode="values"):
            # 取得最新的訊息
            last_msg = event["messages"][-1]
            
            # 只有當最新訊息是 AI 講的話才印出來
            # (第一次迴圈通常是 User 的輸入，所以要過濾掉)
            if last_msg["role"] == "assistant":
                print(last_msg["content"], end="", flush=True)
        
        print()  # 換行
        
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        break