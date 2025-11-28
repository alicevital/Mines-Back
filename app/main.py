from fastapi import FastAPI

from app.controllers.game_start_controller import GameRouter
from app.controllers.game_ws_controller import WebSocketRouter
from app.controllers.user_controller import UserRouter
from app.controllers.wallets_controllers import WalletRouter


app = FastAPI(title="Mines Academy")

app.include_router(UserRouter)
app.include_router(WalletRouter)
app.include_router(WebSocketRouter)
app.include_router(GameRouter)

print("Loaded at port 8000")