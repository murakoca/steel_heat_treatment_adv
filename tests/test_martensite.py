def test_Ms():
    from metallurgy.martensite import Ms
    assert Ms({'C':0.8}) < 300