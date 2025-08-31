from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models import DimProduto, FactRecebimento, FactCategoria, DimCategoria
from typing import Optional
from app.schemas.recebimentos import AddReceiptRequest, AddReceiptResponse, ReceiptResponse
import base64

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/recebimento", response_model=ReceiptResponse)
async def recebimento(db: AsyncSession = Depends(get_db), codigo: Optional[int] = None):
    try:
        if codigo:
            query = (
            select(
                func.to_char(FactRecebimento.data_receb, 'DD/MM/YYYY').label('data_receb'),
                DimProduto.codigo,
                DimProduto.nome_basico,
                DimProduto.fabricante,
                FactRecebimento.fornecedor,
                FactRecebimento.preco_de_aquisicao,
                DimProduto.imagem,
                FactRecebimento.quant,
                FactRecebimento.lote,
                func.to_char(FactRecebimento.validade, 'DD/MM/YYYY').label('validade'),
                DimProduto.preco_de_venda,
                DimProduto.fragilidade,
                DimCategoria.categoria.label("categoria")
            )
            .select_from(FactRecebimento)
            .join(DimProduto, FactRecebimento.codigo == DimProduto.codigo)
            .outerjoin(FactCategoria, DimProduto.codigo == FactCategoria.codigo)
            .outerjoin(DimCategoria, FactCategoria.idcategoria == DimCategoria.idcategoria)
            .where(FactRecebimento.codigo == codigo)
            )
        else:
            query = (
                select(
                    func.to_char(FactRecebimento.data_receb, 'DD/MM/YYYY').label('data_receb'),
                    DimProduto.codigo,
                    DimProduto.nome_basico,
                    DimProduto.fabricante,
                    FactRecebimento.fornecedor,
                    FactRecebimento.preco_de_aquisicao,
                    DimProduto.imagem,
                    FactRecebimento.quant,
                    FactRecebimento.lote,
                    func.to_char(FactRecebimento.validade, 'DD/MM/YYYY').label('validade'),
                    DimProduto.preco_de_venda,
                    DimProduto.fragilidade,
                    DimCategoria.categoria.label("categoria")
                )
                .select_from(FactRecebimento)
                .join(DimProduto, FactRecebimento.codigo == DimProduto.codigo)
                .outerjoin(FactCategoria, DimProduto.codigo == FactCategoria.codigo)
                .outerjoin(DimCategoria, FactCategoria.idcategoria == DimCategoria.idcategoria)
            )
        
        result = await db.execute(query)
        recebimentos = result.mappings().all()
    except Exception as e:
        print("Erro ao buscar recebimentos:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno, por favor tente novamente mais tarde")

    # Converter para JSON
    dados = []
    for rec in recebimentos:
        row = dict(rec)
        if row.get('imagem') and isinstance(row.get('imagem'), (bytes, bytearray)):
            row['imagem'] =  base64.b64encode(row["imagem"]).decode("utf-8")
        row['fragilidade'] = 'SIM' if row['fragilidade'] else 'NÃO'
        dados.append(row)

    return ReceiptResponse(
        dados=dados
    )

# apenas com get e path parameter
@router.get("/recebimento/{codigo}", response_model=ReceiptResponse)
async def recebimento(codigo: int, db: AsyncSession = Depends(get_db)):
    try:
        query = (
            select(
                func.to_char(FactRecebimento.data_receb, 'DD/MM/YYYY').label('data_receb'),
                DimProduto.codigo,
                DimProduto.nome_basico,
                DimProduto.fabricante,
                FactRecebimento.fornecedor,
                FactRecebimento.preco_de_aquisicao,
                DimProduto.imagem,
                FactRecebimento.quant,
                FactRecebimento.lote,
                func.to_char(FactRecebimento.validade, 'DD/MM/YYYY').label('validade'),
                DimProduto.preco_de_venda,
                DimProduto.fragilidade,
                DimCategoria.categoria.label("categoria")
            )
            .select_from(FactRecebimento)
            .join(DimProduto, FactRecebimento.codigo == DimProduto.codigo)
            .outerjoin(FactCategoria, DimProduto.codigo == FactCategoria.codigo)
            .outerjoin(DimCategoria, FactCategoria.idcategoria == DimCategoria.idcategoria)
            .where(FactRecebimento.codigo == codigo)
        )

        result = await db.execute(query)
        recebimentos = result.mappings().all()
        print("Recebimentos encontrados:", recebimentos)
    except Exception as e:
        print("erro:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno, por favor tente novamente mais tarde")

    # Converter para JSON
    dados = []
    for rec in recebimentos:
        row = dict(rec)
        if row.get('imagem') and isinstance(row.get('imagem'), (bytes, bytearray)):
            row['imagem'] =  base64.b64encode(row["imagem"]).decode("utf-8")
            row['fragilidade'] = 'SIM' if row['fragilidade'] else 'NÃO'
        dados.append(row)

    return ReceiptResponse(
        dados=dados
    )

# com o método post
# @router.post("/Recebimento", response_model=ReceiveResponse)
# async def recebimento(data: Receiverequest, db: AsyncSession = Depends(get_db)):
#     try:
#         query = (
#             select(FactRecebimento)
#             .options(joinedload(FactRecebimento.produto))  # Faz o JOIN
#             .where(FactRecebimento.codigo == data.codigo)
#         )
#         result = await db.execute(query)
#         recebimentos = result.scalars().all()

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno, por favor tente novamente mais tarde")

#     # Converter para JSON
#     dados = []
#     for rec in recebimentos:
#         dados.append({ # separa os dados desjados para a resposta
#             "DATA_RECEB": rec.data_receb.strftime("%d/%m/%Y") if rec.data_receb else None,
#             "CODIGO": rec.produto.codigo,
#             "NOME_BASICO": rec.produto.nome_basico,
#             "FABRICANTE": rec.produto.fabricante,
#             "FORNECEDOR": rec.fornecedor,
#             "PRECO_DE_AQUISICAO": rec.preco_de_aquisicao,
#             "IMAGEM": rec.produto.imagem,
#             "QUANT": rec.quant,
#             "LOTE": rec.lote,
#             "VALIDADE": rec.validade.strftime("%d/%m/%Y") if rec.validade else None,
#             "PRECO_DE_VENDA": rec.produto.preco_de_venda,
#             "FRAGILIDADE": rec.produto.fragilidade
#         })

#     return ReceiptResponse(
#         dados=dados
#     )

@router.post("/adicionar-recebimento", response_model=AddReceiptResponse)
async def add_receipt(data: AddReceiptRequest, db: AsyncSession = Depends(get_db)):
    #checa se o código existe
    query = select(DimProduto).where(DimProduto.codigo == data.codigo)

    try:
        result = await db.execute(query)
        result_data = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no banco de dados. Erro: {e}")
    
    if not result_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Produto com código: {data.codigo} não encontrado.")

    new_receipt = FactRecebimento(
        data_receb=data.data_receb,
        quant=data.quant,
        codigo=data.codigo,
        validade=data.validade,
        preco_de_aquisicao=data.preco_de_aquisicao,
        lote=data.lote,
        fornecedor=data.fornecedor
    )

    try:
        db.add(new_receipt)
        await db.commit()
        await db.refresh(new_receipt)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao adicionar produto no banco de dados. Erro: {e}")
    
    return AddReceiptResponse(
        message="Recebimento adicionado com sucesso!"
    )
