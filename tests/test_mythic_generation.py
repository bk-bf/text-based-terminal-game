from fantasy_rpg.world.mythic_generation import generate_mythic_events
from fantasy_rpg.world.world_coordinator import WorldCoordinator


def test_generate_default_number_of_events():
    wc = WorldCoordinator(world_size=(5,5), seed=42, skip_generation=False)
    # WorldCoordinator generates mythic_events during generation
    events = getattr(wc, 'mythic_events', None)
    assert events is not None, "mythic_events should be attached to WorldCoordinator"
    assert 8 <= len(events) <= 12, f"expected 8-12 events, got {len(events)}"


def test_event_fields_and_locations():
    wc = WorldCoordinator(world_size=(4,4), seed=1, skip_generation=False)
    events = wc.mythic_events
    for ev in events:
        assert 'id' in ev and ev['id'].startswith('mythic-')
        assert 'name' in ev and isinstance(ev['name'], str)
        assert 'year' in ev
        assert 'event_type' in ev
        assert 'description' in ev
        assert 'location' in ev
        # location should map to an existing hex id or be '0000'
        loc = ev['location']
        assert loc == '0000' or loc in wc.hex_data
