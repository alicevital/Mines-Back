from fastapi import APIRouter, WebSocket
import json

from app.database.db import get_database
from app.core.config import RABBITMQ_URI

from app.repositories.match_repository import MatchRepository
from app.repositories.wallets_repository import WalletRepository

from app.utils.dispatcher import active_connections
from app.utils.rabbitmq import RabbitMQPublisher

from app.services.game_services import GameService
from app.services.game_steps_service import GameStepService
from app.services.game_stop_service import GameStopService



db = get_database()
match_repo = MatchRepository(db["matches"])
wallet_repo = WalletRepository(db)
rabbit = RabbitMQPublisher(RABBITMQ_URI)

game_start_service = GameService(match_repo, wallet_repo, rabbit)
game_step_service = GameStepService(match_repo, rabbit, wallet_repo)
game_stop_service = GameStopService(match_repo, wallet_repo, rabbit)


WebSocketRouter = APIRouter()


async def process_events_ws(event: str, data: dict):

    if event == "GAME_START":
        await game_start_service.start_game(
            user_id=data.get("user_id"),
            bet_amount=data.get("bet_amount"),
            total_mines=data.get("total_mines")
        )

    elif event == "GAME_STEP":
        await game_step_service.step_in_game(
            cell=data["cell"],
            matches_id=data["match_id"]
        )

    elif event == "GAME_CASHOUT":
        await game_stop_service.stop_game(
            match_id=data["match_id"]
        )

    return {"error": "Evento inválido"}


@WebSocketRouter.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):

    '''Função que gerencia a conexão, processa o evento e fecha a conexão após isso'''

    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
          
            raw = await websocket.receive_text()

            try:
                msg = json.loads(raw)
                event = msg.get("event")
                data = msg.get("data", {})

                # Processa o evento
                await process_events_ws(event, data)


            except Exception as e:
                await websocket.send_json({
                    "event": "Error",
                    "message": str(e)
                })

    except:
      
        ws = active_connections.get(user_id)
        if ws:
            try:
                await ws.close()
            except:
                pass
        
        active_connections.pop(user_id, None)