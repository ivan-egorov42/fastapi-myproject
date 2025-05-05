from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, validator
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel, UniqueConstraint

from app.schemas.games import GameRead
from app.schemas.players import PlayerRead


class StatsType(str, Enum):
    PLAYER = "player"
    GAME = "game"


class StatsBase(SQLModel):
    # Обязательные поля для всех типов статистики
    # game_id: Optional[int] = Field(..., foreign_key="game.id", description="ID связанной игры")
    stats_type: StatsType = Field(..., description="Тип статистики (player/game)")

    # Основные метрики
    points: int = Field(default=0, ge=0, description="Количество набранных очков")
    minutes_played: float = Field(
        default=0, ge=0, le=48, description="Сыгранные минуты"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                # "game_id": 1,
                "stats_type": "player",
                "points": 25,
                "minutes_played": 34.5,
            }
        }
    )


class PlayerStats(StatsBase, table=True):
    # __table_args__ = (UniqueConstraint("player_id", "game_id"),)
    """Модель статистики игрока в БД"""
    id: Optional[int] = Field(default=None, primary_key=True)
    # player_id: Optional[int] = Field(default=None, foreign_key="player.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Специфичные для игрока метрики
    assists: int = 0
    rebounds: int = 0
    steals: int = 0
    blocks: int = 0

    # Статистика бросков
    field_goals_made: int = 0
    field_goals_attempted: int = 0
    three_points_made: int = 0
    three_points_attempted: int = 0
    free_throws_made: int = 0
    free_throws_attempted: int = 0

    # Дополнительные метрики
    turnovers: int = 0
    personal_fouls: int = 0
    plus_minus: int = 0

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                # Специфичные для игрока метрики
                "assists": 5,
                "rebounds": 7,
                "steals": 2,
                "blocks": 1,
                # Статистика бросков
                "field_goals_made": 8,
                "field_goals_attempted": 15,
                "three_points_made": 3,
                "three_points_attempted": 6,
                "free_throws_made": 4,
                "free_throws_attempted": 5,
                # Дополнительные метрики
                "turnovers": 2,
                "personal_fouls": 3,
                "plus_minus": 12,
            }
        }
    )

class GameStats(StatsBase, table=True):
    # __table_args__ = (UniqueConstraint("game_id"),)
    """Модель игровой статистики в БД"""
    game_id : int = Field
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Специфичные поля
    team_points: int = 0
    opponent_points: int = 0
    quarter_scores: List[int] = Field(default=[], sa_type=ARRAY(Integer))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                # Специфичные для игры метрики
                "game_id": 1,
                "team_points": 102,
                "opponent_points": 98,
                "quarter_scores": [25, 30, 22, 25],
            }
        }
    )


class PlayerStatsCreate(StatsBase):
    """Схема для создания статистики игрока"""

    # player_id: int = Field(..., foreign_key="player.id", description="ID игрока")
    stats_type: StatsType = StatsType.PLAYER

    # Специфичные для игрока метрики
    assists: int = Field(default=0, ge=0, description="Результативные передачи")
    rebounds: int = Field(default=0, ge=0, description="Подборы")
    steals: int = Field(default=0, ge=0, description="Перехваты")
    blocks: int = Field(default=0, ge=0, description="Блок-шоты")

    # Статистика бросков
    field_goals_made: int = Field(default=0, ge=0, description="Успешные броски с игры")
    field_goals_attempted: int = Field(
        default=0, ge=0, description="Попытки бросков с игры"
    )
    three_points_made: int = Field(default=0, ge=0, description="Успешные 3-х очковые")
    three_points_attempted: int = Field(
        default=0, ge=0, description="Попытки 3-х очковых"
    )
    free_throws_made: int = Field(default=0, ge=0, description="Успешные штрафные")
    free_throws_attempted: int = Field(default=0, ge=0, description="Попытки штрафных")

    # Дополнительные метрики
    turnovers: int = Field(default=0, ge=0, description="Потери мяча")
    personal_fouls: int = Field(default=0, ge=0, le=6, description="Фолы (0-6)")
    plus_minus: int = Field(default=0, description="Показатель +/-")

    model_config = ConfigDict(
    json_schema_extra={
        "example": {
            "points": 25,
            "minutes_played": 34.5,
            "stats_type" :"game",
            # Специфичные для игрока метрики
            "assists": 5,
            "rebounds": 7,
            "steals": 2,
            "blocks": 1,
            # Статистика бросков
            "field_goals_made": 8,
            "field_goals_attempted": 15,
            "three_points_made": 3,
            "three_points_attempted": 6,
            "free_throws_made": 4,
            "free_throws_attempted": 5,
            # Дополнительные метрики
            "turnovers": 2,
            "personal_fouls": 3,
            "plus_minus": 12,
        }
    }
)


class GameStatsCreate(StatsBase):
    """Схема для создания игровой статистики (командной)"""

    stats_type: StatsType = StatsType.GAME

    # Специфичные для игры метрики
    game_id : int = Field
    team_points: int = Field(default=0, ge=0, description="Очки команды")
    opponent_points: int = Field(default=0, ge=0, description="Очки соперника")
    quarter_scores: List[int] = Field(default=[], description="Очки по четвертям")


class PlayerStatsRead(PlayerStatsCreate):
    """Схема для чтения статистики игрока"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class GameStatsRead(GameStatsCreate):
    """Схема для чтения игровой статистики"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class PlayerStatsUpdate(BaseModel):
    assists: Optional[int] = None
    rebounds: Optional[int] = None
    steals: Optional[int] = None
    blocks: Optional[int] = None
    field_goals_made: Optional[int] = None
    field_goals_attempted: Optional[int] = None
    three_points_made: Optional[int] = None
    three_points_attempted: Optional[int] = None
    free_throws_made: Optional[int] = None
    free_throws_attempted: Optional[int] = None
    turnovers: Optional[int] = None
    personal_fouls: Optional[int] = None
    plus_minus: Optional[int] = None


class GameStatsUpdate(BaseModel):
    id: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    team_points: Optional[int] = None
    opponent_points: Optional[int] = None
    quarter_scores: Optional[int] = None


class PlayerStatsWithGame(PlayerStatsRead):
    """Схема статистики игрока с данными игры"""

    game: "GameRead"


class GameStatsWithPlayers(GameStatsRead):
    game: "GameRead"
    game_stats: "GameStatsRead"
    player: List["PlayerStatsRead"]
