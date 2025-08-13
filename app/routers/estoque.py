from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.estoque import EstoqueReal
from app.schemas.estoque import EstoqueResponse
from typing import List

router = APIRouter()

@router.get("/estoque", response_model=List[EstoqueResponse])
async def listar_estoque(db: AsyncSession = Depends(get_db)):
    query = select(EstoqueReal)
    result = await db.execute(query)
    rows = result.scalars().all()
    return rows
