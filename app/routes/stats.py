from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas.games import Game
from app.schemas.players import Player
from app.schemas.stats import GameStatsCreate  # Создание игровой статистики
from app.schemas.stats import GameStatsRead  # Схема чтения игровой статистики
from app.schemas.stats import PlayerStatsCreate  # Создание статистики игрока
from app.schemas.stats import PlayerStatsRead  # Схема чтения статистики игрока
from app.schemas.stats import PlayerStatsWithGame  # Статистика игрока + данные игры
from app.schemas.stats import (
    GameStats,
    GameStatsUpdate,
    GameStatsWithPlayers,
    PlayerStats,
    PlayerStatsUpdate,
)

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.post("/games/{game_id}/players/{player_id}", response_model=PlayerStatsRead)
async def create_player_stats_for_game(
    game_id: int,
    player_id: int,
    stats: PlayerStatsCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Создает запись со статистикой игрока в конкретной игре.

    Параметры:
    - game_id: ID игры.
    - player_id: ID игрока.
    - stats: Данные статистики.
    - db: Сессия базы данных.

    Возвращает:
    - Объект созданной статистики игрока.

    Исключения:
    - HTTPException 404, если игрок или игра не найдены.
    """
    # Проверка существования игрока и игры
    if not await db.get(Player, player_id):
        raise HTTPException(404, "Player not found")
    if not await db.get(Game, game_id):
        raise HTTPException(404, "Game not found")

    db_stats = PlayerStats(**stats.dict(), player_id=player_id, game_id=game_id)
    db.add(db_stats)
    await db.commit()
    await db.refresh(db_stats)
    return db_stats


@router.post("/games/", response_model=GameStatsRead)
async def create_game_stats(
    stats: GameStatsCreate, db: AsyncSession = Depends(get_async_session)
):
    """
    Создает командную статистику для указанной игры.

    Параметры:
    - stats: Данные статистики игры.
    - db: Сессия базы данных.

    Возвращает:
    - Объект созданной командной статистики.

    Исключения:
    - HTTPException 404, если игра не найдена.
    """
    if not await db.get(Game, stats.game_id):
        raise HTTPException(404, "Game not found")

    db_stats = GameStats(**stats.dict())
    db.add(db_stats)
    await db.commit()
    await db.refresh(db_stats)
    return db_stats


@router.get("/players/{player_id}/games/{game_id}", response_model=PlayerStatsRead)
async def get_player_stats_for_game(
    player_id: int, game_id: int, db: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает статистику конкретного игрока в конкретной игре.

    Параметры:
    - player_id: ID игрока.
    - game_id: ID игры.
    - db: Сессия базы данных.

    Возвращает:
    - Объект статистики игрока.

    Исключения:
    - HTTPException 404, если статистика не найдена.
    """
    stats = await db.execute(
        select(PlayerStats)
        .where(PlayerStats.player_id == player_id)
        .where(PlayerStats.game_id == game_id)
    )
    stats = stats.scalar_one_or_none()
    if not stats:
        raise HTTPException(404, "Stats not found")
    return stats


@router.get("/players/{player_id}", response_model=List[PlayerStatsWithGame])
async def get_all_player_stats(
    player_id: int,
    season: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает все записи статистики игрока, опционально фильтруя по сезону.

    Параметры:
    - player_id: ID игрока.
    - season: Сезон (опционально).
    - db: Сессия базы данных.

    Возвращает:
    - Список объектов статистики с данными об играх.
    """
    query = select(PlayerStats).where(PlayerStats.player_id == player_id)

    if season:
        query = query.join(Game).where(Game.season == season)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/games/{game_id}", response_model=GameStatsRead)
async def get_game_stats(game_id: int, db: AsyncSession = Depends(get_async_session)):
    """
    Возвращает командную статистику для конкретной игры.

    Параметры:
    - game_id: ID игры.
    - db: Сессия базы данных.

    Возвращает:
    - Объект командной статистики.

    Исключения:
    - HTTPException 404, если игра не найдена.
    """
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")

    team_stats = await db.execute(select(GameStats).where(GameStats.game_id == game_id))
    return team_stats.scalar_one_or_none()


@router.get("/games/{game_id}/full-stats", response_model=GameStatsWithPlayers)
async def get_full_game_stats(
    game_id: int, db: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает полную статистику игры: командную и по игрокам.

    Параметры:
    - game_id: ID игры.
    - db: Сессия базы данных.

    Возвращает:
    - Объект с игрой, командной статистикой и списком статистик игроков.

    Исключения:
    - HTTPException 404, если игра не найдена.
    """
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")

    team_stats = await db.execute(select(GameStats).where(GameStats.game_id == game_id))
    players_stats = await db.execute(
        select(PlayerStats).where(PlayerStats.game_id == game_id).join(Player)
    )

    return {
        "game": game,
        "team_stats": team_stats.scalar_one_or_none(),
        "players_stats": players_stats.scalars().all(),
    }


@router.get("/players/{player_id}/aggregate")
async def get_player_aggregates(
    player_id: int,
    season: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Вычисляет агрегированные показатели по очкам игрока за все игры (или сезон).

    Параметры:
    - player_id: ID игрока.
    - season: Сезон (опционально).
    - db: Сессия базы данных.

    Возвращает:
    - Словарь с агрегатами: среднее, максимум, сумма очков.

    Исключения:
    - HTTPException 404, если нет данных.
    """
    stats = select(
        func.avg(PlayerStats.points).label("avg_points"),
        func.max(PlayerStats.points).label("max_points"),
        func.sum(PlayerStats.points).label("total_points"),
    ).where(PlayerStats.player_id == player_id)

    if season:
        stats = stats.join(Game).where(Game.season == season)

    result = await db.execute(stats)
    aggregates = result.first()

    if not aggregates:
        raise HTTPException(404, "No stats found")

    return {
        "player_id": player_id,
        "avg_points": round(float(aggregates.avg_points or 0), 1),
        "max_points": aggregates.max_points or 0,
        "total_points": aggregates.total_points or 0,
    }


# Обновление конкретной статистики игрока (по ID статистики)
@router.patch("{stats_id}/players/{player_id}", response_model=PlayerStatsRead)
async def update_player_stats(
    player_id: int,
    stats_id: int,
    stats_update: PlayerStatsUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет существующую запись статистики игрока по ID статистики и игрока.

    Параметры:
    - stats_id: ID записи статистики.
    - player_id: ID игрока.
    - stats_update: Обновленные данные.
    - db: Сессия базы данных.

    Возвращает:
    - Обновленный объект статистики.

    Исключения:
    - HTTPException 404, если статистика не найдена или не принадлежит игроку.
    """
    # Проверяем, что статистика принадлежит игроку
    db_stats = await db.execute(
        select(PlayerStats)
        .where(PlayerStats.id == stats_id)
        .where(PlayerStats.player_id == player_id)
    )
    db_stats = db_stats.scalar_one_or_none()

    if not db_stats:
        raise HTTPException(404, "Stats not found for this player")

    for key, value in stats_update.dict(exclude_unset=True).items():
        setattr(db_stats, key, value)

    await db.commit()
    await db.refresh(db_stats)
    return db_stats


@router.patch("/games/{game_id}", response_model=GameStatsRead)
async def update_game_stats(
    game_id: int,
    stats_update: GameStatsUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет или создает статистику игры.

    Параметры:
    - game_id: ID игры.
    - stats_update: Обновленные данные.
    - db: Сессия базы данных.

    Возвращает:
    - Объект обновленной (или созданной) статистики игры.
    """
    # Получаем или создаем статистику игры
    stats = await db.execute(select(GameStats).where(GameStats.game_id == game_id))
    stats = stats.scalar_one_or_none()

    if not stats:
        stats = GameStats(game_id=game_id, **stats_update.dict())
        db.add(stats)
    else:
        for field, value in stats_update.dict(exclude_unset=True).items():
            setattr(stats, field, value)

    await db.commit()
    await db.refresh(stats)
    return stats


@router.patch("/players/{player_id}/games/{game_id}", response_model=PlayerStatsRead)
async def update_player_stats_for_game(
    player_id: int,
    game_id: int,
    stats_update: PlayerStatsUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет или создает статистику игрока в конкретной игре.

    Параметры:
    - player_id: ID игрока.
    - game_id: ID игры.
    - stats_update: Обновленные данные.
    - db: Сессия базы данных.

    Возвращает:
    - Объект обновленной (или созданной) статистики игрока.

    Исключения:
    - HTTPException 404, если игрок или игра не найдены.
    """
    # Проверяем существование игры и игрока
    if not (await db.get(Player, player_id)) or not (await db.get(Game, game_id)):
        raise HTTPException(404, "Player or Game not found")

    # Находим или создаем статистику
    stats = await db.execute(
        select(PlayerStats)
        .where(PlayerStats.player_id == player_id)
        .where(PlayerStats.game_id == game_id)
    )
    stats = stats.scalar_one_or_none()

    if not stats:
        stats = PlayerStats(player_id=player_id, game_id=game_id, **stats_update.dict())
        db.add(stats)
    else:
        for field, value in stats_update.dict(exclude_unset=True).items():
            setattr(stats, field, value)

    await db.commit()
    await db.refresh(stats)
    return stats


@router.delete("/games/{stats_id}")
async def delete_game_stats(
    stats_id: int, db: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет запись командной статистики по ID.

    Параметры:
    - stats_id: ID записи статистики игры.
    - db: Сессия базы данных.

    Возвращает:
    - Сообщение об успешном удалении.

    Исключения:
    - HTTPException 404, если запись не найдена.
    """
    stats = await db.get(GameStats, stats_id)
    if not stats:
        raise HTTPException(404, "Stats record not found")

    await db.delete(stats)
    await db.commit()
    return {"message": "Stats deleted successfully"}


@router.delete("/players/{stats_id}")
async def delete_player_stats(
    stats_id: int, db: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет запись статистики игрока по ID.

    Параметры:
    - stats_id: ID записи статистики игрока.
    - db: Сессия базы данных.

    Возвращает:
    - Сообщение об успешном удалении.

    Исключения:
    - HTTPException 404, если запись не найдена.
    """
    stats = await db.get(PlayerStats, stats_id)
    if not stats:
        raise HTTPException(404, "Stats record not found")

    await db.delete(stats)
    await db.commit()
    return {"message": "Stats deleted successfully"}
