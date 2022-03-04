from bid import Bids


def test_Bids_init(bid_file, hashers, trails):
    assert Bids('.', hashers, trails)


def test_get_bids_by_hasher_id(bids):
    bid = bids.getBidsByHasherId(0)
    bid_by_hasher = bid.list.pop()
    assert bid_by_hasher.hasher.id == 0


def test_bookend_values(bids):
    assert bids.bookendValues == (100, 100)


def test_count(bids):
    assert bids.count == 500


def test_value(bids):
    assert bids.value == 50000


def test_add(bid, bids):
    bids.add(bid)
    assert bids.getBidsByHasherId(bid.hasher.id).list.pop() == bid


def test_get_bids_by_time_slot(bids, time_slots):
    time_slot = time_slots.list.pop()
    assert bids.getBidsByTimeSlotId(int(time_slot.id)).list.pop().timeSlot == time_slot


def test_get_bids_by_trail_id(bids, trails):
    trail = trails.list.pop()
    assert bids.getBidsByTrailId(str(trail.id)).list.pop().trail == trail


def test_get_hashers_by_time_slot_id(bids, time_slots):
    time_slot = time_slots.list.pop()
    hashers = bids.getHashersByTimeSlotId(time_slot.id)
    assert hashers.list


def test_get_time_slots(bids, time_slots):
    slots = bids.getTimeSlots()
    assert slots.list == time_slots.list


def test_get_trails_by_time_slot_id(bids, time_slots):
    trails = bids.getTrailsByTimeSlotId(int(time_slots.list[0].id))
    assert 0 in [int(trail.id) for trail in trails.list]


def test_get_hashers(bids, hashers):
    assert len(bids.getHashers().list) == 500
