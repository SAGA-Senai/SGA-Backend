from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class DimCategoria(Base):
    __tablename__ = "dimcategoria"

    idcategoria: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    categoria: Mapped[str] = mapped_column(String(255), nullable=False)

    prodcategorias: Mapped["FactCategoria"] = relationship(back_populates="categoria")

class FactCategoria(Base):
    __tablename__ = "factcategoria"

    idcategoriaproduto: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    codigo: Mapped[int] = mapped_column(Integer, ForeignKey("dimproduto.codigo"), nullable=False)
    idcategoria: Mapped[int] = mapped_column(Integer, ForeignKey("dimcategoria.idcategoria"), nullable=False)

    categoria: Mapped["DimCategoria"] = relationship(back_populates="prodcategorias")