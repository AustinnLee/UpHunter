from openai import OpenAI
from src.config import Config
from src.core.logger import setup_logger
from src.core.vector_store import VectorStore  # 引入向量库

logger = setup_logger("AIClient")


class AIClient:
    def __init__(self):
        if not Config.AI_API_KEY:
            logger.warning("⚠️ 未配置 AI_API_KEY，AI 功能将不可用")
            self.client = None
            return

        # 初始化客户端 (SiliconFlow)
        self.client = OpenAI(
            api_key=Config.AI_API_KEY,
            base_url=Config.AI_BASE_URL
        )

        # 显式指定对话模型 (SiliconFlow 免费且强大的 DeepSeek V3)
        self.chat_model = "deepseek-ai/DeepSeek-V3"

        # 显式指定嵌入模型 (必须和 vector_store 里一致)
        self.embedding_model = "BAAI/bge-m3"

    def _get_embedding(self, text):
        """内部方法：获取向量 (供 VectorStore 使用)"""
        text = text.replace("\n", " ")
        try:
            return self.client.embeddings.create(
                input=[text],
                model=self.embedding_model
            ).data[0].embedding
        except Exception as e:
            logger.error(f"❌ Embedding 失败: {e}")
            # bge-m3 维度是 1024
            return [0.0] * 1024

    def chat_with_jobs(self, user_query):
        """
        RAG 核心逻辑：先搜向量库，再问 AI
        """
        if not self.client:
            return "AI 服务未初始化"

        # 1. 搜索最相关的职位 (Retrieval)
        # VectorStore 内部会调用 self.client (如果我们在 VectorStore 里传入 client 更好，但现在解耦也行)
        vector_store = VectorStore()
        results = vector_store.search(user_query, top_k=5)

        if not results:
            return "抱歉，数据库中没有找到相关的职位数据。请先运行爬虫抓取更多数据。"

        # 2. 构建 Prompt (Augmentation)
        context_text = ""
        for i, item in enumerate(results):
            # 处理 LanceDB 返回的数据结构 (可能是 dict 或 object)
            title = item.get('title', 'Unknown')
            budget = item.get('budget', 'Unknown')
            desc = item.get('text', '')[:300]  # 截断描述

            context_text += f"""
            [职位 {i + 1}]
            标题: {title}
            预算: {budget}
            描述: {desc}...
            ----------------
            """

        prompt = f"""
        你是一个专业的 Upwork 求职顾问。

        用户的问题: "{user_query}"

        我为你从数据库中检索到了以下最相关的职位 (Context):
        {context_text}

        请基于上述职位信息，回答用户的问题。
        1. 推荐 1-2 个最匹配的职位。
        2. 说明推荐理由。
        3. 如果职位预算太低或不匹配，请直说。
        """

        # 3. 生成回答 (Generation)
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "你是一个乐于助人的数据分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"RAG 生成失败: {e}")
            return f"AI 思考超时或出错: {e}"

    def extract_skills(self, job_description):
        """(旧功能) 用于提取技能"""
        if not self.client: return "Error"
        prompt = "请从以下职位描述中，提取出最核心的 3-5 个技术栈关键词，用逗号分隔。例如: Python, SQL, AWS。"
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "只能返回关键词，不要废话。"},
                    {"role": "user", "content": f"{prompt}\n\n{job_description[:2000]}"}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Error"
