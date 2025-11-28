from fastapi import FastAPI
from app.controllers.game_config_controller import GameConfigRouter

app = FastAPI(title="Mines Academy")

app.include_router(GameConfigRouter)

print("Loaded at port 8000")

