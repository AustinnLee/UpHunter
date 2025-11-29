import sentry_sdk
from fastapi import FastAPI
from src.config import Config
from src.api import routes

# 1. Sentry 初始化
if Config.SENTRY_DSN:
    print(f"🔍 Sentry DSN found: {Config.SENTRY_DSN[:10]}...")  # 打印前10位确认读到了

    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        debug=True  # 🟢 开启调试模式！
    )
    print("✅ Sentry initialized in DEBUG mode.")
else:
    print("⚠️ Sentry DSN not found.")

# 2. App 初始化
app = FastAPI(
    title="UpHunter API",
    description="Upwork 职位数据猎手 - 企业级数据接口",
    version="1.0.0"
)

# 3. 挂载受保护的路由 (需要密码的)
app.include_router(routes.router)

# 4. 根路径 (公开)
@app.get("/")
def root():
    return {"message": "Welcome to UpHunter API."}

# 5. Sentry 测试接口 (公开，不需要密码)
@app.get("/sentry-debug")
def trigger_error():
    print("💣 正在手动触发 ZeroDivisionError...")
    return 1 / 0  # 这行必定报错

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
