import pandas as pd
from sqlalchemy import create_engine
from src.config import Config

# 连接数据库
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# 读取所有数据
print("正在从数据库导出...")
df = pd.read_sql("SELECT * FROM upwork_jobs", engine)

# 保存为 CSV
output_file = "upwork_market_data.csv"
df.to_csv(output_file, index=False)

print(f"✅ 导出成功！共 {len(df)} 条数据。")
print(f"文件路径: {output_file}")
现在我想用另外一个项目，新的工程来练习上述所有的内容保证我全部学会了，
请翻阅我给你的那份upwork的工作需求，帮我找一个非爬虫类的项目，帮我练习一遍所有内容，
如果有新的内容也更好了，