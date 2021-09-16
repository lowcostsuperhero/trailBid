from pytest import fixture
from trail import Trail


@fixture
def trail_capacity_small():
    return 1


def test_bid_count_no_bids(trail):
    assert trail.bidCount == 0
    assert trail.bidValue == 0


def test_get_time_slot_on_init_only(time_slot, trail_capacity, trail_id, trail_name):
    trail = Trail(trail_id, 0, trail_name, trail_capacity)
    assert trail.getTimeSlot() is None


def test_get_time_slot_after_set_time_slot(time_slot, trail_capacity, trail_id, trail_name):
    trail = Trail(trail_id, 0, trail_name, trail_capacity)
    trail.setTimeSlot(time_slot)
    assert trail.getTimeSlot() == time_slot


def test_add_bid(bid, trail):
    trail.addBid(bid)
    bids = trail.getBids()
    retrieved_bid = bids.getBids().list.pop()
    assert retrieved_bid is bid


def test_add_successful_bid(bid, trail):
    trail.addSuccessfulBid(bid)
    assert not trail.getBids().getBids().list
    success_bid = trail.successfulBids.list.pop()
    assert success_bid is bid


def test_is_at_cap_on_single_bid(bid, trail):
    trail.addBid(bid)
    assert not trail.isAtCapacity()


def test_is_at_cap_small_trail(bid, time_slot, trail_capacity_small, trail_id, trail_name):
    trail = Trail(trail_id, 0, trail_name, trail_capacity_small)
    trail.addSuccessfulBid(bid)
    assert trail.isAtCapacity()


def test_get_hashers_only_successful(bid, trail):
    trail.addSuccessfulBid(bid)
    assert trail.getHashers().list == []


def test_get_hashers(bid, trail):
    trail.addBid(bid)
    assert trail.getHashers().list.pop() == bid.hasher

