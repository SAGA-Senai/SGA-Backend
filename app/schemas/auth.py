from pydantic import BaseModel, EmailStr
from datetime import date

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tipo_usuario: str
    email: str

class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    datanasc: date | None = None
    dataentrada: date | None = None

class CreateUserRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    datanasc: date | None = None
    dataentrada: date | None = None

class UserResponse(BaseModel):
    idusuario: int
    nome: str
    email: str
    datanasc: date | None = None
    dataentrada: date | None = None
    inserido_por: str | None = None