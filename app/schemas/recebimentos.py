from pydantic import BaseModel
from datetime import date
from typing import Optional

# necessário apenas se o método post de Recebimentos for usado
# class Receiverequest(BaseModel):
#     codigo: int

class AddReceiptRequest(BaseModel):
    data_receb: date
    quant: int
    codigo: int
    validade: Optional[date] # <--- Precisa ser opcional para aceitar null
    preco_de_aquisicao: float
    lote: str
    fornecedor: str | None

class AddReceiptResponse(BaseModel):
    message: str | None

class ReceiptResponse(BaseModel):
    dados: list