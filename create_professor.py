"""
Script para criar um professor inicial no banco de dados.
Execute: python create_professor.py
"""

import asyncio
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.professor import DimProfessor
from app.core.security import get_password_hash


async def create_initial_professor():
    async with SessionLocal() as db:
        email = "professor@exemplo.com"
        senha_plain = "senha123"
        
        result = await db.execute(
            select(DimProfessor).where(DimProfessor.email == email)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"❌ Professor com email {email} já existe!")
            return
        
        professor = DimProfessor(
            nome="Professor Inicial",
            email=email,
            senha=get_password_hash(senha_plain)
        )
        
        db.add(professor)
        await db.commit()
        await db.refresh(professor)
        
        print(f"✅ Professor criado com sucesso!")
        print(f"   Email: {email}")
        print(f"   Senha: {senha_plain}")
        print(f"   SN: {professor.sn}")


if __name__ == "__main__":
    print("🚀 Criando professor inicial...")
    asyncio.run(create_initial_professor())
