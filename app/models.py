# from sqlmodel import SQLModel, Field, Relationship # type: ignore
# from typing import Optional, List
# from datetime import date

# class PlayerBase(SQLModel):
#     name: str
#     position: str
#     jersey_number: int = Field(ge=0, le=99)
#     height: float  # В метрах
#     weight: float  # В кг

# class Player(PlayerBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     stats: List["PlayerStats"] = Relationship(back_populates="player")

# class GameBase(SQLModel):
#     date: date
#     opponent: str
#     home_away: str  # "home" или "away"
#     points_scored: int
#     points_conceded: int

# class Game(GameBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     stats: List["PlayerStats"] = Relationship(back_populates="game")

# class PlayerStats(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     player_id: int = Field(foreign_key="player.id")
#     game_id: int = Field(foreign_key="game.id")
#     points: int
#     assists: int
#     rebounds: int
#     player: Player = Relationship(back_populates="stats")
#     game: Game = Relationship(back_populates="stats")