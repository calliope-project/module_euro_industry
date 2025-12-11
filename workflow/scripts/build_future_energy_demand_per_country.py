import pandas as pd
import csv


def build_future_energy_demand(
    industrial_production_per_country,
    sector_ratios,
    output_path,
):
    production = pd.read_csv(industrial_production_per_country,header=[0,1], index_col=0)/1000 #Mton/y
    ratio = pd.read_csv(sector_ratios, header=[0, 1], index_col=0)

    demand = []
    for route in production.columns:
        country_production = production[route]
        sector_ratio = ratio[route]

        
        demand_df = pd.DataFrame(
            country_production.values[:, None] * sector_ratio.values[None, :],
            index=production.index,
            columns=ratio.index
        ).unstack().to_frame()
        demand_df.columns = pd.MultiIndex.from_tuples([route],names=["sector","route"])
        demand.append(demand_df)

    energy = pd.concat(demand,axis=1)
    energy.index.names = ["carrier","country"]  
    energy = energy.unstack(level=[0,1]).to_frame("value")
    energy["unit"] = "TWh/a"
    energy.loc[
        energy.index.get_level_values("carrier").str.contains("emission"),"unit"
    ] = "MtCO2/a"

    
    
    energy.to_csv(output_path)


if __name__ == "__main__":
    build_future_energy_demand(
        industrial_production_per_country=snakemake.input.production,
        sector_ratios=snakemake.input.sector_ratio,
        output_path=snakemake.output.file,
    )