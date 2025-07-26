from sqlalchemy import Column, BigInteger, String
from app.core.database import Base

class DimProfessor(Base):
    __tablename__ = "dimprofessor"

    sn = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
