import time
import urllib.parse
import pandas as pd
from src.fetchers.stealth_browser import StealthBrowserFetcher
from src.parsers.upwork import UpworkParser
from src.storage.postgres import PostgresStorage
from src.database import SessionLocal
from src.core.logger import setup_logger
from src.models import UpworkJob

logger = setup_logger("Job.UpHunter")


def run():
    logger.info("🏹 启动 UpHunter 任务 (批量稳健版)...")

    keywords = [
        "Data Engineering",
        "Streamlit",
        "Tableau",
        "Real Estate Data",
        "Web Scraping"
    ]

    MAX_PAGES = 5

    db = SessionLocal()
    storage = PostgresStorage(db)
    parser = UpworkParser()

    try:
        for kw in keywords:
            logger.info(f"\n🔍 === 开始搜索任务: {kw} ===")

            # 🟢 策略调整：每个关键词启动一个新的浏览器实例
            # 防止长时间运行导致的指纹积累或内存泄漏
            browser = StealthBrowserFetcher(headless=False)

            try:
                for page in range(1, MAX_PAGES + 1):
                    logger.info(f"   📄 正在抓取第 {page} 页...")

                    encoded_kw = urllib.parse.quote(kw)
                    url = f"https://www.upwork.com/nx/search/jobs/?q={encoded_kw}&sort=recency&page={page}"

                    # --- 重试循环 ---
                    html = None
                    for attempt in range(3):
                        try:
                            html = browser.fetch(url, wait_for_selector="article", sleep_time=10)
                            if html: break
                        except Exception as e:
                            logger.warning(f"      ⚠️ 抓取异常 (尝试 {attempt + 1}/3): {e}")
                            # 如果浏览器崩了，这里其实应该重启浏览器，简便起见先只做延时
                            time.sleep(5)

                    if html:
                        df = parser.parse(html)

                        if not df.empty:
                            logger.info(f"      ✅ 成功解析 {len(df)} 个职位")

                            # 数据补全
                            if 'skills' not in df.columns:
                                df['skills'] = ""
                            df['search_keyword'] = kw
                            df['skills'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))

                            # 入库
                            count = 0
                            for _, row in df.iterrows():
                                if not row['url']: continue
                                exists = storage.get(UpworkJob, row['url'])
                                if not exists:
                                    job = UpworkJob(
                                        url=row['url'],
                                        title=row['title'],
                                        job_type=row['job_type'],
                                        budget_min=row['budget_min'],
                                        budget_max=row['budget_max'],
                                        posted_time=row['posted_time'],
                                        search_keyword=row['search_keyword'],
                                        description=row['description'],
                                        skills=row['skills']
                                    )
                                    storage.add(job)
                                    count += 1

                            storage.commit()
                            logger.info(f"      💾 新增入库: {count} 条")

                        else:
                            logger.warning(f"      ⚠️ 页面已加载但未解析到数据 (可能翻到底了)")
                            # 如果连续空页，可以 break (这里先不 break 只要一页空)
                    else:
                        logger.error(f"      ❌ 第 {page} 页抓取彻底失败")

                    # 翻页休息
                    import random
                    sleep_time = random.randint(10, 15)
                    logger.info(f"      😴 休息 {sleep_time} 秒...")
                    time.sleep(sleep_time)

            except Exception as kw_err:
                logger.error(f"❌ 关键词 {kw} 任务发生致命错误: {kw_err}")

            finally:
                # 无论这个关键词成功还是失败，都关闭浏览器，清理环境
                browser.close()
                logger.info(f"🛑 已关闭浏览器。冷却 10 秒准备下一个关键词...")
                time.sleep(10)

    except Exception as e:
        logger.critical(f"❌ 主进程崩溃: {e}")
    finally:
        db.close()
        logger.info("🎉 所有任务结束。")


if __name__ == "__main__":
    run()
