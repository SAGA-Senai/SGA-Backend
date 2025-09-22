from sqlalchemy import String, Date, BigInteger, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import date

class FactRecebimento(Base):
    __tablename__ = "factrecebimento"

    idrecebimento: Mapped[int] = mapped_column(primary_key=True)
    data_receb: Mapped[date] = mapped_column(Date, nullable=False)
    quant: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # codigo: Mapped[int] = mapped_column(Integer, nullable=False)
    codigo: Mapped[int] = mapped_column(ForeignKey("dimproduto.codigo", ondelete="CASCADE"), nullable=False)
    validade: Mapped[date] = mapped_column(Date, nullable=True)
    preco_de_aquisicao: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    lote: Mapped[str] = mapped_column(String(30), nullable=False)
    fornecedor: Mapped[str | None] = mapped_column(String(255), nullable=True)