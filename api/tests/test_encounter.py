import pytest
from app.domain.encounter import encounter_multiplier, rate_encounter
from app.domain.models import Difficulty, MonsterEntry, PartyMember

def test_easy_encounter():
  party = [PartyMember(1)] * 4
  monsters = [MonsterEntry("1/4", count=2)]
  difficulty, adjusted_xp = rate_encounter(party, monsters)
  assert difficulty is Difficulty.EASY
  assert adjusted_xp == 150
  
def test_for_trivial_encounter():
  party = [PartyMember(1)] * 4
  monsters = [MonsterEntry("1/4", count=1)]
  difficulty, _ = rate_encounter(party, monsters)
  assert difficulty is Difficulty.TRIVIAL
  
def test_mult_scales_with_mons():
  assert encounter_multiplier(1, party_size=4) == 1.0
  assert encounter_multiplier(4, party_size=4) == 2.0
  assert encounter_multiplier(20, party_size=4) == 4.0
  
def test_small_party_shifts_mult_up():
  assert encounter_multiplier(4, party_size=2) == 2.5
  
def test_large_party_shifts_mult_down():
  assert encounter_multiplier(4, party_size=6) == 1.5
  
@pytest.mark.parametrize("count", [1, 100])
def test_mult_never_escapes_table(count):
  assert encounter_multiplier(count, party_size=1) in [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
  
def test_empty_party_is_rejected():
  with pytest.raises(ValueError):
    rate_encounter([], [MonsterEntry("1")])
    
def test_party_of_five_wont_shift_mult():
  assert encounter_multiplier(4, party_size=5) == 2.0
  
def test_party_of_six_shifts_mult_down():
  assert encounter_multiplier(4, party_size=6) == 1.5