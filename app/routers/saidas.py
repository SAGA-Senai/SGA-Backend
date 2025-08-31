from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models import DimProduto, FactRecebimento, FactSaida
from app.schemas.saidas import SaidaResponse, AddSaidaRequest, AddSaidaResponse, FornecedoresResponse, LotesResponse
import base64

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/saidas", response_model=SaidaResponse)
async def issue(db: AsyncSession = Depends(get_db)):
    # Query com ORM
    query = (
        select(
            DimProduto.codigo,
            DimProduto.nome_basico,
            DimProduto.fabricante,
            FactSaida.fornecedor,
            FactRecebimento.preco_de_aquisicao,
            DimProduto.imagem,
            FactSaida.quant,
            func.to_char(FactSaida.data_saida, 'DD/MM/YYYY').label('data_saida'),
            FactRecebimento.lote,
            func.to_char(FactRecebimento.validade, 'DD/MM/YYYY').label('validade'),
            DimProduto.preco_de_venda,
            DimProduto.fragilidade
        )
        .join(DimProduto, FactSaida.codigo == DimProduto.codigo)
        .join(FactRecebimento, 
            (FactSaida.codigo == FactRecebimento.codigo) &
            (FactSaida.lote == FactRecebimento.lote))
    )

    try:
        result = await db.execute(query)
        saidas = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha em buscar saídas no banco de dados")
    
    # transforma em uma lista para evitar erro do pydantic
    dados = []
    for saida in saidas:
        row = dict(saida)
        if row.get('imagem') and isinstance(row.get('imagem'), (bytes, bytearray)):
            row['imagem'] =  base64.b64encode(row["imagem"]).decode("utf-8")
        row['fragilidade'] = 'SIM' if row['fragilidade'] else 'NÃO'
        dados.append(row)

    return SaidaResponse(
        dados=dados
    )

@router.get("/saidas/{codigo}", response_model=SaidaResponse)
async def issue(codigo: int, db: AsyncSession = Depends(get_db)):
    # Query com ORM
    query = (
        select(
            DimProduto.codigo,
            DimProduto.nome_basico,
            DimProduto.fabricante,
            FactSaida.fornecedor,
            FactRecebimento.preco_de_aquisicao,
            DimProduto.imagem,
            FactSaida.quant,
            func.to_char(FactSaida.data_saida, 'DD/MM/YYYY').label('data_saida'),
            FactRecebimento.lote,
            func.to_char(FactRecebimento.validade, 'DD/MM/YYYY').label('validade'),
            DimProduto.preco_de_venda,
            DimProduto.fragilidade
        )
        .join(DimProduto, FactSaida.codigo == DimProduto.codigo)
        .join(FactRecebimento, 
            (FactSaida.codigo == FactRecebimento.codigo) &
            (FactSaida.lote == FactRecebimento.lote))
        .where(FactSaida.codigo == codigo)
    )

    try:
        result = await db.execute(query)
        saidas = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha em buscar saídas no banco de dados")

    # para Evitar erro do pydantic e transformar decimal em float
    dados = []
    for saida in saidas:
        row = dict(saida)
        if row.get('imagem') and isinstance(row.get('imagem'), (bytes, bytearray)):
            row['imagem'] =  base64.b64encode(row["imagem"]).decode("utf-8")
        row['fragilidade'] = 'SIM' if row['fragilidade'] else 'NÃO'
        dados.append(row)

    return SaidaResponse(
        dados=dados
    )

@router.post("/adicionar-saida", response_model=AddSaidaResponse)
async def add_issue(data: AddSaidaRequest, db: AsyncSession = Depends(get_db)):   
    # utilização de subqueries para evitar duplicação de colunas
    # subquery de recebimentos
    recebimentos_subq = (
        select(func.coalesce(func.sum(FactRecebimento.quant), 0))
        .where(
            FactRecebimento.codigo == data.codigo,
            FactRecebimento.lote == data.numbLote,
            FactRecebimento.fornecedor == data.fornecedor
        )
    ).scalar_subquery()

    # subquery de saídas
    saidas_subq = (
        select(func.coalesce(func.sum(FactSaida.quant), 0))
        .where(
            FactSaida.codigo == data.codigo,
            FactSaida.lote == data.numbLote,
            FactSaida.fornecedor == data.fornecedor
        )
    ).scalar_subquery()

    # query final
    query = select((recebimentos_subq - saidas_subq).label("EstoqueDisponivel"))

    try: 
        result = await db.execute(query)
        quantidade_disponivel = result.scalar() or 0
        quantidade_disponivel = int(quantidade_disponivel) # transforma para fazer comparação

        if quantidade_disponivel < data.quantidade:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantidade no estoque insuficiente")

        # Adicionando saída no banco de dados
        new_issue = FactSaida(
            data_saida=data.data_saida,
            quant=data.quantidade,
            codigo=data.codigo,
            lote=data.numbLote,
            fornecedor=data.fornecedor
        )

        db.add(new_issue)
        await db.commit()
        await db.refresh(new_issue)
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao adicionar saída")

    return AddSaidaResponse(
        message="Saída adicionada com sucesso!"
    )

@router.get("/fornecedores/{codigo}", response_model=FornecedoresResponse)
async def fornecedores(codigo: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(FactRecebimento.fornecedor)
        .distinct()
        .where(FactRecebimento.codigo == codigo)
    )

    try:
        result = await db.execute(query)
        fornecedores = result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar fornecedores: " + str(e))

    if len(fornecedores) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Fornecedor não encontrado para o codigo {codigo}')

    dados = [{
        "id": row,
        "nome": row
    } for row in fornecedores]

    return FornecedoresResponse(
        dados=dados
    )

@router.get("/lotes/", response_model=LotesResponse)
async def lotes(fornecedor: str | None = None, codigo: int | None = None, db: AsyncSession = Depends(get_db)):
    # utilização de subqueries para evitar duplicação de colunas
    # subquery de recebimentos
    recebimentos_subq = (
        select(func.coalesce(func.sum(FactRecebimento.quant), 0))
        .where(
            FactRecebimento.codigo == codigo,
            FactRecebimento.fornecedor == fornecedor
        )
    ).scalar_subquery()

    # subquery de saídas
    saidas_subq = (
        select(func.coalesce(func.sum(FactSaida.quant), 0))
        .where(
            FactSaida.codigo == codigo,
            FactSaida.fornecedor == fornecedor
        )
    ).scalar_subquery()

    # query final
    query = (
        select(
            (recebimentos_subq - saidas_subq).label("EstoqueDisponivel"),
            FactRecebimento.lote
        )
        .group_by(
            FactRecebimento.lote
        )
        .where(
            FactRecebimento.codigo == codigo,
            FactRecebimento.fornecedor == fornecedor
        )
    )
    
    try:
        result = await db.execute(query)
        query_result = result.mappings().all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao buscar lotes: {str(e)}")
    
    dados = [{
        "id": row.lote,
        "codigo": codigo,
        "lote": row.lote,
        "fornecedor": fornecedor,
        "estoqueDisponivel": row.EstoqueDisponivel
    } for row in query_result]

    return LotesResponse(
        dados=dados
    )