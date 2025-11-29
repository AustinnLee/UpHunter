from openai import OpenAI
from src.config import Config
from src.core.logger import setup_logger

logger = setup_logger("AIClient")

class AIClient:
    def __init__(self):
        if not Config.AI_API_KEY:
            logger.warning("⚠️ 未配置 AI_API_KEY，AI 功能将不可用")
            self.client = None
            return

        # 初始化 OpenAI 客户端 (兼容 DeepSeek/Moonshot)
        self.client = OpenAI(
            api_key=Config.AI_API_KEY,
            base_url=Config.AI_BASE_URL
        )
        self.model = Config.AI_MODEL

    def analyze_text(self, text, prompt):
        """通用文本分析方法"""
        if not self.client:
            return "AI未启用"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是我的数据分析助手。请只返回结果，不要废话。"},
                    {"role": "user", "content": f"{prompt}\n\n内容:\n{text[:2000]}"} # 截断防止超长
                ],
                temperature=0.1 # 低温度，结果更稳定
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ AI 请求失败: {e}")
            return "Error"

    def extract_skills(self, job_description):
        """专门用于提取技能"""
        prompt = "请从以下职位描述中，提取出最核心的 3-5 个技术栈关键词，用逗号分隔。例如: Python, SQL, AWS。"
        return self.analyze_text(job_description, prompt)
