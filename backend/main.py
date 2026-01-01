from fastapi import FastAPI
from .interfaces.api import router as api_router
from .interfaces.middleware import AuditLoggingMiddleware
from .infrastructure.postgres_repo import PostgresClaimRepository
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

app = FastAPI(title="AegisClaims AI Platform")

# Register Middleware
app.add_middleware(AuditLoggingMiddleware)

# database setup (Example)
# DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"
# engine = create_async_engine(DATABASE_URL)
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@app.on_event("startup")
async def startup():
    # Initialize DB, AI Clients, etc.
    pass

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
