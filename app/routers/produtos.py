from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from app.models.produto import DimProduto
from app.core.database import get_db
from fastapi import Body
import base64

from app.schemas.produto import ProdutoResponse, ProdutoDelete, ProdutoPatch
from typing import List, Union

router = APIRouter()

@router.post("/produtos")
async def cadastrar_produto(
    codigo: int = Form(...),
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
    inserido_por: str = Form(...),
    imagem: Union[UploadFile, str, None] = File(None),
    db: AsyncSession = Depends(get_db)
):
    if isinstance(imagem, str) or imagem is None:
        imagem_bytes = None
    else:
        imagem_bytes = await imagem.read()

    stmt = insert(DimProduto).values(
        codigo=codigo,
        nome_basico=nome_basico,
        nome_modificador=nome_modificador,
        descricao_tecnica=descricao_tecnica,
        fabricante=fabricante,
        unidade=unidade,
        preco_de_venda=preco_de_venda,
        fragilidade=fragilidade,
        rua=rua,
        coluna=coluna,
        andar=andar,
        altura=altura,
        largura=largura,
        profundidade=profundidade,
        peso=peso,
        observacoes_adicional=observacoes_adicional,
        imagem=imagem_bytes,
        inserido_por=inserido_por
    )

    try:
        await db.execute(stmt)
        await db.commit()
        return {"success": True, "message": "Produto cadastrado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EDIÇÃO - VER PRODUTOS PROVISORIO 

@router.get("/ver_produtos", response_model=List[ProdutoResponse])
async def ver_produtos(db: AsyncSession = Depends(get_db)):
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


@router.get("/ver_produtos/{codigo}", response_model=ProdutoResponse)
async def ver_produto(codigo: int, db: AsyncSession = Depends(get_db)):
    query = select(DimProduto).where(DimProduto.codigo == codigo)
    result = await db.execute(query)
    produto = result.scalar_one_or_none() 

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    produto_dict = produto.__dict__.copy()
    if produto_dict.get("imagem"):
        produto_dict["imagem"] = base64.b64encode(produto_dict["imagem"]).decode("utf-8")
    
    return ProdutoResponse(**produto_dict)

# DELETE - PRODUTOS

@router.delete("/deletar_produto/{codigo}")
async def deletar_produto(codigo: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DimProduto).where(DimProduto.codigo == codigo))
    produto_deletado = result.scalar_one_or_none()

    if not produto_deletado:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # FAZER MENSAGEM DE AVISO CASO PRODUTO ESTEJA RELACIONADO COM OUTRA TABELA
    # EX.: FactRecebimento

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
    imagem: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(DimProduto).where(DimProduto.codigo == codigo))
    produto = result.scalar_one_or_none()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

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

    await db.commit()
    await db.refresh(produto)
    return {"success": True, "message": "Produto atualizado com sucesso - AEEE"}