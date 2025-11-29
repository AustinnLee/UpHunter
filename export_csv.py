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
