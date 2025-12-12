import pandas as pd
import numpy as np
from collections import defaultdict

def reverse_dict(d):
    rev = defaultdict(list)
    for k, v in d.items():
        rev[v].append(k)
    return dict(rev)

aggregate = {
    'Electric arc': 'Iron and steel',
    'Integrated steelworks': 'Iron and steel',
    'Aluminium - primary production':'Aluminium',
    'Aluminium - secondary production':'Aluminium',
}

reverse_aggregate = reverse_dict(aggregate)





def base_route_ratios(current_production,current_energy_demand,future_ratio,output_path):

    production = pd.read_csv(current_production,index_col=0)
    demand = pd.read_csv(current_energy_demand,index_col=[0],header=[0,1])
    future_ratio = pd.read_csv(future_ratio,index_col=[0],header=[0,1])

    rename = {
    "waste": "biomass",
    "electricity": "elec",
    "solid": "coke",
    "gas": "methane",
    "other": "biomass",
    "liquid": "naphtha",
}   
    demand = demand.rename(rename).groupby(level=0).sum()
    missing = future_ratio.index.difference(demand.index)

    # add missing
    demand = demand.reindex(index=demand.index.union(missing),fill_value=0)

    for country,sector in demand.columns:

        if sector in aggregate:
            get = future_ratio.loc[missing].xs(sector,level=1,axis=1).values.ravel()

        else:
            get = future_ratio.loc[missing,(sector,"primary_route")].values.ravel()

        demand.loc[missing,(country,sector)] = get * production.loc[country,sector]


    # aggregate demand
    demand.columns = pd.MultiIndex.from_tuples([(country,aggregate.get(sector,sector)) for country,sector in demand.columns])
    demand = demand.T.groupby(level=[0,1]).sum().T

    # aggregate_production
    production = production.T.rename(aggregate).groupby(level=0).sum().unstack()

    ratio = demand.div(production,axis=1).replace([np.inf, -np.inf], 0).fillna(0) * 1e3 #TWh/kt to MWh/t

    ratio.to_csv(output_path)



if __name__ == "__main__":
    base_route_ratios(
        current_production=snakemake.input.current_aggregated_production,
        current_energy_demand=snakemake.input.current_energy_demand,
        future_ratio = snakemake.input.future_ratio,
        output_path=snakemake.output.file,

    )



