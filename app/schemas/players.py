from datetime import date
from enum import Enum
from sqlmodel import SQLModel, Field
from pydantic import ConfigDict
from typing import Optional

class PlayerBase(SQLModel):
    name: str = Field(..., description="Full name of player")
    position: str = Field(..., description="Player's position")
    jersey_number: int = Field(..., ge=0, le=99, description="Jersey number")
    height: float = Field(..., gt=0, description="Height in meters")
    weight: float = Field(..., gt=0, description="Weight in kg")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Luka Dončić",
                "position": "Point Guard",
                "jersey_number": 77,
                "height": 2.01,
                "weight": 104
            }
        }
    )

class Player(PlayerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # stats: List["PlayerStats"] = Relationship(back_populates="player")  # Если есть связь

class PlayerCreate(PlayerBase):
    pass

class PlayerRead(PlayerBase):
    id: int

class PlayerUpdate(SQLModel):
    name: Optional[str] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None