from pydantic import BaseModel
from typing import Optional

class EstoqueResponse(BaseModel):
    codigo: int
    nome_basico: str
    quantidade: int
    quant_recente: int

class CatalogoResponse(BaseModel):
    codigo: int
    nome_basico: Optional[str]
    nome_modificador: Optional[str]
    descricao_tecnica: Optional[str]
    fabricante: Optional[str]
    categorias: Optional[str]
    observacoes_adicional: Optional[str]
    imagem: Optional[str]
    unidade: Optional[str]
    preco_de_venda: Optional[float]
    fragilidade: str
    inserido_por: Optional[str]
    rua: Optional[int]
    coluna: Optional[int]
    andar: Optional[int]
    altura: Optional[float]
    largura: Optional[float]
    profundidade: Optional[float]
    peso: Optional[float]
    quantidade: Optional[int]