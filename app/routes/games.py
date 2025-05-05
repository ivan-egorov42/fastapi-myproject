from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_async_session
from app.schemas import users as schema_users
from app.schemas.games import Game, GameCreate, GameRead, GameUpdate

from ..auth import auth_handler

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/games", tags=["Games"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(oauth2_scheme)],
    response_model=GameRead,
)
async def create_game(
    game: GameCreate,
    current_user: schema_users.User = Depends(auth_handler.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Создает новую игру в базе данных.

    Параметры:
    - game: Данные для создания новой игры.
    - current_user: Аутентифицированный пользователь (для авторизации).
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Объект созданной игры.
    """
    db_game = Game(**game.dict())
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game


@router.get("/{game_id}", response_model=GameRead)
async def read_game(game_id: int, db: AsyncSession = Depends(get_async_session)):
    """
    Получает данные об одной игре по её ID.

    Параметры:
    - game_id: Уникальный идентификатор игры.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Объект игры, если она найдена.

    Исключения:
    - HTTPException 404, если игра не найдена.
    """
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
    home_away: Optional[str] = None,  # "home", "away"
):
    """
    Возвращает список игр с поддержкой фильтрации и пагинации.

    Параметры:
    - db: Асинхронная сессия базы данных.
    - skip: Количество записей для пропуска (смещение).
    - limit: Максимальное количество возвращаемых записей.
    - season: Фильтрация по сезону.
    - result: Фильтрация по результату ("win", "loss", "overtime").
    - home_away: Фильтрация по домашнему/выездному статусу ("home", "away").

    Возвращает:
    - Список игр, удовлетворяющих условиям фильтрации.
    """
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
    game_id: int, game_data: GameUpdate, db: AsyncSession = Depends(get_async_session)
):
    """
    Обновляет данные об игре по её ID.

    Параметры:
    - game_id: Уникальный идентификатор игры.
    - game_data: Частично обновленные данные игры.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Обновленный объект игры.

    Исключения:
    - HTTPException 404, если игра не найдена.
    """
    db_game = await db.get(Game, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")

    for key, value in game_data.dict(exclude_unset=True).items():
        setattr(db_game, key, value)

    await db.commit()
    await db.refresh(db_game)
    return db_game


@router.delete("/{game_id}", dependencies=[Depends(oauth2_scheme)])
async def delete_game(game_id: int, db: AsyncSession = Depends(get_async_session)):
    """
    Удаляет игру по её ID.

    Параметры:
    - game_id: Уникальный идентификатор игры.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Словарь с сообщением об успешном удалении.

    Исключения:
    - HTTPException 404, если игра не найдена.
    """
    db_game = await db.get(Game, game_id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")

    await db.delete(db_game)
    await db.commit()
    return {"message": "Game deleted"}
