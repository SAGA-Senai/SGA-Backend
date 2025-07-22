from sqlalchemy import String, LargeBinary, Numeric, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class DimProduto(Base):
    __tablename__ = "dimproduto"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome_basico: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_modificador: Mapped[str | None] = mapped_column(String(255), nullable=True)
    descricao_tecnica: Mapped[str | None] = mapped_column(nullable=True)
    fabricante: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacoes_adicional: Mapped[str | None] = mapped_column(nullable=True)
    imagem: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preco_de_venda: Mapped[float | None] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    fragilidade: Mapped[bool] = mapped_column(Boolean, nullable=False)
    inserido_por: Mapped[str] = mapped_column(String(255), nullable=False)
    rua: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coluna: Mapped[int | None] = mapped_column(Integer, nullable=True)
    andar: Mapped[int | None] = mapped_column(Integer, nullable=True)
    altura: Mapped[float | None] = mapped_column(Float, nullable=True)
    largura: Mapped[float | None] = mapped_column(Float, nullable=True)
    profundidade: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relacionamento
    recebimentos: Mapped[list["FactRecebimento"]] = relationship(back_populates="produto")
    saidas: Mapped[list["FactSaida"]] = relationship(back_populates="produto")