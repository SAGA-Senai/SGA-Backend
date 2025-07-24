from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, outerjoin
from sqlalchemy.orm import joinedload
from passlib.hash import bcrypt
from app.core.database import SessionLocal
from app.models.usuario import DimUsuario
from app.models import DimProduto, FactSaida, FactRecebimento
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.auth import RegisterRequest
from app.schemas.auth import DataResponse
from app.schemas.auth import AddReceiptRequest, AddReceiptResponse
from app.schemas.auth import AddSaidaRequest, AddSaidaResponse



router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/login", response_model=LoginResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    query = select(DimUsuario).where(DimUsuario.email == data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not bcrypt.verify(data.senha, user.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    return LoginResponse(
        idusuario=user.idusuario,
        nome=user.nome,
        email=user.email
    )


@router.post("/register", response_model=LoginResponse)
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 1. Verificar se o e-mail já existe
    query = select(DimUsuario).where(DimUsuario.email == data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email já registrado.")

    # 2. Criar novo usuário com senha criptografada
    hashed_password = bcrypt.hash(data.senha)
    new_user = DimUsuario(
        nome=data.nome,
        email=data.email,
        senha=hashed_password,
        datanasc=data.datanasc,
        dataentrada=data.dataentrada,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return LoginResponse(
        idusuario=new_user.idusuario,
        nome=new_user.nome,
        email=new_user.email
    )

@router.get("/recebimento", response_model=DataResponse)
async def recebimento(db: AsyncSession = Depends(get_db), codigo: Optional[int] = None):
    try:
        if codigo:
            query = (
            select(FactRecebimento)
            .options(joinedload(FactRecebimento.produto))  # Faz o JOIN
            .where(FactRecebimento.codigo == codigo)
            )
        else:
            query = (
                select(FactRecebimento)
                .options(joinedload(FactRecebimento.produto))  # Faz o JOIN
            )

        result = await db.execute(query)
        recebimentos = result.scalars().all()
    except Exception as e:
        print("erro:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, DETAIL="Erro interno, por favor tente novamente mais tarde")

    # Converter para JSON
    dados = []
    for rec in recebimentos:
        dados.append({
            "DATA_RECEB": rec.data_receb.strftime("%d/%m/%Y") if rec.data_receb else None,
            "CODIGO": rec.produto.codigo,
            "NOME_BASICO": rec.produto.nome_basico,
            "FABRICANTE": rec.produto.fabricante,
            "FORNECEDOR": rec.fornecedor,
            "PRECO_DE_AQUISICAO": rec.preco_de_aquisicao,
            "IMAGEM": rec.produto.imagem,
            "QUANT": rec.quant,
            "LOTE": rec.lote,
            "VALIDADE": rec.validade.strftime("%d/%m/%Y") if rec.validade else None,
            "PRECO_DE_VENDA": rec.produto.preco_de_venda,
            "FRAGILIDADE": rec.produto.fragilidade
        })

    return DataResponse(
        dados=dados
    )

# apenas com get e path parameter
@router.get("/recebimento/{codigo}", response_model=DataResponse)
async def recebimento(codigo: int, db: AsyncSession = Depends(get_db)):
    try:
        query = (
        select(FactRecebimento)
        .options(joinedload(FactRecebimento.produto))  # Faz o JOIN
        .where(FactRecebimento.codigo == codigo) # filtra pelo código
        )

        result = await db.execute(query)
        recebimentos = result.scalars().all()
    except Exception as e:
        print("erro:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno, por favor tente novamente mais tarde")

    # Converter para JSON
    dados = []
    for rec in recebimentos:
        dados.append({
            "DATA_RECEB": rec.data_receb.strftime("%d/%m/%Y") if rec.data_receb else None,
            "CODIGO": rec.produto.codigo,
            "NOME_BASICO": rec.produto.nome_basico,
            "FABRICANTE": rec.produto.fabricante,
            "FORNECEDOR": rec.fornecedor,
            "PRECO_DE_AQUISICAO": rec.preco_de_aquisicao,
            "IMAGEM": rec.produto.imagem,
            "QUANT": rec.quant,
            "LOTE": rec.lote,
            "VALIDADE": rec.validade.strftime("%d/%m/%Y") if rec.validade else None,
            "PRECO_DE_VENDA": rec.produto.preco_de_venda,
            "FRAGILIDADE": rec.produto.fragilidade
        })

    return DataResponse(
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

#     return DataResponse(
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

@router.get("/saidas", response_model=DataResponse)
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
        .join(FactRecebimento, FactSaida.codigo == FactRecebimento.codigo)
    )

    try:
        result = await db.execute(query)
        saidas = result.mappings().all()
    except Exception as e:
        print('erro:', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha em buscar saídas no banco de dados")
    
    # transforma em uma lista para evitar erro do pydantic
    dados = []
    for row in saidas:
        dados.append({
            "codigo": row.codigo,
            "nome_basico": row.nome_basico,
            "fabricante": row.fabricante,
            "fornecedor": row.fornecedor,
            "preco_de_aquisicao": float(row.preco_de_aquisicao),
            "imagem": row.imagem,
            "quant": row.quant,
            "data_saida": row.data_saida,
            "lote": row.lote,
            "validade": row.validade    ,
            "preco_de_venda": float(row.preco_de_venda),
            "fragilidade": row.fragilidade
        })

    return DataResponse(
        dados=dados
    )

@router.get("/saidas/{codigo}", response_model=DataResponse)
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
        .join(FactRecebimento, FactSaida.codigo == FactRecebimento.codigo)
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
    for row in saidas:
        dados.append({
            "codigo": row["codigo"],
            "nome_basico": row["nome_basico"],
            "fabricante": row["fabricante"],
            "fornecedor": row["fornecedor"],
            "preco_de_aquisicao": float(row["preco_de_aquisicao"]),
            "imagem": row["imagem"],
            "quant": row["quant"],
            "data_saida": row["data_saida"],
            "lote": row["lote"],
            "validade": row["validade"],
            "preco_de_venda": float(row["preco_de_venda"]),
            "fragilidade": row["fragilidade"]
        })

    return DataResponse(
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

@router.get("/saldos", response_model=DataResponse)
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

    return DataResponse(
        dados=dados
    )    

@router.get("/saldos/{codigo}", response_model=DataResponse)
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

    return DataResponse(
        dados=dados
    )    

@router.get("/fornecedores/{codigo}", response_model=DataResponse)
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

    return DataResponse(
        dados=dados
    )

@router.get("/lotes/", response_model=DataResponse)
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

    return DataResponse(
        dados=dados
    )







