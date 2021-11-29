from python_evidence.dempster_handler import DempsterHandler, Measure, MeasureCollector

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
    dh.add_measure([Measure(["e", "f"], 0.1)])
    measures = dh.accumulate_all_measures()


def test_dempster_handler_3_good():
    dh = DempsterHandler()
    measure_one = Measure(["r", "s"], 0.187)
    measure_two = Measure(["u", "e"], 0.25)
    ret = measure_one.__eq__(measure_two)
    if ret:
        print("wrong")


"""
BAD
"""