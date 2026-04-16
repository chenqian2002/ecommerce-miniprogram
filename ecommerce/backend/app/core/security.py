"""
密码加密模块 - 用于安全存储密码

这个模块解决的问题：
- 不能直接存储明文密码（太危险）
- 使用 hash 算法对密码进行加密
- 登录时比对加密后的密码
"""

import hashlib

def hash_password(password: str) -> str:
    """
    对密码进行加密
    
    为什么需要？
    - 数据库中存的不是明文密码，而是加密后的值
    - 即使数据库被黑，也无法直接得到用户密码
    
    原理：
    - 使用 SHA256 算法进行哈希
    - 同一个密码每次加密结果相同（便于验证）
    
    例如：
        password = "123456"
        encrypted = hash_password(password)
        # encrypted = "8d969eef6ecad3c29a3a873fba8cac1..."
        
        verify_password("123456", encrypted)  # True
        verify_password("wrong", encrypted)   # False
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    参数：
    - plain_password: 用户输入的原始密码（明文）
    - hashed_password: 数据库中存储的加密密码
    
    返回：
    - True: 密码匹配
    - False: 密码错误
    
    流程：
        用户输入 "123456"
            ↓
        verify_password("123456", "8d969eef...")
            ↓
        对比两个 hash 值是否相同
            ↓
        返回 True 或 False
    """
    return hash_password(plain_password) == hashed_password
