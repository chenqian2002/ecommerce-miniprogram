import random
brain={
    "名字":["wo shi paython"],
    "你好":["你好"]
}
history=[]
print("现在是代码实验室")
while True:
    # 取得使用者輸入，並去掉前後空白
    user = input("你說: ").strip()
    
    # 把這句話存入記憶列表
    history.append(f"用戶說過: {user}")
    if user in brain:
        reply=random.choice(brain[user])
        print(f"機器人: {reply}")
 # 如果用戶說了 bye，就跳出迴圈
        if user == "bye":
            break
    else:
      # 如果不懂，就印出目前的記憶數量
        count = len(history)
        print(f"機器人: 我聽不懂... 但我已經記住你說的 {count} 句話了！")