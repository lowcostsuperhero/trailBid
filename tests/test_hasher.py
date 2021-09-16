def test_init(hasher):
    assert hasher


def test_bid_count_on_bidless_hasher(hasher):
    assert hasher.bidCount == 0


def test_bid_value_on_bidless_hasher(hasher):
    assert hasher.bidValue == 0


def test_successful_bid_count_on_bidless_hasher(hasher):
    assert hasher.successfulBidCount == 0


def test_add_bid(bid, bid_allowance, hasher, mocker):
    mock_settings = {'bidAllowance': bid_allowance}
    mocker.patch('hasher.settings', mock_settings)
    hasher.addBid(bid)
    assert hasher.bids.list.pop() == bid

