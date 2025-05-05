from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel


class GameLocation(str, Enum):
    HOME = "home"
    AWAY = "away"


class GameBase(SQLModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "game_date": "2023-11-15",
                "opponent": "Los Angeles Lakers",
                "home_away": "home",
                "points_scored": 112,
                "points_conceded": 108,
                "season": "2023-2024",
            }
        }
    )

    game_date: date
    opponent: str = Field(..., description="Opponent team name")
    home_away: GameLocation = Field(..., description="Game location: home or away")
    points_scored: int = Field(..., ge=0, description="Points scored by the team")
    points_conceded: int = Field(..., ge=0, description="Points conceded by the team")
    season: str = Field(..., description="Season in format YYYY-YYYY")


class Game(GameBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class GameCreate(GameBase):
    pass


class GameRead(GameBase):
    id: int


class GameUpdate(BaseModel):
    game_date: Optional[date] = None
    opponent: Optional[str] = None
    home_away: Optional[GameLocation] = None
    points_scored: Optional[int] = None
    points_conceded: Optional[int] = None
    season: Optional[str] = None

    class Config:
        json_schema_extra = {"example": {"points_scored": 115, "points_conceded": 110}}
