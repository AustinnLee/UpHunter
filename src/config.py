import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    # 数据库配置
    DB_USER = os.getenv("DB_USER", "lee")
    DB_PASSWORD = os.getenv("DB_PASSWORD","")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "uphunter_db")

    # 拼接连接串
    if DB_PASSWORD:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # AI 配置
    AI_API_KEY = os.getenv("AI_API_KEY")
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    AI_MODEL = "gpt-3.5-turbo" if os.getenv("AI_PROVIDER") == "openai" else "deepseek-chat"

    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "default-insecure-key")