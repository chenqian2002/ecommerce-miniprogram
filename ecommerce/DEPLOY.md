# 部署指南

## 本地开发环境

### 系统要求
- Python 3.8 或以上
- pip（Python 包管理器）
- Git
- 微信开发者工具

### 安装步骤

#### 1. 克隆项目
```bash
git clone git@github.com:chenqian2002/ecommerce-miniprogram.git
cd ecommerce
```

#### 2. 后端配置

**创建虚拟环境**
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**安装依赖**
```bash
pip install -r requirements.txt
```

**初始化数据库**
```bash
python init_data.py
```

**启动服务器**
```bash
python run.py
```

服务器将在 `http://127.0.0.1:8000` 启动

**验证后端**
```bash
curl http://127.0.0.1:8000/health
# 返回：{"status": "ok"}
```

#### 3. 前端配置

**打开微信开发者工具**
1. 启动微信开发者工具
2. 选择"本地项目"
3. 项目路径：`/path/to/ecommerce/minprogram`
4. AppID：`wxf20133399e7c179c`（测试号）
5. 项目名称：任意

**关闭域名检查**
- 点击顶部菜单：详情
- 本地设置
- 取消勾选"域名检查"

**启动编译**
- 按下 `Ctrl+B`（Win）或 `Cmd+B`（Mac）

---

## 生产环境部署

### 服务器要求
- Linux 服务器（推荐 Ubuntu 20.04+）
- Python 3.8+
- Nginx（反向代理）
- PostgreSQL（生产推荐，可选）

### 部署步骤

#### 1. 服务器初始化

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和依赖
sudo apt install -y python3-pip python3-venv nginx git

# 创建应用用户
sudo useradd -m -s /bin/bash ecommerce
sudo su - ecommerce
```

#### 2. 克隆并配置项目

```bash
# 克隆项目
git clone git@github.com:chenqian2002/ecommerce-miniprogram.git
cd ecommerce/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产依赖
pip install gunicorn
```

#### 3. 环境配置

**创建 .env 文件**
```bash
cat > .env << EOF
# 数据库（改用 PostgreSQL）
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce

# JWT 密钥（生成强密钥）
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# API 配置
API_TITLE=电商平台 API
API_VERSION=1.0.0

# 环境
ENVIRONMENT=production
DEBUG=False

# 微信配置（需按实际填写）
WECHAT_APPID=your-appid
WECHAT_SECRET=your-secret
WECHAT_MCHID=your-mchid
WECHAT_API_KEY=your-api-key
EOF
```

#### 4. 数据库迁移

```bash
# 如果使用 PostgreSQL
python init_data.py

# 或使用 Alembic（可选）
alembic upgrade head
```

#### 5. 创建 Systemd 服务

**创建服务文件**
```bash
sudo tee /etc/systemd/system/ecommerce.service > /dev/null << EOF
[Unit]
Description=Ecommerce API Service
After=network.target

[Service]
Type=notify
User=ecommerce
WorkingDirectory=/home/ecommerce/ecommerce/backend
Environment="PATH=/home/ecommerce/ecommerce/backend/venv/bin"
ExecStart=/home/ecommerce/ecommerce/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/ecommerce/access.log \
    --error-logfile /var/log/ecommerce/error.log \
    app.main:app

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF
```

**启动服务**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ecommerce
sudo systemctl start ecommerce
sudo systemctl status ecommerce
```

#### 6. Nginx 配置

**创建 Nginx 配置**
```bash
sudo tee /etc/nginx/sites-available/ecommerce > /dev/null << EOF
upstream ecommerce_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # HTTP 重定向到 HTTPS（生产环境）
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # HTTPS 证书（使用 Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # GZIP 压缩
    gzip on;
    gzip_types text/plain text/css application/json;

    # 日志
    access_log /var/log/nginx/ecommerce-access.log;
    error_log /var/log/nginx/ecommerce-error.log;

    # 代理配置
    location /api/ {
        proxy_pass http://ecommerce_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://ecommerce_backend;
    }
}
EOF
```

**启用配置**
```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. SSL 证书（Let's Encrypt）

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot certonly --nginx -d api.yourdomain.com

# 自动续期
sudo systemctl enable certbot.timer
```

---

## Docker 部署（可选）

### 创建 Dockerfile

```dockerfile
# 后端 Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn uvicorn

# 复制代码
COPY backend/ .

# 环境变量
ENV PYTHONUNBUFFERED=1

# 启动
CMD ["gunicorn", "--workers", "4", "--worker-class", \
     "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", \
     "app.main:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ecommerce:password@db:5432/ecommerce
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=ecommerce
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ecommerce
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend

volumes:
  postgres_data:
```

**启动容器**
```bash
docker-compose up -d
```

---

## 监控和日志

### 日志位置

```
# Apache Gunicorn 日志
/var/log/ecommerce/access.log
/var/log/ecommerce/error.log

# Nginx 日志
/var/log/nginx/ecommerce-access.log
/var/log/nginx/ecommerce-error.log

# 系统日志
journalctl -u ecommerce -f
```

### 性能监控

```bash
# 查看进程
ps aux | grep gunicorn

# 检查内存
free -h

# 检查磁盘
df -h

# 查看网络连接
netstat -tuln | grep 8000
```

---

## 常见问题

### 1. 数据库连接失败
```bash
# 检查数据库状态
sudo systemctl status postgresql

# 查看连接
psql -l

# 创建数据库
createdb ecommerce
```

### 2. Nginx 反向代理失败
```bash
# 检查配置语法
sudo nginx -t

# 查看 Nginx 日志
tail -f /var/log/nginx/error.log

# 重启 Nginx
sudo systemctl restart nginx
```

### 3. 小程序无法连接
- 确保后端应用已启动
- 检查防火墙设置
- 更新小程序中的 API 地址
- 在生产环境需要配置真实域名

### 4. SSL 证书过期
```bash
# 手动续期
sudo certbot renew --force-renewal

# 自动续期（通常已启用）
sudo systemctl status certbot.timer
```

---

## 性能优化建议

### 1. 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_user_phone ON users(phone);
CREATE INDEX idx_product_category ON products(category_id);
CREATE INDEX idx_order_user ON orders(user_id);
```

### 2. 缓存优化
```bash
# 安装 Redis
sudo apt install redis-server

# 配置应用使用 Redis
# .env 添加
CACHE_REDIS_URL=redis://localhost:6379/0
```

### 3. 异步任务
```bash
# 安装 Celery
pip install celery

# 后台处理订单、邮件等
```

---

**最后更新**：2026年4月16日
