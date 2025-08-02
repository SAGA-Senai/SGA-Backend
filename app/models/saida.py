from sqlalchemy import String, Date, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import date

class FactSaida(Base):
    __tablename__ = "factsaidas"

    idrecebimento: Mapped[int] = mapped_column(primary_key=True)
    data_saida: Mapped[date] = mapped_column(Date, nullable=False)
    quant: Mapped[date] = mapped_column(BigInteger, nullable=False)
    lote: Mapped[str] = mapped_column(String(30), nullable=False)
    codigo: Mapped[int] = mapped_column(Integer, nullable=False)
    fornecedor: Mapped[str] = mapped_column(String, nullable=True)
