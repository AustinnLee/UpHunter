# Upsert(去重逻辑)
from sqlalchemy.orm import Session
from sqlalchemy import text, TextClause
from src.core.logger import setup_logger
import pandas as pd

logger = setup_logger("PostgresStorage")


class PostgresStorage:
    def __init__(self, db_session: Session):
        self.db = db_session

    def save_df_upsert(self, df: pd.DataFrame, table_name: str, date_col: str = 'trade_date'):
        """
        通用的 Upsert (有则忽略，无则插入) 逻辑
        :param df: 要存的数据
        :param table_name: 表名 (由调用者决定，而不是写死)
        :param date_col: 用来判断重复的日期列名 (默认 trade_date)
        """
        if df.empty:
            return

        try:
            # 1. 检查重复逻辑 (通用化)
            current_date = df[date_col].iloc[0]

            # 使用绑定参数防止注入，且表名也不能直接拼字符串，但 table_name 通常是可信的
            # 注意：SQLAlchemy 的 text() 不支持表名作为参数绑定，所以这里用 f-string 是妥协，
            # 但前提是 table_name 是内部代码控制的，不是用户输入的。
            check_sql: TextClause = text(f"SELECT count(*) FROM {table_name} WHERE {date_col} = :date")
            result = self.db.execute(check_sql, {"date": current_date}).scalar()

            if result > 0:
                logger.warning(f"⚠️ [{table_name}] {current_date} 数据已存在 ({result} 条)。跳过。")
                return

                # 2. 批量插入
            logger.info(f"💾 正在写入 {len(df)} 条数据到 {table_name}...")
            df.to_sql(
                name=table_name,
                con=self.db.bind,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            logger.info(f"✅ [{table_name}] 入库成功！")

        except Exception as e:
            logger.error(f"❌ [{table_name}] 入库失败: {e}")
            self.db.rollback()

    # ==========================================
    # 2. 基础 CRUD 工具 (Basic Operations)
    # [新增] 专门给 Service 层用的
    # ==========================================
    def get(self, model_class, primary_key):
        """查单条"""
        return self.db.query(model_class).get(primary_key)

    def add(self, obj):
        """加单条"""
        self.db.add(obj)

    def commit(self):
        """提交"""
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 提交事务失败: {e}")
            raise e

    def rollback(self):
        """回滚"""
        self.db.rollback()