import pytest
from app.domain.combat import Combat, CombatError
from app.domain.combatant import ActiveCondition, Combatant

def make(name, hp=20, init=10, dex=10, player=False):
  return Combatant(
    id=name.lower(), name=name, max_hp=hp, current_hp=hp, initiative=init, dexterity=dex, is_player=player,
  )
  
def test_initiative_orders_highest_first():
  combat = Combat([make("Slow", init=5), make("Fast", init=20)])
  assert [c.name for c in combat.combatants] == ["Fast", "Slow"]
  
def test_dexterity_breaks_initiative_ties():
  combat = Combat([make("Clumsy", init=10, dex=8), make("Nimble", init=10, dex=16)])
  assert combat.current.name == "Nimble"
  
def test_players_win_full_ties():
  combat = Combat([
    make("Goblin", init=10, dex=14),
    make("Rogue", init=10, dex=14, player=True),
  ])
  assert combat.current.name == "Rogue"
  
def test_round_increments_after_last_combatant():
  combat = Combat([make("A", init=20), make("B", init=10)])
  combat.start()
  combat.advance_turn()
  assert combat.round == 1
  combat.advance_turn()
  assert combat.round == 2
  assert combat.current.name == "A"
  
def test_condition_expires_at_end_of_own_turn():
  target = make("Bard", init=20)
  target.conditions.append(ActiveCondition("poisoned", duration=1))
  combat = Combat([target, make("Orc", init=10)])
  combat.start()
  events = combat.advance_turn()
  assert not target.has_condition("poisoned")
  assert any(e.kind == "condition_expired" for e in events)
  
def test_indefinite_condition_never_expire():
  target = make("Bard", init=20)
  target.conditions.append(ActiveCondition("blinded", duration=None))
  combat = Combat([target, make("Orc", init=10)])
  combat.start()
  for _ in range(6):
    combat.advance_turn()
  assert target.has_condition("blinded")
  
def test_temp_hp_absorbs_before_real_hp():
  c = make("Wizard", hp=20)
  c.temp_hp = 5
  combat = Combat([c])
  combat.apply_damage("wizard", 8)
  assert c.temp_hp == 0
  assert c.current_hp == 17
  
def test_damage_triggers_concentration_check():
  c = make("Wizard", hp=30)
  c.concentrating_on = "hold_person"
  combat = Combat([c])
  events = combat.apply_damage("wizard", 9)
  check = next(e for e in events if e.kind == "concentration_check")
  assert "DC 10" in check.message # 9 // 2 = 4, floored to a minimum of 10
  
def test_dropping_to_zero_breaks_concentration_without_a_check():
  c = make("Wizard", hp=10)
  c.concentrating_on = "hold_person"
  combat = Combat([c])
  events = combat.apply_damage("wizard", 10)
  assert c.concentrating_on is None
  assert not any(e.kind == "concentration_check" for e in events)
  
def test_overflow_just_below_max_hp_only_knocks_out():
  c = make("Fighter", hp=20)
  combat = Combat([c])
  combat.apply_damage("fighter", 39)
  assert not c.is_dead
  assert not c.is_conscious
  
def test_critical_hit_on_downed_target_costs_two_saves():
  c = make("Fighter", hp=10)
  combat = Combat([c])
  combat.apply_damage("fighter", 10)
  combat.apply_damage("fighter", 5, is_critical=True)
  assert c.death_saves.failures == 2
  
def test_healing_from_zero_resets_death_saves():
  c = make("Fighter", hp=20)
  combat = Combat([c])
  combat.apply_damage("fighter", 25)
  c.death_saves.failures = 2
  combat.heal("fighter", 5)
  assert c.current_hp == 5
  assert c.death_saves.failures == 0
  
def test_advancing_before_start_is_rejected():
  combat = Combat([make("A")])
  with pytest.raises(CombatError):
    combat.advance_turn()
    
def test_damage_event_reports_the_full_hit_not_the_net():
  c = make("Wizard", hp=20)
  c.temp_hp = 5
  combat = Combat([c])
  events = combat.apply_damage("wizard", 12)
  damage_event = next(e for e in events if e.kind == "damage")
  assert "12 damage" in damage_event.message
  assert c.current_hp == 13