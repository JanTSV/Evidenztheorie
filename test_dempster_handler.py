from python_evidence.dempster_handler import _MeasureCollector, DempsterHandler, Measure

"""
GOOD
"""
def test_dempster_handler_1_good():
    dh = DempsterHandler()
    assert dh != None


def test_dempster_handler_2_good():
    dh = DempsterHandler()
    dh.add_categories(["t", "r", "s", "u", "e", "f"])
    dh.add_measure([Measure(["t", "r", "s"], 0.88)])
    

"""
BAD
"""