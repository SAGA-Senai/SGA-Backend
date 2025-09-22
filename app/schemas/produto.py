from pydantic import BaseModel, ConfigDict
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

# RESPOSTA DE VER PRODUTOS  # < --- MEU
class ProdutoResponse(BaseModel):
    codigo: int
    nome_basico: str
    nome_modificador: str
    descricao_tecnica: Optional[str]
    fabricante: Optional[str]
    unidade: Optional[str]
    preco_de_venda: float
    fragilidade: bool
    rua: int
    coluna: int
    andar: int
    altura: float
    largura: float
    profundidade: float
    peso: float
    observacoes_adicional: Optional[str]
    inserido_por: str
    imagem: Optional[str]  # agora base64

    class Config:
        orm_mode = True

# DELETAR
class ProdutoDelete(BaseModel):
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
    # imagem: Optional[bytes] = None
    inserido_por: str

# EDITAR
class ProdutoPatch(BaseModel):
    nome_basico: Optional[str] = None
    nome_modificador: Optional[str] = None
    descricao_tecnica: Optional[str] = None
    fabricante: Optional[str] = None
    unidade: Optional[str] = None
    preco_de_venda: Optional[float] = None
    fragilidade: Optional[bool] = None
    rua: Optional[int] = None
    coluna: Optional[int] = None
    andar: Optional[int] = None
    altura: Optional[float] = None
    largura: Optional[float] = None
    profundidade: Optional[float] = None
    peso: Optional[float] = None
    observacoes_adicional: Optional[str] = None
    imagem: Optional[bytes] = None
    inserido_por: Optional[str] = None

# RESPOSTA DO LOTE DE EDIÇÃO

class LoteResponse(BaseModel):
    lote: str
    fornecedor: str
    validade: Optional[date] = None

# EDITAR LOTE  
class LotePatch(BaseModel):
    validade: Optional[date] = None
    fornecedor: Optional[str] = None