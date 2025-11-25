from fastapi import FastAPI
from models.matches_models import MatcheModel

app = FastAPI(title="Mines Academy")

print("Loaded at port 8000")

@app.post("/test")
def test_item(item: MatcheModel):
    return item
