from .combatant import Combatant, ActiveCondition
from .events import CombatEvent

class CombatError(Exception):
  """illegal operattion for the current combat state"""
  
def initiative_sort_key(c: Combatant) -> tuple[int, int, int]:
  # checks initiative first, then dexterity, then entity type (players first, then npcs)
  return (-c.initiative, -c.dexterity, 0 if c.is_player else 1)
  
class Combat:
  def __init__(self, combatants: list[Combatant]) -> None:
    if not combatants:
      raise CombatError("Combat must have at least one combatant")
    self.combatants = sorted(combatants, key=initiative_sort_key)
    self.round = 1
    self.turn_index = 0
    self.started = False
    
  @property
  def current(self) -> Combatant:
    return self.combatants[self.turn_index]
  
  def start(self) -> list[CombatEvent]:
    if self.started:
      raise CombatError("Combat has already started")
    self.started = True
    return [CombatEvent("round_start", "Round 1 begins")]
  
  def advance_turn(self) -> list[CombatEvent]:
    if not self.started:
      raise CombatError("Combat has not started yet")
    
    events = self._end_of_turn(self.current)
    self.turn_index += 1
    
    if self.turn_index >= len(self.combatants):
      self.turn_index = 0
      self.round += 1
      events.append(CombatEvent("round_start", f"Round {self.round} begins"))
      
    events.append(CombatEvent("turn_start", f"{self.current.name}'s turn begins", self.current.id))
    return events
  
  def _end_of_turn(self, c: Combatant) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    remaining_conditions: list[ActiveCondition] = []
    for cond in c.conditions:
      if cond.rounds_remaining is None:
        remaining_conditions.append(cond)
      else:
        events.append(
          CombatEvent(
            "condition_expired",
            f"{cond.name} ends on {c.name}",
            c.id,
          )
        )
    c.conditions = remaining_conditions
    return events