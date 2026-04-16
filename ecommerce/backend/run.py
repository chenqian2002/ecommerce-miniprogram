# 后端启动脚本

import uvicorn
import os

if __name__ == "__main__":
    print("电商平台后端服务正在启动...")
    print("访问地址: http://127.0.0.1:8000")
    print("接口文档: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True
    )
