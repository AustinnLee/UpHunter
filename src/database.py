#SQLAlchemy 的 引擎Engine和会话SessionLocal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from src.config import Config
# 1. 加载 .env 文件里的密码
# 哪怕你现在没用 .env，也先写上，这是好习惯
load_dotenv()

# 2. 配置数据库连接串 (Connection String)
# 格式: postgresql://用户名:密码@地址:端口/数据库名
# 如果你是 Mac Postgres.app，默认没有密码，用户通常是你的系统用户名

# 3. 创建引擎 (Engine)
# echo=True 会在控制台打印出生成的 SQL 语句，方便调试（生产环境要关掉）
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# 4. 创建会话工厂 (SessionLocal)
# 以后我们要操作数据库，就找 SessionLocal 要一个 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 创建基类 (Base)
# 以后所有的表模型都要继承这个 Base
Base = declarative_base()

# 6. 依赖注入工具 (Dependency)
# 用法：with get_db() as db: ...
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 在 src/database.py 底部添加
if __name__ == "__main__":
    # 临时导入模型以触发注册
    from src.models import UpworkJob
    print("⚙️ Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done.")