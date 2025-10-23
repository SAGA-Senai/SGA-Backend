from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from datetime import date 
class DimUsuario(Base):
    __tablename__ = "dimusuario"

    idusuario: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    datanasc: Mapped[date | None] = mapped_column(nullable=True)
    dataentrada: Mapped[date | None] = mapped_column(nullable=True)
    inserido_por: Mapped[str | None] = mapped_column(String(255), nullable=True)     