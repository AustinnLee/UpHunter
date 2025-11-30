import sentry_sdk
from fastapi import FastAPI
from src.api import routes

# ==========================================
# 1. Sentry 初始化 (硬编码 DSN，排除一切干扰)
# ==========================================
# 请直接使用这个 DSN，不要改动任何标点符号
SENTRY_DSN_FINAL = "https://956951d1295123307ddddeaa185c8355@o4510447033843712.ingest.us.sentry.io/4510447065890816"

try:
    sentry_sdk.init(
        dsn=SENTRY_DSN_FINAL,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        debug=True # 保持开启，方便看日志
    )
    print(f"✅ Sentry initialized with DSN: {SENTRY_DSN_FINAL[:10]}...")
except Exception as e:
    print(f"❌ Sentry init failed: {e}")

# ==========================================
# 2. App 初始化
# ==========================================
app = FastAPI(
    title="UpHunter API",
    description="Upwork 职位数据猎手 - 企业级数据接口",
    version="1.0.0"
)

# 3. 挂载路由
app.include_router(routes.router)

# 4. 根路径
@app.get("/")
def root():
    return {"message": "Welcome to UpHunter API."}

# 5. 错误触发器 (公开接口)
@app.get("/sentry-debug")
def trigger_error():
    print("💣 正在手动触发 ZeroDivisionError...")
    return 1 / 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
