from fastapi import FastAPI
from src.api import routes
import sentry_sdk
from src.config import Config

# 1. 初始化 Sentry (在 FastAPI App 创建之前)
if Config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        # 设置捕获率 1.0 = 100% 的错误都抓
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# 初始化 App
app = FastAPI(
    title="UpHunter API",
    description="Upwork 职位数据猎手 - 企业级数据接口",
    version="1.0.0"
)

# 注册路由 (把具体的接口挂载上来)
app.include_router(routes.router)

# 根路径
@app.get("/")
def root():
    return {"message": "Welcome to UpHunter API. Visit /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)
