from sqlalchemy import Column, String, Integer, Text, DateTime, func
from src.database import Base


class UpworkJob(Base):
    __tablename__ = "upwork_jobs"

    # 职位链接通常包含唯一ID，适合做主键
    # 例如: https://www.upwork.com/jobs/~01abcd1234...
    url = Column(String(500), primary_key=True)

    title = Column(String(255))
    job_type = Column(String(50))  # Hourly / Fixed

    # 薪资范围 (标准化为数字，方便分析)
    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)

    posted_time = Column(String(100))  # 原始字符串 "5 minutes ago"
    search_keyword = Column(String(100))  # 我们搜什么词抓到的

    description = Column(Text)  # 职位详情
    skills = Column(Text)  # 技能标签 (逗号分隔)

    # 抓取时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
