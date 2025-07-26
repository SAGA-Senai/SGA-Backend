from sqlalchemy import Column, Integer, String, Float, Boolean, LargeBinary
from app.core.database import Base

class DimProduto(Base):
    __tablename__ = "dimproduto"

    codigo = Column(Integer, primary_key=True, index=True)
    nome_basico = Column(String(255), nullable=False)
    nome_modificador = Column(String(255), nullable=False)
    descricao_tecnica = Column(String)
    fabricante = Column(String(255))
    unidade = Column(String(50))
    preco_de_venda = Column(Float)
    fragilidade = Column(Boolean)
    rua = Column(Integer)
    coluna = Column(Integer)
    andar = Column(Integer)
    altura = Column(Float)
    largura = Column(Float)
    profundidade = Column(Float)
    peso = Column(Float)
    observacoes_adicional = Column(String)
    imagem = Column(LargeBinary, nullable=True)
    inserido_por = Column(String(255), nullable=False)
