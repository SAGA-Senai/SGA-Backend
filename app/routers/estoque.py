from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.estoque import EstoqueReal
from app.schemas.estoque import EstoqueResponse
from app.models.recebimento import FactRecebimento
from app.schemas.recebimentos import EstoqueSeguranca
from typing import List
from sqlalchemy import func

router = APIRouter()

@router.get("/estoque", response_model=List[EstoqueResponse])
async def listar_estoque(db: AsyncSession = Depends(get_db)):
    query = select(EstoqueReal)
    result = await db.execute(query)
    rows = result.scalars().all()
    return rows

@router.get("/estoqueseguranca", response_model=List[EstoqueSeguranca])
async def calcularestoque(db: AsyncSession = Depends(get_db)):
    query = (
        select(
            FactRecebimento.codigo,
            ((func.max(FactRecebimento.quant) + func.min(FactRecebimento.quant)) / 2).label("estoque_seguranca")
        )
        .group_by(FactRecebimento.codigo)
    )
    result = await db.execute(query)
    rows = result.all()  # retorna lista de tuplas (codigo, estoque_seguranca)

    # transformar em lista de dicts
    return [{"codigo": r[0], "estoque_seguranca": r[1]} for r in rows]