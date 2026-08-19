from dataclasses import dataclass
from enum import Enum

class Difficulty(Enum):
  TRIVIAL = "trivial"
  EASY = "easy"
  MEDIUM = "medium"
  HARD = "hard"
  DEADLY = "deadly"
  
@dataclass(frozen=True)
class PartyMember:
  level: int
  
  def __post_init__(self) -> None:
    if not 1 <= self.level <= 20:
      raise ValueError(f"level must be 1-20, got {self.level}")
    
@dataclass(frozen=True)
class MonsterEntry:
  challenge_rating: str
  count: int = 1