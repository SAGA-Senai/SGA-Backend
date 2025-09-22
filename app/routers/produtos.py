from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.models.produto import DimProduto
from app.core.database import get_db
from app.models.categoria import FactCategoria

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
    categorias: str = Form(...),
    imagem: Union[UploadFile, str, None] = File(None),
    db: AsyncSession = Depends(get_db)
):
    # trata imagem
    if isinstance(imagem, str) or imagem is None:
        imagem_bytes = None
    else:
        imagem_bytes = await imagem.read()
    
    try:
        lista_categorias: List[int] = [int(c.strip()) for c in categorias.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="Formato invÃ¡lido para categorias. Use: 1,2,3")

    # insere produto
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

        for id_categoria in lista_categorias:
            stmt_categoria = insert(FactCategoria).values(
                codigo=codigo,
                idcategoria=id_categoria
            )
            await db.execute(stmt_categoria)

        await db.commit()
        return {"success": True, "message": "Produto cadastrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))