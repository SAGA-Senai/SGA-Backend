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

class AddProductRequest(BaseModel):
    codigo: int
    nome_basico: str
    nome_modificador: str | None
    descricao_tecnica: str | None
    fabricante: str
    observacoes_adicional: str | None
    imagem: bytes | None
    unidade: str
    preco_de_venda: float | None
    fragilidade: float | None
    inserido_por: str
    rua: int | None    
    coluna: int | None
    andar: int | None
    altura: float | None
    largura: float | None
    profundidade: float | None
    peso: float | None

class AddProductResponse(BaseModel):
    status_code: int
    message: str | None

# necessário apenas se o método post de Recebimentos for usado
# class Receiverequest(BaseModel):
#     codigo: int

class ReceiveResponse(BaseModel):
    status_code: int
    dados: list

class AddReceiptRequest(BaseModel):
    data_receb: date
    quant: int
    codigo: int
    validade: date
    preco_de_aquisicao: float
    lote: str
    fornecedor: str | None

class AddReceiptResponse(BaseModel):
    status_code: int
    mensagem: str