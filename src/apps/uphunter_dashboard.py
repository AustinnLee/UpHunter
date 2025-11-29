import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import sys
import os
import re

# 路径补丁
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import Config

# 连接数据库
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

st.set_page_config(page_title="UpHunter Market Insights", layout="wide", page_icon="🏹")

st.title("🏹 UpHunter: 自由职业市场情报中心")


# 1. 加载数据
@st.cache_data(ttl=60)
def load_data():
    try:
        return pd.read_sql("SELECT * FROM upwork_jobs", engine)
    except Exception as e:
        st.error(f"数据库连接失败: {e}")
        return pd.DataFrame()


df = load_data()

if df.empty:
    st.warning("暂无数据，请运行爬虫。")
    st.stop()

# 2. 数据清洗 (用于展示)
# 过滤掉 Budget 极大的异常值 (可能是占位符)
df_clean = df.copy()
df_clean['budget_max'] = pd.to_numeric(df_clean['budget_max'], errors='coerce').fillna(0)

# 🚫 过滤掉 0 和 超大值
mask = (df_clean['budget_max'] > 50) & (df_clean['budget_max'] < 20000)
clean_df = df_clean[mask]


df_clean = df_clean[df_clean['budget_max'] > 0]  # 只看有预算的
df_clean = df_clean[df_clean['budget_max'] < 50000]  # 过滤掉比如 100万 的假预算

# 3. KPI
col1, col2, col3 = st.columns(3)
col1.metric("总职位数", len(df))
col2.metric("平均预算 (Fixed)", f"${df_clean[df_clean['job_type'] == 'Fixed']['budget_max'].mean():.0f}")
col3.metric("最高时薪 (Hourly)", f"${df_clean[df_clean['job_type'] == 'Hourly']['budget_max'].max():.0f}/hr")

st.markdown("---")

# 4. 核心图表：哪个技能钱多？
st.subheader("💰 技能价值分布 (Box Plot)")
fig_box = px.box(
    df_clean,
    x="search_keyword",
    y="budget_max",
    color="job_type",
    #points="all",
    hover_data=["title"],
    title="不同技能关键词的预算分布"
)
st.plotly_chart(fig_box, use_container_width=True)

# 5. 核心图表：技能需求量
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 职位数量对比")
    count_df = df['search_keyword'].value_counts().reset_index()
    count_df.columns = ['Keyword', 'Count']
    fig_bar = px.bar(count_df, x='Keyword', y='Count', color='Keyword')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("☁️ 热门词汇 (Description)")
    # 🔍 Debug: 看看原始文本是不是空的
    raw_text = " ".join(df['description'].astype(str).tolist())
    st.write(f"Debug: 文本总长度 = {len(raw_text)}")

    from collections import Counter

    text = " ".join(df['description'].astype(str).tolist()).lower()
    # 简单的停用词过滤
    stopwords = set(['the', 'and', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'with', 'we', 'are', 'looking'])
    words = [w for w in re.findall(r'\w+', text) if len(w) > 3 and w not in stopwords]
    common_words = Counter(words).most_common(15)

    #只取前 10 个
    wc_df = pd.DataFrame(common_words[0:10], columns=['Word', 'Count'])
    # orientation='h' 让条条横过来，字就不会挤在一起了
    fig_wc = px.bar(wc_df, x='Count', y='Word', orientation='h', title="Top 10 Keywords")
    # 倒序排列，让最大的在上面
    fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_wc, use_container_width=True)

# 6. 详细列表
with st.expander("🔎 职位猎手 (点击标题跳转)"):
    # 制作可点击的链接
    display_df = df[['title', 'budget_max', 'job_type', 'search_keyword', 'url']].copy()

    # Streamlit 的 dataframe 组件支持链接列配置
    st.dataframe(
        display_df,
        column_config={
            "url": st.column_config.LinkColumn("Apply Link")
        },
        use_container_width=True
    )
