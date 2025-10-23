from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_professor,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    CreateUserRequest,
    UserResponse
)
from app.models.usuario import DimUsuario
from app.models.professor import DimProfessor

router = APIRouter(tags=["Autenticação"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    email = request.email
    senha = request.senha
    
    result_professor = await db.execute(
        select(DimProfessor).where(DimProfessor.email == email)
    )
    professor = result_professor.scalars().first()
    
    if professor and verify_password(senha, professor.senha):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": professor.email, "tipo_usuario": "professor"},
            expires_delta=access_token_expires
        )
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            tipo_usuario="professor",
            email=professor.email
        )
    
    result_user = await db.execute(
        select(DimUsuario).where(DimUsuario.email == email)
    )
    usuario = result_user.scalars().first()
    
    if usuario and verify_password(senha, usuario.senha):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": usuario.email, "tipo_usuario": "usuario"},
            expires_delta=access_token_expires
        )
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            tipo_usuario="usuario",
            email=usuario.email
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha inválidos"
    )


@router.post("/usuarios", response_model=UserResponse)
async def create_user(
    data: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_professor)
):
    query = select(DimUsuario).where(DimUsuario.email == data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado no sistema."
        )
    
    hashed_password = get_password_hash(data.senha)
    
    new_user = DimUsuario(
        nome=data.nome,
        email=data.email,
        senha=hashed_password,
        datanasc=data.datanasc,
        dataentrada=data.dataentrada,
        inserido_por=current_user["email"]
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        idusuario=new_user.idusuario,
        nome=new_user.nome,
        email=new_user.email,
        datanasc=new_user.datanasc,
        dataentrada=new_user.dataentrada,
        inserido_por=new_user.inserido_por
    )
