from pydantic import BaseModel, Field

class PartyMemberIn(BaseModel):
  level: int - Field(ge=1, le=20)
  
class MonsterEntryIn(BaseModel):
  challenge_rating: str
  count: int = Field(default=1, ge=1, le=100)
  
class ThresholdsOut(BaseModel):
  easy: int
  medium: int
  hard: int
  deadly: int
  
class RateEncounterRequest(BaseModel):
  party: list[PartyMemberIn] = Field(min_length=1)
  monsters: list[MonsterEntryIn] = Field(min_length=1)
  
class RateEncounterResponse(BaseModel):
  difficulty: str
  raw_xp: int
  adjusted_xp: int
  multiplier: float
  thresholds: ThresholdsOut
  
class CombatantIn(BaseModel):
  name: str = Field(min_length=1, max_length=100)
  max_hp: int = Field(ge=1)
  initiative: int
  dexterity: int = Field(default=10, ge=1, le=30)
  is_player: bool = False
  
class CombatantOut(BaseModel):
  id: str
  name: str
  max_hp: int
  current_hp: int
  temp_hp: int
  initiative: int
  is_player: bool
  is_conscious: bool
  conditions: list[ConditionOut]
  
class ConditionOut(BaseModel):
  name: str
  duration: int | None
  
class EventOut(BaseModel):
  kind: str
  message: str
  combatant_id: str | None = None
  data: dict | None = None
  
class CombatOut(BaseModel):
  id: str
  round: int
  current_combatant_id: str | None
  combatants: list[CombatantOut]
  
class CombatActionResponse(BaseModel):
  combat: CombatOut
  events: list[EventOut]
  
class DamageRequest(BaseModel):
  amount: int = Field(ge=0)
  is_critical: bool = False