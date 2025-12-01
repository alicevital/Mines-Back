from pydantic import BaseModel


class GameStepRequest(BaseModel):
    match_id: str
    cell: int


class GameStepResponse(BaseModel):
    event: str

