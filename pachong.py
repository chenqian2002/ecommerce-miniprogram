# 正确导入方式
from bs4 import BeautifulSoup
import requests  # 注意拼写：requests，不是 resquest

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.google.com/"  # 假裝從 Google 跳過來，有時有效
}

# 修正：headers=（不是 hearders=），requests（不是 resquest）
response = requests.get("https://movie.douban.com/top250", headers=headers)
html=response.text
soup=BeautifulSoup(html,'html.parser')
all_title=soup.findAll("span",attrs={"class":"title"})
#print(all_title.string)
for title in all_title:
    title_string= title.string
    if "/" not in title_string:
        print(title_string)
