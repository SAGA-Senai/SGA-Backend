from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProdutoCreate(BaseModel):
    codigo: int
    nome_basico: str
    nome_modificador: str
    descricao_tecnica: Optional[str] = None
    fabricante: Optional[str] = None
    unidade: Optional[str] = None
    preco_de_venda: float
    fragilidade: bool
    rua: int
    coluna: int
    andar: int
    altura: float
    largura: float
    profundidade: float
    peso: float
    observacoes_adicional: Optional[str] = None
    imagem: Optional[bytes] = None
    inserido_por: str
