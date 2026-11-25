from lib.classify import classify


def test_classify():
    assert classify(620, 620, .10) == "near"
    assert classify(593, 620, .10) == "near"
    assert classify(930, 620, .10) == "wide"
    assert classify(292, 620, .10) == "narrow"
    assert classify(682, 620, .10) == "near"   # limite incluse
    assert classify(683, 620, .10) == "wide"
