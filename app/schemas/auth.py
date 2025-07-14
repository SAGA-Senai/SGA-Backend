from pydantic import BaseModel, EmailStr
from datetime import date

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class LoginResponse(BaseModel):
    idusuario: int
    nome: str
    email: str

class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    datanasc: date | None = None
    dataentrada: date | None = None