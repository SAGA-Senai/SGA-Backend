from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import sessionmaker, aliased
from app.core.database import SessionLocal
from app.models.produto import DimProduto
from app.models import FactSaida, FactRecebimento
from app.schemas.saldos import SaldosResponse
import base64

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

def get_saldos_query():
    """
    Função auxiliar para construir a query base de saldos.
    Isso evita duplicação de código entre as endpoints.
    """
    # subquery para agregar os dados de recebimento
    recebimento_sub = select(
        FactRecebimento.lote,
        FactRecebimento.fornecedor,
        FactRecebimento.validade,
        FactRecebimento.codigo,
        func.sum(FactRecebimento.quant).label('quant_recebimento')
    ).group_by(
        FactRecebimento.lote,
        FactRecebimento.fornecedor,
        FactRecebimento.validade,
        FactRecebimento.codigo
    ).subquery()

    # subquery para agregar os dados de saida
    saida_sub = select(
        FactSaida.lote,
        FactSaida.fornecedor,
        func.sum(FactSaida.quant).label('quant_saida')
    ).group_by(
        FactSaida.lote,
        FactSaida.fornecedor
    ).subquery()

    # aliased para referenciar as subqueries de forma clara
    r = aliased(recebimento_sub)
    s = aliased(saida_sub)

    # query principal com os JOINs
    query = select(
        DimProduto.codigo,
        DimProduto.nome_basico,
        r.c.lote,
        DimProduto.imagem,
        DimProduto.fragilidade,
        DimProduto.fabricante,
        r.c.fornecedor,
        DimProduto.preco_de_venda,
        # Note: func.to_char é uma função específica do PostgreSQL.
        func.to_char(r.c.validade, 'DD/MM/YYYY').label('validade'),
        func.coalesce(r.c.quant_recebimento, 0).label('quant_recebimento'),
        func.coalesce(s.c.quant_saida, 0).label('quant_saida'),
        (func.coalesce(r.c.quant_recebimento, 0) - func.coalesce(s.c.quant_saida, 0)).label('saldo')
    ).join(
        r, DimProduto.codigo == r.c.codigo
    ).outerjoin(
        s, and_(r.c.lote == s.c.lote, r.c.fornecedor == s.c.fornecedor)
    )

    return query


@router.get("/saldos", response_model=SaldosResponse)
async def balance(db: AsyncSession = Depends(get_db)):
    query = get_saldos_query()

    try:
        result = await db.execute(query)
        saldos = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha interna do servidor")

    dados = []
    for saldo in saldos:
        row = dict(saldo)
        if row.get('imagem') and isinstance(row.get('imagem'), (bytes, bytearray)):
            row['imagem'] =  base64.b64encode(row["imagem"]).decode("utf-8")
        row['fragilidade'] = 'SIM' if row['fragilidade'] else 'NÃO'
        dados.append(row)

    return SaldosResponse(
        dados=dados
    )    

@router.get("/saldos/{codigo}", response_model=SaldosResponse)
async def balance(codigo: int, db: AsyncSession = Depends(get_db)):
    query = get_saldos_query().where(DimProduto.codigo == codigo)

    try:
        result = await db.execute(query)
        saldos = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha interna do servidor")

    # Para evitar erros do pydantic
    dados = []
    for saldo in saldos:
        row = dict(saldo)
        if row.get('imagem') and isinstance(row.get('imagem'), (bytes, bytearray)):
            row['imagem'] =  base64.b64encode(row["imagem"]).decode("utf-8")
        row['fragilidade'] = 'SIM' if row['fragilidade'] else 'NÃO'
        dados.append(row)

    return SaldosResponse(
        dados=dados
    )