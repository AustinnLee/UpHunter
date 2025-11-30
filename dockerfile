# 1. 基础镜像 (Base Image)
# 我们选一个轻量级的 Python 3.10 官方镜像
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统依赖 (Postgres驱动、Chrome依赖)
# Chrome 依赖是爬虫最头疼的，这里我们先只做 API 服务的打包
# 如果要包含爬虫，Dockerfile 会复杂很多 (需要装 Chrome)
# 这节课我们要先学会打包 API
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 复制依赖清单
COPY requirements.txt .

# 5. 安装 Python 依赖
# --no-cache-dir 减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制源代码
COPY . .

# 7. 暴露端口 (FastAPI 默认 8000)
EXPOSE 10000

# 8. 启动命令 (使用 shell 格式，以便读取变量)
# 如果有 $PORT 就用 $PORT，否则用 8000
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
