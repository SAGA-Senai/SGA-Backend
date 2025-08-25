from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, literal
from app.core.database import get_db
from app.models.estoque import EstoqueReal
from app.schemas.estoque import EstoqueResponse, CatalogoResponse
from app.models.saida import FactSaida
from app.schemas.saidas import EstoqueSeguranca
from app.models.produto import DimProduto
from typing import List
from sqlalchemy import func
import base64

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
            FactSaida.codigo,
            ((func.max(FactSaida.quant) + func.min(FactSaida.quant)) / 2).label("estoque_seguranca")
        )
        .group_by(FactSaida.codigo)
    )
    result = await db.execute(query)
    rows = result.all()  # retorna lista de tuplas (codigo, estoque_seguranca)

    # transformar em lista de dicts
    return [{"codigo": r[0], "estoque_seguranca": r[1]} for r in rows]

@router.get("/ver-catalogo", response_model=List[CatalogoResponse])
async def ver_catalogo(db: AsyncSession = Depends(get_db)):

    query = (
        select(
            DimProduto.codigo,
            DimProduto.nome_basico,
            DimProduto.nome_modificador,
            DimProduto.descricao_tecnica,
            DimProduto.fabricante,
            DimProduto.observacoes_adicional,
            DimProduto.imagem,
            DimProduto.unidade,
            DimProduto.preco_de_venda,
            case(
                (DimProduto.fragilidade == True, literal("SIM")),
                else_=literal("NÃO")
            ).label('fragilidade'),
            DimProduto.inserido_por,
            DimProduto.rua,
            DimProduto.coluna,
            DimProduto.andar,
            DimProduto.altura,
            DimProduto.largura,
            DimProduto.profundidade,
            DimProduto.peso,
            EstoqueReal.quantidade
        )
        .outerjoin(EstoqueReal, EstoqueReal.codigo == DimProduto.codigo)
    )

    result = await db.execute(query)
    rows = result.mappings().all()  # <-- retorna dict-like ao invés de tupla

    response = []
    for row in rows:
        produto_dict = dict(row)  # converte para dict normal
        if produto_dict.get("imagem"):
            # Converte bytea em base64 (se for bytes)
            if isinstance(produto_dict["imagem"], (bytes, bytearray)):
                produto_dict["imagem"] = base64.b64encode(produto_dict["imagem"]).decode("utf-8")
        response.append(produto_dict)

    return response