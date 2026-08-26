from dataclasses import dataclass

@dataclass
class CombatEvent:
    kind: str
    message: str
    combatant_id: str | None = None
    
