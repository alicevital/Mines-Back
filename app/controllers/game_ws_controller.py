from fastapi import APIRouter, WebSocket

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


async def process_events_ws(event: str, data: dict, user_id: str):

    if event == "GAME_START":
        await game_start_service.start_game(
            user_id=user_id,
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


@WebSocketRouter.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    '''Função que gerencia a conexão, processa o evento e fecha a conexão após isso'''

    await websocket.accept()
    current_user_id = None

    try:

        try:
            initial_data = await websocket.receive_json()
            current_user_id = initial_data.get("user_id")

            if not current_user_id:
                await websocket.close(code=1008, reason="user id required")
                return
            
            active_connections[current_user_id] = websocket

            if "event" in initial_data:
                event = initial_data.get("event")
                data = initial_data.get("data", {})

                try:
                    await process_events_ws(event, data, user_id=current_user_id)
                except Exception as e:
                    await websocket.send_json({"event": "Error", "message": str(e)})
        except Exception as e:
            # Se falhar ao ler o JSON inicial ou validar
            await websocket.close(code=1008, reason="Invalid authentication payload")
            return

        while True:
          
            raw = await websocket.receive_json()

            try:
                event = raw.get("event")
                data = raw.get("data", {})

                # Processa o evento
                await process_events_ws(event, data, user_id=current_user_id)


            except Exception as e:
                await websocket.send_json({
                    "event": "Error",
                    "message": str(e)
                })

    except Exception as e:
        print(f"Erro na conexão WS: {e}")