from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from typing import Optional

from app.db import get_async_session
# from app.models import Game
from app.schemas.games import Game, GameCreate, GameRead, GameUpdate

router = APIRouter(prefix="/games", tags=["Games"])

@router.post("/", response_model=GameRead)
async def create_game(
    game: GameCreate, 
    db: AsyncSession = Depends(get_async_session)
):
    db_game = Game(**game.dict())
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game

@router.get("/{game_id}", response_model=GameRead)
async def read_game(
    game_id: int, 
    db: AsyncSession = Depends(get_async_session)
):
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.get("/", response_model=List[GameRead])
async def read_games(
    *,
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
    season: Optional[str] = None,
    result: Optional[str] = None,  # "win", "loss", "overtime"
    home_away: Optional[str] = None  # "home", "away"
):
    query = select(Game)
    
    if season:
        query = query.where(Game.season == season)
    if result:
        query = query.where(Game.result == result)
    if home_away:
        query = query.where(Game.home_away == home_away)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.patch("/{game_id}", response_model=GameRead)
async def update_game(
    game_id: int,
    game_data: GameUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    db_game = await db.get(Game, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    for key, value in game_data.dict(exclude_unset=True).items():
        setattr(db_game, key, value)
    
    await db.commit()
    await db.refresh(db_game)
    return db_game
# TODO: add security
# from app.core.security import get_current_user

# @router.post("/", dependencies=[Depends(get_current_user)])
# async def create_game_protected(
#     game: GameCreate,
#     db: AsyncSession = Depends(get_async_session)
# ):
#     # Только авторизованные пользователи могут создавать матчи
#     db_game = Game(**game.dict())
#     db.add(db_game)
#     await db.commit()
#     return db_game