from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models.produto import DimProduto
from app.models import FactSaida, FactRecebimento
from app.schemas.saldos import SaldosResponse

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/saldos", response_model=SaldosResponse)
async def balance(db: AsyncSession = Depends(get_db)):
    # CTE para o saldo acumulado
    saldo_cte = (
        select(
            DimProduto.codigo.label("codigo"),
            DimProduto.nome_basico.label("nome_basico"),
            FactRecebimento.lote.label("lote"),
            DimProduto.imagem.label("imagem"),
            func.to_char(FactRecebimento.validade, "DD/MM/YYYY").label("validade"),
            func.coalesce(func.sum(FactRecebimento.quant), 0).label("quant_recebimento"),
            func.coalesce(func.sum(FactSaida.quant), 0).label("quant_saida"),
        )
        .join(DimProduto, FactRecebimento.codigo == DimProduto.codigo)
        .outerjoin(FactSaida, FactRecebimento.codigo == FactSaida.codigo)
        .group_by(
            DimProduto.codigo,
            DimProduto.nome_basico,
            FactRecebimento.lote,
            DimProduto.imagem,
            FactRecebimento.validade,
        )
        .cte("SaldoAcumulado")
    )

    # SELECT final usando a CTE
    query = (
        select(
            saldo_cte.c.codigo,
            saldo_cte.c.nome_basico,
            saldo_cte.c.lote,
            saldo_cte.c.imagem,
            saldo_cte.c.validade,
            saldo_cte.c.quant_recebimento,
            saldo_cte.c.quant_saida,
            (saldo_cte.c.quant_recebimento - saldo_cte.c.quant_saida).label("saldo"),
        )
    )

    try:
        result = await db.execute(query)
        saldos = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha interna do servidor")

    dados = [dict(row) for row in saldos]

    return SaldosResponse(
        dados=dados
    )    

@router.get("/saldos/{codigo}", response_model=SaldosResponse)
async def balance(codigo: int, db: AsyncSession = Depends(get_db)):
    # CTE para o saldo acumulado
    saldo_cte = (
        select(
            DimProduto.codigo.label("codigo"),
            DimProduto.nome_basico.label("nome_basico"),
            FactRecebimento.lote.label("lote"),
            DimProduto.imagem.label("imagem"),
            func.to_char(FactRecebimento.validade, "DD/MM/YYYY").label("validade"),
            func.coalesce(func.sum(FactRecebimento.quant), 0).label("quant_recebimento"),
            func.coalesce(func.sum(FactSaida.quant), 0).label("quant_saida"),
        )
        .join(DimProduto, FactRecebimento.codigo == DimProduto.codigo)
        .outerjoin(FactSaida, FactRecebimento.codigo == FactSaida.codigo)
        .group_by(
            DimProduto.codigo,
            DimProduto.nome_basico,
            FactRecebimento.lote,
            DimProduto.imagem,
            FactRecebimento.validade,
        )
        .cte("SaldoAcumulado")
    )

    # SELECT final usando a CTE
    query = (
        select(
            saldo_cte.c.codigo,
            saldo_cte.c.nome_basico,
            saldo_cte.c.lote,
            saldo_cte.c.imagem,
            saldo_cte.c.validade,
            saldo_cte.c.quant_recebimento,
            saldo_cte.c.quant_saida,
            (saldo_cte.c.quant_recebimento - saldo_cte.c.quant_saida).label("saldo"),
        )
        .where(saldo_cte.c.codigo == codigo)
    )

    try:
        result = await db.execute(query)
        saldos = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha interna do servidor")

    # Para evitar erros do pydantic
    dados = [dict(row) for row in saldos]

    return SaldosResponse(
        dados=dados
    )