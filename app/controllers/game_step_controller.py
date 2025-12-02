from fastapi import APIRouter, Depends, HTTPException
from app.core.config import RABBITMQ_URI

from app.database.db import get_database

from app.schemas.step_schema import GameStepRequest, GameStepResponse


from app.repositories.match_repository import MatchRepository
from app.repositories.wallets_repository import WalletRepository
from app.services.game_steps_service import GameStepService
from app.utils.rabbitmq import RabbitMQPublisher


GameStepRouter = APIRouter(tags=["Jogada"])


# --- Dependência do banco ---
def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass


# --- Injeção de dependências do Service ---
def get_game_step_service(db=Depends(get_db)):

    match_repo = MatchRepository(db["matches"])
    wallet_repo = WalletRepository(db)

    rabbitmq = RabbitMQPublisher(RABBITMQ_URI)

    return GameStepService(
        match_repo=match_repo,
        wallet_repo=wallet_repo,
        rabbitmq=rabbitmq
    )


# --- Endpoint ---
@GameStepRouter.post("/game/step", response_model=GameStepResponse)
async def step_game(
    body: GameStepRequest,
    service: GameStepService = Depends(get_game_step_service)
):
    """
    Realiza uma jogada no jogo:
        - valida partida
        - verifica mina
        - envia STEP_RESULT
        - envia GAME_LOSE ou GAME_WIN
        - atualiza current_step
        - atualiza saldo (se win)
    """

    try:
        result = await service.step_in_game(
            cell=body.cell,
            matches_id=body.match_id
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
