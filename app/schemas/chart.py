from pydantic import BaseModel
from typing import Optional

class ChartResponse(BaseModel):
    categories: list
    values: list
    receipts: list
    issues: list
    days: list