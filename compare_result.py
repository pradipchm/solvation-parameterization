import pandas as pd

column_names = ["solvent_acree", "solvent_trular", "eps"]
df = pd.read_csv("sol_ener_comparison.csv", names=column_names)

solvent_acree = df.solvent_acree.to_list()

lf = df.groupby(['solvent_trular']).mean()
eps =  lf.eps.to_list()
solvent_trular= []
for i, row in lf.iterrows():
    solvent_trular.append(i)


for solvent in solvent_acree:
    if str(solvent).lower() in solvent_trular:
        index = solvent_trular.index(str(solvent).lower())
        eps_acree = eps[index]
    else:
        eps_acree = 0.0
    print(eps_acree)

        
