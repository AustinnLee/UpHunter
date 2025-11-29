from fastapi import FastAPI
import sentry_sdk

sentry_sdk.init(
    dsn="https://956951d1295123307ddddeaa185c8355@o4510447033843712.ingest.us.sentry.io/4510447065890816",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = FastAPI()
