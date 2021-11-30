from python_evidence.dempster_handler_2 import DempsterHandler, Measure

dh = DempsterHandler(["t", "r", "s", "u", "e", "f"])

# Measure 1
# Expected: Add omega with p = 0.12  
dh.add_measure([Measure(["t", "r", "s"], 0.88)])

# Measure 2
# Expected: add omega with p = 0.1
dh.add_measure([
                    Measure(["t", "s", "f"], 0.45), 
                    Measure(["u", "r"]   , 0.45)
                ])

# Measure 3
dh.add_measure([Measure(["u", "e", "r"], 0.65)])

print("ALOHA")
print(dh)

accumulated = dh.accumulate()
dh.print(accumulated)

print("ACCUMULATE x2")
accumulated = dh.accumulate()
dh.print(accumulated)

print("ACCUMULATE x3")
accumulated = dh.accumulate()
dh.print(accumulated)

# Plausibility and belief
print("Plausibility r:", dh.plausibility(accumulated, "r"))

print("\nBelief r: ", dh.belief(accumulated, "r"))
print("Belief t: ", dh.belief(accumulated, "t"))
print("Belief f: ", dh.belief(accumulated, "f"))

print("\nBelief - Es was ein Mann: ", dh.belief(accumulated, ["t", "r", "f"]))
print("belief - Es was eine Frau: ", dh.belief(accumulated, ["s", "u", "e"]))

print("\nPlausibility - Es was ein Mann: ", dh.plausibility(accumulated, ["t", "r", "f"]))
print("Plausibility - Es was eine Frau: ", dh.plausibility(accumulated, ["s", "u", "e"]))

print("\nZweifel(r): ", dh.doubt(accumulated, "r"))