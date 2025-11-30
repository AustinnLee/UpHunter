from src.database import SessionLocal
from src.models import UpworkJob
from src.core.vector_store import VectorStore
from src.core.logger import setup_logger

logger = setup_logger("Job.SyncVectors")


def run():
    db = SessionLocal()
    vector_db = VectorStore()

    try:
        # 1. 查出所有有描述的职位
        jobs = db.query(UpworkJob).filter(UpworkJob.description != None).all()
        logger.info(f"🔍 数据库中共有 {len(jobs)} 个有效职位，准备向量化...")

        batch_size = 50
        batch_data = []

        for job in jobs:
            # 准备数据
            # text: 只有描述参与搜索
            # meta: 标题、预算等信息作为元数据存起来，不用搜，但展示时需要
            item = {
                "id": job.url,
                "text": f"{job.title}. {job.description}",  # 把标题和描述拼在一起搜
                "meta": {
                    "title": job.title,
                    "budget": str(job.budget_max) if job.budget_max else "0",
                    "type": job.job_type or "Unknown"
                }
            }
            batch_data.append(item)

            # 批量写入
            if len(batch_data) >= batch_size:
                vector_db.add_jobs(batch_data)
                batch_data = []

        # 写入剩余的
        if batch_data:
            vector_db.add_jobs(batch_data)

    finally:
        db.close()


if __name__ == "__main__":
    run()
