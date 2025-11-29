from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import UpworkJob
from typing import List, Optional
from src.api.auth import verify_api_key

# 全局鉴权：这个文件里的所有接口，都必须带 API Key
router = APIRouter(dependencies=[Depends(verify_api_key)])


# --- 1. 获取职位列表 ---
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

    # 按时间倒序
    jobs = query.order_by(UpworkJob.created_at.desc()).limit(limit).all()
    return jobs


# --- 2. 获取统计数据 ---
@router.get("/stats", tags=["Analytics"])
def get_stats(db: Session = Depends(get_db)):
    """
    获取数据库统计概览
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


# --- 3. 触发爬虫 (后台任务) ---

def run_crawler_task(keyword: str):
    """
    实际执行爬虫的逻辑 (运行在后台线程)
    """
    print(f"🚀 [Background] 收到抓取请求: {keyword}")

    try:
        # 延迟导入，防止 Docker 启动时因缺 Chrome 而崩溃
        from src.jobs import scrape_upwork

        # 这里调用爬虫的主入口
        # 注意：目前的 scrape_upwork.run() 是跑全量关键词的
        # 如果你想只跑这一个 keyword，你需要去改造 scrape_upwork.py
        # 暂时先跑默认的全量逻辑
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
    # 将任务加入后台队列，立即返回响应
    background_tasks.add_task(run_crawler_task, keyword)

    return {
        "message": f"爬虫任务已提交至后台队列 (关键词: {keyword})",
        "status": "processing",
        "note": "如果是云端环境且未配置 Chrome，此任务可能会失败，请查看后台日志。"
    }
