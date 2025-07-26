from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from app.models.produto import DimProduto
from app.core.database import get_db

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
    imagem: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    imagem_bytes = await imagem.read() if imagem else None

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
