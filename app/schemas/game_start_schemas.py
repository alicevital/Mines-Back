from pydantic import BaseModel

class GameStartedSchema(BaseModel):
    match_id: str
    user_id: str
    total_cells: int
    total_mines: int