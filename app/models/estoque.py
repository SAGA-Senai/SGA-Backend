from sqlalchemy import Column, Integer, String
from app.core.database import Base

class EstoqueReal(Base):
    __tablename__ = "vw_estoquereal"

    codigo = Column(Integer, primary_key=True)
    nome_basico = Column(String)
    quantidade = Column(Integer)
    quant_recente = Column(Integer)
