from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt
from app.core.database import SessionLocal
from app.models.usuario import DimUsuario
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.auth import RegisterRequest 
from app.routers.tokens import create_access_token, verify_token

router = APIRouter()
# para proteção
security = HTTPBearer()

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

    payload = {"sub": str(user.idusuario), "email": data.email} # payload do JWT sem exp (expiration time)
    token = create_access_token(payload)

    return LoginResponse(
        idusuario=user.idusuario,
        nome=user.nome,
        email=user.email,
        token=token
    )

# Verificar o usuário com o token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
    return payload

@router.get("/me")
async def me(user = Depends(get_current_user)):
    return {"user": user}


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
