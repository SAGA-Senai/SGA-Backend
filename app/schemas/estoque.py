from pydantic import BaseModel

class EstoqueResponse(BaseModel):
    codigo: int
    nome_basico: str
    quantidade: int
    quant_recente: int
