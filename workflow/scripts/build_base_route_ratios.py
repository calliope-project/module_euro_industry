import pandas as pd
import numpy as np


aggregate = {
    'Electric arc': 'Iron and steel',
    'Integrated steelworks': 'Iron and steel',
    'Aluminium - primary production':'Aluminium',
    'Aluminium - secondary production':'Aluminium',
}

def base_route_ratios(current_aggregated_production,current_energy_demand,output_path):

    production = pd.read_csv(current_aggregated_production,index_col=0).sum()
    demand = pd.read_csv(current_energy_demand,index_col=[0],header=[0,1]).T.groupby(level=1).sum().T

    demand.columns = [aggregate.get(c,c) for c in demand.columns]

    demand = demand.T.groupby(level=0).sum().T
    rename = {
    "waste": "biomass",
    "electricity": "elec",
    "solid": "coke",
    "gas": "methane",
    "other": "biomass",
    "liquid": "naphtha",
}   
    demand = demand.rename(rename).groupby(level=0).sum()



    ratio = demand/production*1e3 #TWh/kt to MWh/t
    ratio.to_csv(output_path)



if __name__ == "__main__":
    base_route_ratios(
        current_aggregated_production=snakemake.input.current_aggregated_production,
        current_energy_demand=snakemake.input.current_energy_demand,
        output_path=snakemake.output.file,
    )



