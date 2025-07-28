from pydantic import BaseModel

class SaldosResponse(BaseModel):
    dados: list
    