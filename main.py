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

print("ALL ACCUMULATED (same as m123)")
print(dh.accumulate_all_measures())

# Plausibility and belief
print("Plausibility r:", m123.plausibility("r"))

print("\nBelief r: ", m123.belief("r"))
print("Belief t: ", m123.belief("t"))
print("Belief f: ", m123.belief("f"))

print("\nBelief - Es was ein Mann: ", m123.belief(["t", "r", "f"]))
print("belief - Es was eine Frau: ", m123.belief(["s", "u", "e"]))

print("\nPlausibility - Es was ein Mann: ", m123.plausibility(["t", "r", "f"]))
print("Plausibility - Es was eine Frau: ", m123.plausibility(["s", "u", "e"]))

print("\nZweifel(r): ", m123.doubt("r"))