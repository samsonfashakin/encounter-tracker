from dataclasses import dataclass, field

#Using entities instead of value objects for combatants to allow for more complex behavior and state management in the future. These will have identity and will mutate over the course of a combat encounter, so they are not frozen dataclasses.


@dataclass
class DeathSaves:
  successes: int = 0
  failures: int = 0
  
  @property
  def is_dead(self) -> bool:
    return self.failures >= 3
  
  @property
  def is_stable(self) -> bool:
    return self.successes >= 3
  
  def reset(self) -> None:
    self.successes = 0
    self.failures = 0
    
@dataclass
class ActiveCondition:
  name: str
  duration: int | None = None  # Duration in rounds, None = indefinite
  
  @dataclass
  class Combatant:
    id: str
    name: str
    max_hp: int
    current_hp: int
    initiative: int
    dexterity: int
    is_player: bool
    temp_hp: int = 0
    conditions: list[ActiveCondition] = field(default_factory=list)
    death_saves: DeathSaves = field(default_factory=DeathSaves)
    concentrating_on: str | None = None
    
    @property
    def is_conscious(self) -> bool:
      return self.current_hp > 0
    
    @property
    def is_dead(self) -> bool:
      return self.death_saves.is_dead
    
    def has_condition(self, name: str) -> bool:
      return any(c.name == name for c in self.conditions)
    
    