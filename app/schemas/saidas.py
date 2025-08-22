from pydantic import BaseModel
from datetime import date

class AddSaidaRequest(BaseModel):
    fornecedor: str
    codigo: int
    quantidade: int
    numbLote: str
    data_saida: date
    # inseridoPor: str

class AddSaidaResponse(BaseModel):
    message: str | None

class SaidaResponse(BaseModel):
    dados: list

class FornecedoresResponse(BaseModel):
    dados: list

class LotesResponse(BaseModel):
    dados: list

class EstoqueSeguranca(BaseModel):
    codigo: int
    estoque_seguranca: float