from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers import auth, recebimentos, saidas, saldos
from fastapi.middleware.cors import CORSMiddleware
from app.routers import produtos
from app.routers import estoque
from app.routers import chart


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ou ['https://meu‑site.com']
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(produtos.router, prefix="/api")
app.include_router(recebimentos.router)
app.include_router(saidas.router)
app.include_router(saldos.router)
app.include_router(estoque.router)
app.include_router(chart.router)