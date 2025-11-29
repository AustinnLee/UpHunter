import sys
import os

# 1. 路径补丁 (确保能找到 src)
sys.path.append(os.getcwd())

from src.database import engine, Base
# 2. 必须导入模型，否则 Base 不知道要建什么表
from src.models import UpworkJob

def init():
    print("⚙️ 初始化数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 表结构创建成功！")

if __name__ == "__main__":
    init()
