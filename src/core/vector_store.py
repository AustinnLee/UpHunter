import lancedb
from src.config import Config
from openai import OpenAI
from src.core.logger import setup_logger
import os

logger = setup_logger("VectorStore")


class VectorStore:
    def __init__(self):
        # 1. 初始化 OpenAI
        self.client = OpenAI(
            api_key=Config.AI_API_KEY,
            base_url=Config.AI_BASE_URL
        )

        # 2. 初始化 LanceDB (本地文件数据库)
        db_path = os.path.join(os.getcwd(), "data", "lancedb")
        os.makedirs(db_path, exist_ok=True)
        self.db = lancedb.connect(db_path)

        # 3. 创建表 (如果不存在)
        # LanceDB 需要先定义 Schema，或者第一次 add 时自动推断
        # 这里我们用自动推断模式
        self.table_name = "upwork_jobs"

    def _get_embedding(self, text):
        """调用 OpenAI 获取向量"""
        text = text.replace("\n", " ")
        try:
            return self.client.embeddings.create(
                input=[text],
                model=Config.EMBEDDING_MODEL  # 便宜又快
            ).data[0].embedding
        except Exception as e:
            logger.error(f"❌ Embedding 失败: {e}")
            return [0.0] * 1024 # 返回空向量防止崩盘

    def add_jobs(self, jobs):
        """
        jobs: list of dict [{'id':..., 'text':..., 'meta':...}]
        """
        if not jobs: return

        data_to_insert = []
        logger.info(f"⚡️ 正在生成 {len(jobs)} 个向量 (调用 API)...")

        for job in jobs:
            vector = self._get_embedding(job['text'])
            # LanceDB 要求扁平化结构
            item = {
                "id": job['id'],
                "vector": vector,
                "text": job['text'],
                "title": job['meta']['title'],
                "budget": job['meta']['budget'],
                "type": job['meta']['type']
            }
            data_to_insert.append(item)

        try:
            # 打开表 (如果不存在就创建)
            if self.table_name in self.db.table_names():
                tbl = self.db.open_table(self.table_name)
                tbl.add(data_to_insert)
            else:
                self.db.create_table(self.table_name, data=data_to_insert)

            logger.info(f"✅ {len(jobs)} 条数据已存入 LanceDB")
        except Exception as e:
            logger.error(f"❌ 存储失败: {e}")

    def search(self, query, top_k=5):
        """语义搜索"""
        if self.table_name not in self.db.table_names():
            return []

        query_vector = self._get_embedding(query)

        tbl = self.db.open_table(self.table_name)
        # LanceDB 的搜索语法
        results = tbl.search(query_vector).limit(top_k).to_pandas()
        return results.to_dict('records')
