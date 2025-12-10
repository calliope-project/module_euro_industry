import pandas as pd
import numpy as np


def concat_ratios(base,alternatives,output_path):
    base = pd.read_csv(base,index_col=0,header=0)
    base.columns = pd.MultiIndex.from_product([base.columns,["base_route"]])
    alternatives = pd.concat([pd.read_csv(f,index_col=0,header=[0,1]) for f in alternatives],axis=1)
    base.index.name = "MWh/tMaterial"
    alternatives.index.name = "MWh/tMaterial"

    pd.concat([base,alternatives],axis=1).replace([np.inf, -np.inf], 0).fillna(0).to_csv(output_path)



if __name__ == "__main__":
    concat_ratios(
        base=snakemake.input.base_route,
        alternatives=snakemake.input.alternative_routes,
        output_path=snakemake.output.file,
    )