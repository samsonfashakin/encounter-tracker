from .models import Difficulty, MonsterEntry, PartyMember
from .xp_tables import CR_TO_XP, XP_THRESHOLDS

MULTIPLIERS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

def party_thresholds(party: list[PartyMember]) -> tuple[int, int, int, int]:
  """Sum each party member's 4 xp thresholds into party-wide budgets for easy, medium, hard, and deadly encounters."""
  if not party:
    raise ValueError("party must not be empty")
  totals = [0, 0, 0, 0]
  for member in party:
    for i, value in enumerate(XP_THRESHOLDS[member.level]):
      totals[i] += value
  return tuple(totals) # type: ignore[return-value]

def _multiplier_index(monster_count: int) -> int:
  """Return the index of the multiplier to use for a given number of monsters."""
  if monster_count <= 1:
    return 0
  elif monster_count <= 2:
    return 1
  elif monster_count <= 6:
    return 2
  elif monster_count <= 10:
    return 3
  elif monster_count <= 14:
    return 4
  else:
    return 5
  
def encounter_multiplier(monster_count: int, party_size: int) -> float:
  """Action economy multiplier for a given number of monsters and party size. Shifted for unusually large or small parties."""
  index = _multiplier_index(monster_count)
  if party_size < 3:
    index += 1            #small party: treat as one step harder
  elif party_size >= 6:
    index -= 1            #large party: treat as one step easier
  index = max(0, min(index, len(MULTIPLIERS) - 1))  #clamp to valid range
  return MULTIPLIERS[index]

def raw_xp(monsters: list[MonsterEntry]) -> int:
  """Sum the raw XP of a list of monsters."""
  return sum(CR_TO_XP[m.challenge_rating] * m.count for m in monsters)

def rate_encounter(
  party: list[PartyMember], monsters: list[MonsterEntry]
) -> tuple[Difficulty, int]:
  """Return the difficulty and the adjusted XP of the encounter that produced it"""
  monster_count = sum(m.count for m in monsters)
  multiplier = encounter_multiplier(monster_count, len(party))
  adjusted_xp = int(raw_xp(monsters) * multiplier)
  
  easy, medium, hard, deadly = party_thresholds(party)
  if adjusted_xp >= deadly:
    return Difficulty.DEADLY, adjusted_xp
  elif adjusted_xp >= hard:
    return Difficulty.HARD, adjusted_xp
  elif adjusted_xp >= medium:
    return Difficulty.MEDIUM, adjusted_xp
  elif adjusted_xp >= easy:
    return Difficulty.EASY, adjusted_xp
  return Difficulty.TRIVIAL, adjusted_xp