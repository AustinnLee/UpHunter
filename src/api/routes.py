from fastapi import APIRouter, Depends, HTTPException,BackgroundTasks
from src.jobs import scrape_upwork
from sqlalchemy.orm import Session
from src.database import get_db  # 记得我们之前写的依赖注入吗？现在派上用场了
from src.models import UpworkJob
from typing import List, Optional
from src.api.auth import verify_api_key
router = APIRouter(dependencies=[Depends(verify_api_key)])


# 定义返回的数据格式 (Pydantic Model) - 这是一个好的工程实践，但为了简单先跳过，直接返回 dict

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
        # 模糊搜索
        query = query.filter(UpworkJob.search_keyword.ilike(f"%{keyword}%"))

    # 按时间倒序
    jobs = query.order_by(UpworkJob.created_at.desc()).limit(limit).all()

    return jobs  # FastAPI 会自动把 ORM 对象转成 JSON


@router.get("/stats", tags=["Analytics"])
def get_stats(db: Session = Depends(get_db)):
    """
    获取统计数据 (API 版 Dashboard)
    """
    total = db.query(UpworkJob).count()
    # 简单的统计示例
    return {
        "total_jobs": total,
        "status": "healthy"
    }


# 定义一个后台任务函数
def run_crawler_task(keyword: str):
    print(f"🚀 [Background] 开始抓取: {keyword}")
    # 这里调用你之前的爬虫逻辑，稍微改造一下 scrape_upwork 让它支持传参
    # scrape_upwork.run_single_keyword(keyword)
    pass


@router.post("/crawl", tags=["Actions"])
def trigger_crawl(
        keyword: str,
        background_tasks: BackgroundTasks
):
    """
    触发爬虫任务 (异步执行，不会卡住接口)
    """
    # 把任务扔到后台去跑，立刻给用户返回结果
    background_tasks.add_task(run_crawler_task, keyword)

    return {
        "message": f"爬虫任务已启动: {keyword}",
        "status": "processing"
    }