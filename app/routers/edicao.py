from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, and_
from app.models.produto import DimProduto
from app.models.recebimento import FactRecebimento
from app.models.categoria import FactCategoria, DimCategoria
from app.core.database import get_db
from datetime import date
import base64

from app.schemas.produto import ProdutoResponse, ProdutoDelete, LoteResponse
from typing import List, Union, Optional

router = APIRouter()

@router.get("/ver_edicao", response_model=List[ProdutoResponse])
async def ver_produtos_tela_edicao(db: AsyncSession = Depends(get_db)):

    query = select(DimProduto)
    result = await db.execute(query)
    produtos = result.scalars().all()
    
    response = []
    for produto in produtos:
        produto_dict = produto.__dict__.copy()
        if produto_dict.get("imagem"):
            produto_dict["imagem"] = base64.b64encode(produto_dict["imagem"]).decode("utf-8")
        response.append(ProdutoResponse(**produto_dict))
    
    return response

# ----------------------------------------------------------------------------------------------------------

@router.get("/ver_edicao/{codigo}")
async def ver_produto(codigo: int, db: AsyncSession = Depends(get_db)):
    # busca produto
    query_produto = select(DimProduto).where(DimProduto.codigo == codigo)
    result = await db.execute(query_produto)
    produto = result.scalar_one_or_none()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # busca todas as categorias disponíveis
    query_categorias = select(DimCategoria)
    result_categorias = await db.execute(query_categorias)
    todas_categorias = result_categorias.scalars().all()

    # busca categorias já vinculadas ao produto
    query_prod_categorias = (
        select(FactCategoria.idcategoria)
        .where(FactCategoria.codigo == codigo)
    )
    result_prod_categorias = await db.execute(query_prod_categorias)
    categorias_produto = [r[0] for r in result_prod_categorias.all()]

    # prepara retorno
    produto_dict = produto.__dict__.copy()
    if produto_dict.get("imagem"):
        produto_dict["imagem"] = base64.b64encode(produto_dict["imagem"]).decode("utf-8")

    return {
        "produto": produto_dict,
        "todas_categorias": [
            {"idcategoria": c.idcategoria, "categoria": c.categoria}
            for c in todas_categorias
        ],
        "categorias_produto": categorias_produto
    }

@router.get("/ver_edicao/{codigo}/lotes", response_model=List[LoteResponse])
async def ver_lotes_produto(codigo: int, db: AsyncSession = Depends(get_db)):
    query = select(FactRecebimento).where(FactRecebimento.codigo == codigo)
    result = await db.execute(query)
    lotes = result.scalars().all()

    if not lotes:
        raise HTTPException(status_code=404, detail="Nenhum lote encontrado")

    return [
        {"lote": lote.lote, "fornecedor": lote.fornecedor, "data validade": lote.validade}
        for lote in lotes
    ]
 
@router.get("/ver_edicao/{codigo}/lotes/{lote}", response_model=List[LoteResponse])
async def ver_lotes_produto(codigo: int, lote: str, db: AsyncSession = Depends(get_db)):
    query = select(FactRecebimento).where(and_(FactRecebimento.codigo == codigo, FactRecebimento.lote == lote))
    result = await db.execute(query)
    lotes = result.scalars().all()

    if not lotes:
        raise HTTPException(status_code=404, detail="Nenhum lote encontrado")

    return [
        {"lote": lote.lote, "fornecedor": lote.fornecedor, "validade": lote.validade}
        for lote in lotes
    ]

@router.patch("/editar_lote/{codigo}/lotes/{lote}")
async def editar_lote(
    codigo: int,
    lote: str,
    fornecedor: str = Form(...),
    validade: Optional[str] = Form(None),   # <- recebe como string
    db: AsyncSession = Depends(get_db)
):
    if not validade or validade.lower() in ("null", "none"):
        validade_date = None
    else:
        validade_date = date.fromisoformat(validade)

    result = await db.execute(
        select(FactRecebimento).where(
            and_(FactRecebimento.codigo == codigo, FactRecebimento.lote == lote)
        )
    )
    lote = result.scalar_one_or_none()

    if not lote:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    lote.fornecedor = fornecedor
    lote.validade = validade_date   # <- agora é sempre None ou date válido

    await db.commit()
    await db.refresh(lote)
    return {"success": True, "message": "Lote atualizado com sucesso"}

# DELETE - PRODUTOS

@router.delete("/deletar_produto/{codigo}")
async def deletar_produto(codigo: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DimProduto).where(DimProduto.codigo == codigo))
    produto_deletado = result.scalar_one_or_none()

    if not produto_deletado:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
        
    await db.delete(produto_deletado)
    await db.commit()

    return ProdutoDelete(
        codigo=produto_deletado.codigo,
        nome_basico=produto_deletado.nome_basico,
        nome_modificador=produto_deletado.nome_modificador,
        descricao_tecnica=produto_deletado.descricao_tecnica,
        fabricante=produto_deletado.fabricante,
        unidade=produto_deletado.unidade,
        preco_de_venda=produto_deletado.preco_de_venda,
        fragilidade=produto_deletado.fragilidade,
        rua=produto_deletado.rua,
        coluna=produto_deletado.coluna,
        andar=produto_deletado.andar,
        altura=produto_deletado.altura,
        largura=produto_deletado.largura,
        profundidade=produto_deletado.profundidade,
        peso=produto_deletado.peso,
        observacoes_adicional=produto_deletado.observacoes_adicional,
        # imagem=produto_deletado.imagem,
        inserido_por=produto_deletado.inserido_por
    )
 
# EDICAO - PRODUTOS

@router.patch("/editar_produto/{codigo}")
async def editar_produto(
    codigo: int,
    nome_basico: str = Form(...),
    nome_modificador: str = Form(...),
    descricao_tecnica: str = Form(None),
    fabricante: str = Form(None),
    unidade: str = Form(None),
    preco_de_venda: float = Form(...),
    fragilidade: bool = Form(...),
    rua: int = Form(...),
    coluna: int = Form(...),
    andar: int = Form(...),
    altura: float = Form(...),
    largura: float = Form(...),
    profundidade: float = Form(...),
    peso: float = Form(...),
    observacoes_adicional: str = Form(None),
    categorias: str = Form(...),  # <-- recebe várias categorias
    imagem: Union[UploadFile, None] = File(None),
    db: AsyncSession = Depends(get_db)
):
    # Busca o produto
    result = await db.execute(select(DimProduto).where(DimProduto.codigo == codigo))
    produto = result.scalar_one_or_none()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Atualiza os campos básicos
    produto.nome_basico = nome_basico
    produto.nome_modificador = nome_modificador
    produto.descricao_tecnica = descricao_tecnica
    produto.fabricante = fabricante
    produto.unidade = unidade
    produto.preco_de_venda = preco_de_venda
    produto.fragilidade = fragilidade
    produto.rua = rua
    produto.coluna = coluna
    produto.andar = andar
    produto.altura = altura
    produto.largura = largura
    produto.profundidade = profundidade
    produto.peso = peso
    produto.observacoes_adicional = observacoes_adicional

    if imagem:
        produto.imagem = await imagem.read()  # salva como bytes (bytea)

    # --------- Atualizar categorias ---------
    try:
        lista_categorias: List[int] = [int(c.strip()) for c in categorias.split(",") if c.strip()]
    except Exception:
        raise HTTPException(status_code=400, detail="Formato inválido para categorias. Use: 1,2,3")

    # Remove todas as categorias atuais
    await db.execute(delete(FactCategoria).where(FactCategoria.codigo == codigo))

    # Insere as categorias novas
    for id_categoria in lista_categorias:
        stmt_categoria = insert(FactCategoria).values(
            codigo=codigo,
            idcategoria=id_categoria
        )
        await db.execute(stmt_categoria)

    await db.commit()
    await db.refresh(produto)

    return {"success": True, "message": "Produto atualizado com sucesso!"}