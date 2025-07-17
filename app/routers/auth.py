from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from passlib.hash import bcrypt
from app.core.database import SessionLocal
from app.models.usuario import DimUsuario
from app.models.produto import DimProduto
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.auth import RegisterRequest 
from app.schemas.auth import AddProductRequest, AddProductResponse

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

# @router.post("/Recebimento")
# async def recebimento(data)


@router.post("/adicionar-produto", response_model=AddProductResponse)
async def add_product(data: AddProductRequest, db: AsyncSession = Depends(get_db)):
    # checa se o id já existe
    query = select(DimProduto).where(DimProduto.codigo == data.codigo)
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    
    if product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Produto com código: {data.codigo}, já existe")

    new_product = DimProduto(
        codigo=data.codigo,
        nome_basico=data.nome_basico,
        nome_modificador=(data.nome_modificador or None),
        descricao_tecnica=(data.descricao_tecnica or None),
        fabricante=(data.fabricante or None),
        observacoes_adicional=(data.observacoes_adicional or None),
        imagem=data.imagem,  # precisa garantir que é bytes se for bytea
        unidade=(data.unidade or None),
        preco_de_venda=(data.preco_de_venda or None),
        fragilidade=(data.fragilidade or None),
        inserido_por=data.inserido_por,
        rua=(data.rua or None),
        coluna=(data.coluna or None),
        andar=(data.andar or None),
        largura=(data.largura or None),
        profundidade=(data.profundidade or None),
        peso=(data.peso or None)
    )

    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar produto: {str(e)}"
        )

    return AddProductResponse(
        status_code=200,
        message="Produto adicionado com sucesso",
    )