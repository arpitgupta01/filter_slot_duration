from pydantic import BaseModel
from typing import Optional

class Data(BaseModel):
    customer_id : int
    center_id : int
    utterance : Optional[str]

    class Config:
        orm_mode = True