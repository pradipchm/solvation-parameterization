from aiida_environ.workflows.pw.parameterization import ParameterizationWorkChain
import csv
from pathlib import Path

#### Get all the parameterizationWorkChain pks

qb = QueryBuilder()
qb.append(ParameterizationWorkChain)
WorkChain_nodes = qb.all()[-20:]
no_of_nodes = len(WorkChain_nodes)


ALPHA   = 1.14

#### for each parameterizationWorkChain collect the data in the corresponding solvent file


for i in range(no_of_nodes):
    solute_labels= []
    qb = QueryBuilder()
    eps = load_node(WorkChain_nodes[i][0].pk).inputs.environ_solution["ENVIRON"]["env_static_permittivity"]
    qb.append(Dict, filters={"attributes.eps": {'==': eps}})
    solvent = qb.all()[0][0].label
    expt_energy_all =  load_node(WorkChain_nodes[i][0].pk).inputs.expt_energy[:]  ##solutes pks, experimental energies,##
    solute_pks = load_node(WorkChain_nodes[i][0].pk).inputs.structure_pks[:]
    for pks in solute_pks:
        solute_labels.append(load_node(pks).label)
    
    ### Get all CalcJobNode ids
    
    filtered = filter(lambda x: x.process_class.__name__ == 'EnvPwCalculation', WorkChain_nodes[i][0].called_descendants)
    CalcJobNode_ids = [n.id for n in list(filtered)]

    data= []
    solutes = {}

    
    #### collect data from each calc job node 
    for calc_id in CalcJobNode_ids:

            label = load_node(calc_id).inputs.structure.label

            if label not in solutes: solutes[label] = {} 

            solutes[label]['label'] = label

            index_for_solute = solute_labels.index(label)

            solutes[label]['expt_energy'] = expt_energy_all[index_for_solute]


            if load_node(calc_id).attributes["exit_status"] == 0:
                
                ### Energy(E_V0) at Vacuum
                if load_node(calc_id).inputs.environ_parameters.attributes['ENVIRON']['env_static_permittivity'] ==1.0:
                    E_vac = load_node(calc_id).outputs.output_parameters.attributes['energy']
                    ###append into solute E_V0
                    solutes[label]['E_vac'] = E_vac
                else:
                    ### Energy(E_sol0_0) in solution with alpha
                    if load_node(calc_id).inputs.environ_parameters.attributes['BOUNDARY']['alpha'] == ALPHA:
                        E_sol0_0 = load_node(calc_id).outputs.output_parameters.attributes['energy']
                        volume_sol0_0 = load_node(calc_id).outputs.output_parameters.attributes['qm_volume']
                        surface_sol0_0 = load_node(calc_id).outputs.output_parameters.attributes['qm_surface']
                        ##append E_sol0_0, volume_sol0_0, surface_sol0_0
                        solutes[label]['E_sol0_0']= E_sol0_0
                        solutes[label]['volume_sol0_0'] = volume_sol0_0[0]
                        solutes[label]['surface_sol0_0'] = surface_sol0_0[0]
                    else:
                        ### Energy(Esol1_0) in solution with alpha + d(alpha)
                        E_sol1_0 = load_node(calc_id).outputs.output_parameters.attributes['energy']
                        volume_sol1_0 = load_node(calc_id).outputs.output_parameters.attributes['qm_volume']
                        surface_sol1_0 = load_node(calc_id).outputs.output_parameters.attributes['qm_surface']
                        ###append Esol1_0, volume_sol1_0, surface_sol1_0
                        solutes[label]['E_sol1_0'] = E_sol1_0
                        solutes[label]['volume_sol1_0'] = volume_sol1_0[0]
                        solutes[label]['surface_sol1_0'] = surface_sol1_0[0]
            else:
                
                solutes[label]['E_vac'] = "NA"
                solutes[label]['E_sol0_0']  = "NA"
                solutes[label]['volume_sol0_0'] = "NA"
                solutes[label]['surface_sol0_0'] = "NA"
                solutes[label]['E_sol1_0'] = "NA"
                solutes[label]['volume_sol1_0'] = "NA"
                solutes[label]['surface_sol1_0'] = "NA"
 
    #post-processing
    for solute_data in solutes.values():
        data.append(solute_data)

    print(data)

    ###open a csv file with solvent name and write
    fieldnames  = ["label", "expt_energy", "E_vac" , "E_sol0_0",  "volume_sol0_0", "surface_sol0_0", "E_sol1_0", "volume_sol1_0", "surface_sol1_0"]
    file_name = '{}.csv'.format(solvent)
    file_path = Path(file_name)
    if file_path.is_file():
        with open(f'{solvent}.csv', 'a', encoding='UTF8',  newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(data)
    else:
        with open(f'{solvent}.csv', 'w', encoding='UTF8',  newline='\n') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

