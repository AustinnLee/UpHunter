from src.core.ai_client import AIClient

# 模拟一段 Upwork 描述
desc = """
We are looking for an expert in Python and Web Scraping.
You must know Selenium, BeautifulSoup and Postgres.
Experience with AWS is a plus.
"""

client = AIClient()
print("🤖 AI 正在分析...")
skills = client.extract_skills(desc)
print(f"🎯 提取结果: {skills}")
