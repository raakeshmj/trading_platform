from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.exceptions import AppError
from app.redis import init_redis, close_redis
from app.routers import auth, accounts, instruments, orders, ws
from app.services.market_feed import market_simulation_task # Import if we use it
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()
    task = asyncio.create_task(market_simulation_task())
    yield
    # Shutdown
    await close_redis()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(instruments.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
