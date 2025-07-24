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

# necessário apenas se o método post de Recebimentos for usado
# class Receiverequest(BaseModel):
#     codigo: int

class AddReceiptRequest(BaseModel):
    data_receb: date
    quant: int
    codigo: int
    validade: date
    preco_de_aquisicao: float
    lote: str
    fornecedor: str | None

class AddReceiptResponse(BaseModel):
    message: str | None

class AddSaidaRequest(BaseModel):
    fornecedor: str
    codigo: int
    quantidade: int
    numbLote: str
    data_saida: date
    # inseridoPor: str

class AddSaidaResponse(BaseModel):
    message: str | None

class DataResponse(BaseModel):
    dados: list