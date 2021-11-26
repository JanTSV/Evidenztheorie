from python_evidence.dempster_handler import DempsterHandler, Measure

dh = DempsterHandler()
dh.add_categories(["t", "r", "s", "u", "e", "f"])

# Measure 1
# Expected: Add omega with p = 0.12
print("MEASURE 1")
m1 = dh.add_measure([Measure(["t", "r", "s"], 0.88)])
print(m1)

# Measure 2
# Expected: add omega with p = 0.1
print("MEASURE 2")
m2 = dh.add_measure([
                     Measure(["t", "s", "f"], 0.45), 
                     Measure(["u", "r"]   , 0.45)
                    ])
print(m2)

# Measure 3
print("MEASURE 3")
m3 = dh.add_measure([Measure(["u", "e", "r"], 0.65)])
print(m3)

print("COMBINE 1 & 2")
m12 = m1.accumulate_measures(m2)
print(m12)

print("COMBINE 12 & 3")
m123 = m12.accumulate_measures(m3)
print(m123)