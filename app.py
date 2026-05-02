"""
app.py
本檔案由 AI 自動建立，你可以在這裡撰寫主程式邏輯。
"""


def main():
    print("Hello from app.py！")


if __name__ == "__main__":
    main()

from flask import Flask, request, render_template_string, redirect
from datetime import datetime, timedelta
import threading
import threading
import datetime # 引入时间模块
app = Flask(__name__)

@app.route("/")
def home():
    
    now = datetime.datetime.now()
    return f"<h1>现在的时间是：{now}</h1>" # 把时间显示在网页上
@app.route("/about")
def about():
    return "这里是关于我的页面..."

if __name__ == "__main__":
    app.run(debug=True)