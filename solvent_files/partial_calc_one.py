import pandas as pd
import os
from pathlib import Path
import csv

column_names = ["label", "expt_energy", "E_vac" , "E_sol0_0",  "volume_sol0_0", "surface_sol0_0", "E_sol1_0", "volume_sol1_0", "surface_sol1_0"]
#path = '/home/materialab/Pradip_files/Solvation_work/parameterization/analysis_scripts/solvent_files'
#solvent_files = [f for f in os.listdir(path) if f.endswith('.csv')]
solvent_files= ['benzylalcohol.csv']
for sol in solvent_files:

    solvent = Path(sol).stem
    df = pd.read_csv(sol, names=column_names)
    
    expt_energy = df.expt_energy.to_list()
    volume_sol0_0 = df.volume_sol0_0.to_list()
    surface_sol0_0 = df.surface_sol0_0.to_list()
    E_vac = df.E_vac.to_list()
    E_sol0_0 = df.E_sol0_0.to_list()
    E_sol1_0 = df.E_sol1_0.to_list()
    
    n = len(expt_energy) #no_of_solutes
    solvation_energy_0 = [0.0] * n
    solvation_energy_1 = [0.0] * n
    
    for i in range(n):
        if (E_sol0_0[i] == 0.0 or E_vac[i] == 0.0):
            solvation_energy_0[i] += 0.0
        elif (E_sol1_0[i] == 0.0 or E_vac[i] == 0.0):
            solvation_energy_1[i] += 0.0
        else:
            solvation_energy_0[i] += E_sol0_0[i] - E_vac[i]
            solvation_energy_1[i] += E_sol1_0[i] - E_vac[i]
   
    for i in range(n):
        if solvation_energy_0[i]== 0.0:
            expt_energy[i] = 0.0
    
    n_final = len(solvation_energy_0) - solvation_energy_0.count(0.0)
    # calculate partials
    grad_gamma = 0.0
    grad_beta = 0.0
    mse0 = 0.0
    mse1 = 0.0
    
    for i in range(n):
        grad_gamma += (solvation_energy_0[i] - expt_energy[i]) * surface_sol0_0[i] * 2.0 / n_final
        grad_beta += (solvation_energy_0[i] - expt_energy[i]) * volume_sol0_0[i] * 2.0 / n_final
        mse0 += (solvation_energy_0[i] - expt_energy[i]) ** 2 / n_final
        mse1 += (solvation_energy_1[i] - expt_energy[i]) ** 2 / n_final
    delta = 0.000001
    grad_alpha = (mse1 - mse0) / delta
    data = []
    result = {
        'solvent' : solvent,
        'mse': mse0,
        'grad_alpha': grad_alpha,
        'grad_beta': grad_beta,
        'grad_gamma': grad_gamma
    }
    
    data.append(result)
    fieldnames  = ["solvent", "mse", "grad_alpha" , "grad_beta",  "grad_gamma"]
    with open('/home/materialab/Pradip_files/Solvation_work/parameterization/analysis_scripts/partial_one.csv', 'a', encoding='UTF8',  newline='\n') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(data)
        


