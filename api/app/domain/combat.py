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
  
  def _find(self, combatant_id: str) -> Combatant:
    for c in self.combatants:
      if c.id == combatant_id:
        return c
    raise CombatError(f"no combatant found with id {combatant_id}")
  
  def apply_damage(
    self, combatant_id: str, amount: int, is_critical: bool = False
  ) -> list[CombatEvent]:
    if amount < 0:
      raise ValueError("Damage amount must be non-negative")
    
    target = self._find(combatant_id)
    events: list[CombatEvent] = []
    
    # if downed, any damage is a failed death save
    if not target.is_conscious:
      target.death_saves.failures += 2 if is_critical else 1
      events.append(
        CombatEvent(
          "death_save_failure",
          f"{target.name} took damage while down and fails a death save",
          target.id,
        )
      )
      if target.death_saves.is_dead:
        events.append(
          CombatEvent("death", f"{target.name} has died", target.id,)
        )
      return events
    
    # Apply damage to temp hp first, temp hp does not stack
    absorbed = min(target.temp_hp, amount)
    target.temp_hp -= absorbed
    remaining_damage = amount - absorbed
    
    target.current_hp -= remaining_damage
    events.append(
      CombatEvent(
        "damage", 
        f"{target.name} takes {amount} damage", 
        target.id,
        {"total": amount, "absorbed": absorbed, "to_hp": remaining_damage},
      )
    )
    
    if target.current_hp <= 0:
      overflow = abs(target.current_hp)
      target.current_hp = 0
      target.concentrating_on = None
      
      if overflow >= target.max_hp:
        target.death_saves.failures = 3
        events.append(
          CombatEvent("death", f"{target.name} has died", target.id,)
        )
      else:
        events.append(
          CombatEvent(
            "unconscious",
            f"{target.name} has fallen unconscious",
            target.id,
          )
        )
    elif target.concentrating_on:
      dc = max(10, remaining_damage // 2)
      events.append(
        CombatEvent(
          "concentration_check",
          f"{target.name} must make a concentration check (DC {dc})",
          target.id,
        )
      )
    return events
  
  def heal(self, combatant_id: str, amount: int) -> list[CombatEvent]:
    target = self._find(combatant_id)
    was_down = not target.is_conscious
    target.current_hp = min(target.max_hp, target.current_hp + amount)
    
    events = [
      CombatEvent("heal", f"{target.name} heals {amount} HP", target.id)
    ]
    if was_down and target.is_conscious:
      events.append(
        CombatEvent(
          "revived", f"{target.name} is revived", target.id
        )
      )
    return events