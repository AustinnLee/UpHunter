from src.database import SessionLocal
from src.models import UpworkJob
from src.core.ai_client import AIClient
from src.core.logger import setup_logger
import time

logger = setup_logger("Job.AI_Analysis")


def run():
    db = SessionLocal()
    ai = AIClient()

    try:
        # 1. 找出还没被 AI 分析过的职位
        # 假设如果 skills 为空，或者 skills 是我们简单清洗的，就需要 AI 再跑一遍
        # 这里我们简单点：只取前 5 条没分析过的试试水
        jobs = db.query(UpworkJob).limit(5).all()

        logger.info(f"🤖 开始 AI 深度分析，共 {len(jobs)} 个任务...")

        for job in jobs:
            if not job.description:
                continue

            logger.info(f"🧠 分析职位: {job.title[:30]}...")

            # 调用 AI
            extracted_skills = ai.extract_skills(job.description)

            if extracted_skills and "Error" not in extracted_skills:
                # 更新数据库
                # 我们可以把 AI 的结果追加到原有的 skills 后面，或者覆盖
                # 这里演示覆盖，为了看效果
                job.skills = extracted_skills
                logger.info(f"   ✅ 提取技能: {extracted_skills}")

            # 休息一下，别把 API 刷爆了
            time.sleep(1)

        db.commit()
        logger.info("💾 分析结果已保存")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ 分析失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
