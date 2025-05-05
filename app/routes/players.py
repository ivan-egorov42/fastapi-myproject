from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import and_, or_, select

from app.db import get_async_session

# from app.models import Player
from app.schemas.players import Player, PlayerCreate, PlayerRead, PlayerUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/players", tags=["Players"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(oauth2_scheme)],
    response_model=PlayerRead,
)
async def create_player(
    player: PlayerCreate, db: AsyncSession = Depends(get_async_session)
):
    """
    Создает нового игрока в базе данных.

    Параметры:
    - player: Данные для создания нового игрока.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Объект созданного игрока.
    """

    db_player = Player(**player.dict())
    db.add(db_player)
    await db.commit()
    await db.refresh(db_player)
    return db_player


@router.get("/{player_id}", response_model=PlayerRead)
async def read_player(player_id: int, db: AsyncSession = Depends(get_async_session)):
    """
    Получает данные об одном игроке по его ID.

    Параметры:
    - player_id: Уникальный идентификатор игрока.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Объект игрока, если он найден.

    Исключения:
    - HTTPException 404, если игрок не найден.
    """

    player = await db.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/", response_model=List[PlayerRead])
async def read_players(
    *,
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
    # Фильтры
    position: Optional[str] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    # Сортировка
    sort_by: str = "name",
    sort_order: str = "asc",  # или "desc"
):
    """
    Возвращает список игроков с поддержкой фильтрации, пагинации и сортировки.

    Параметры:
    - db: Асинхронная сессия базы данных.
    - skip: Количество записей для пропуска.
    - limit: Максимальное количество записей.
    - position: Фильтрация по позиции игрока.
    - min_height: Минимальный рост.
    - max_height: Максимальный рост.
    - sort_by: Поле для сортировки ("name", "jersey_number", "height").
    - sort_order: Порядок сортировки ("asc" или "desc").

    Возвращает:
    - Список игроков, удовлетворяющих условиям.
    """
    query = select(Player)

    # Фильтрация
    if position:
        query = query.where(Player.position == position)
    if min_height:
        query = query.where(Player.height >= min_height)
    if max_height:
        query = query.where(Player.height <= max_height)

    # Сортировка
    if sort_by not in ["name", "jersey_number", "height"]:
        sort_by = "name"
    order_field = getattr(Player, sort_by)
    query = query.order_by(
        order_field.asc() if sort_order == "asc" else order_field.desc()
    )

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.patch("/{player_id}", response_model=PlayerRead)
async def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные игрока по его ID.

    Параметры:
    - player_id: Уникальный идентификатор игрока.
    - player_data: Частично обновленные данные игрока.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Обновленный объект игрока.

    Исключения:
    - HTTPException 404, если игрок не найден.
    """
    db_player = await db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    for key, value in player_data.dict(exclude_unset=True).items():
        setattr(db_player, key, value)

    await db.commit()
    await db.refresh(db_player)
    return db_player


@router.delete("/{player_id}", dependencies=[Depends(oauth2_scheme)])
async def delete_player(player_id: int, db: AsyncSession = Depends(get_async_session)):
    """
    Удаляет игрока по его ID.

    Параметры:
    - player_id: Уникальный идентификатор игрока.
    - db: Асинхронная сессия базы данных.

    Возвращает:
    - Словарь с сообщением об успешном удалении.

    Исключения:
    - HTTPException 404, если игрок не найден.
    """
    db_player = await db.get(Player, player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")

    await db.delete(db_player)
    await db.commit()
    return {"message": "Player deleted"}
