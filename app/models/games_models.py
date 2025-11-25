from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GamesModel(BaseModel):

    game_id: Optional[str] = None
    name: str
    is_ative = False
    total_cells = 25
    total_mines = List[int] = Field()
    created_at = datetime
    update_at = datetime

    class Config:
        # Permite que o Pydantic serialize para dict para inserir no Mongo -->
        arbitrary_types_allowed = True
        json_encoders = {str: str}