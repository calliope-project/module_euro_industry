import pandas as pd
import numpy as np


def concat_ratios(alternatives,output_path):

    alternatives = pd.concat([pd.read_csv(f,index_col=0,header=[0,1]) for f in alternatives],axis=1)
    alternatives.index.name = "MWh/tMaterial"
    pd.concat([alternatives],axis=1).replace([np.inf, -np.inf], 0).to_csv(output_path)



if __name__ == "__main__":
    concat_ratios(
        alternatives=snakemake.input.alternative_routes,
        output_path=snakemake.output.file,
    )