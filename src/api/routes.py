from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import UpworkJob
from typing import List, Optional
from src.api.auth import verify_api_key

# 全局鉴权
router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/jobs", tags=["Jobs"])
def get_jobs(
        limit: int = 10,
        keyword: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    获取职位列表 (支持关键词过滤)
    """
    query = db.query(UpworkJob)

    if keyword:
        query = query.filter(UpworkJob.search_keyword.ilike(f"%{keyword}%"))

    jobs = query.order_by(UpworkJob.created_at.desc()).limit(limit).all()
    return jobs


@router.get("/stats", tags=["Analytics"])
def get_stats(db: Session = Depends(get_db)):
    """
    获取统计数据
    """
    try:
        total = db.query(UpworkJob).count()
        return {
            "total_jobs": total,
            "status": "healthy",
            "db_connection": "ok"
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


def run_crawler_task(keyword: str):
    """
    后台任务逻辑
    """
    print(f"🚀 [Background] 收到抓取请求: {keyword}")

    try:
        # 🟢 延迟导入 (Lazy Import) - 关键修复！
        # 只有在真正执行任务时才加载爬虫模块，避免 API 启动时因缺 Chrome 报错
        from src.jobs import scrape_upwork

        # 注意：目前的 scrape_upwork.run() 是跑死数据的
        # 如果你想让它只跑这个 keyword，你需要去修改 scrape_upwork.run 接受参数
        # 这里暂时先跑全量
        scrape_upwork.run()

    except ImportError as e:
        print(f"❌ 严重错误: 无法加载爬虫模块 (可能是服务器缺少 Chrome 环境): {e}")
    except Exception as e:
        print(f"❌ 爬虫运行出错: {e}")


@router.post("/crawl", tags=["Actions"])
def trigger_crawl(
        keyword: str,
        background_tasks: BackgroundTasks
):
    """
    触发爬虫任务 (异步)
    """
    background_tasks.add_task(run_crawler_task, keyword)

    return {
        "message": f"爬虫任务已提交至后台队列: {keyword}",
        "status": "processing",
        "note": "如果是云端环境且未配置 Chrome，此任务可能会失败，请查看后台日志。"
    }
