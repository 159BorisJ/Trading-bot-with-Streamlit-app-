from tabulate import tabulate

strategies = ["strategy1", "strategy2", "strategy3"]
comodities = ["comodity1", "comodity2", "comodity3"]

# Inicializácia dát pre tabuľku
data = []

# Naplnenie riadkov tabuľky
for c in comodities:
    row = {"comodities": c}  # Pridaj názov komodity do stĺpca "comodities"
    for s in strategies:
        row[s] = 0  # Predvolená hodnota pre stratégie
    data.append(row)

# Výpočet súčtov pre každú stratégiu
# totals = [sum(values) for values in zip(data["comodity1"], data["comodity2"], data["comodity3"])]

# Pridanie riadku pre súčty do tabuľky
# data["Total"] = totals

print(tabulate(data, headers="keys", tablefmt="fancy_grid"))

