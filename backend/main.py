import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import users, parking_spots, parking_records, reservations, ai, auth
from backend.database import init_db
from backend.config import CORS_ORIGINS, HOST, PORT
import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="智能停车管理系统",
    description="规则驱动的智能停车管理系统（上海实际使用基础上的开放复用版）",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(parking_spots.router)
app.include_router(parking_records.router)
app.include_router(reservations.router)
app.include_router(ai.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 挂载前端静态文件（放在路由之后，避免覆盖 API 路由）
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
