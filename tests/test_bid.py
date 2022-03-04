def test_run_bid(bid):
    bid.runBid()
    assert bid.trail.successfulBidsCount == 1
    assert bid.trail.successfulBids.list.pop() == bid
    assert bid.hasher.successfulBids.list.pop() == bid
