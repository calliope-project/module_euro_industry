import pandas as pd


def build_future_energy_demand(
    industrial_production_per_country,
    future_ratio,
    base_ratio,
    output_path,
):
    production = pd.read_csv(industrial_production_per_country,header=[0,1], index_col=0)/1000 #Mton/y
    future_ratio = pd.read_csv(future_ratio, header=[0, 1], index_col=0)
    base_ratio = pd.read_csv(base_ratio, header=[0, 1], index_col=0)



    demand = []
    for country in production.index:
        for route in production.columns:
            sector, subsector = route
            country_production = production.loc[country,route]

            # some information like the process emissions are missed. As a proxy we take the future primary_route factors as the reference
            if subsector == "base_route":
                sector_ratio = base_ratio[(country,sector)]
            else:
                sector_ratio = future_ratio[route]
            
            demand_df = (country_production * sector_ratio).to_frame()
            demand_df.columns = pd.MultiIndex.from_tuples([(country,sector, subsector)],names=["country","sector","route"])
            demand.append(demand_df)

        energy = pd.concat(demand,axis=1)
        energy.index.names = ["carrier"]  
        energy = energy.unstack().to_frame("value")

        energy["unit"] = "TWh/a"
        energy.loc[
            energy.index.get_level_values("carrier").str.contains("emission"),"unit"
        ] = "MtCO2/a"

    
    
    energy.to_csv(output_path)


if __name__ == "__main__":

    build_future_energy_demand(
        industrial_production_per_country=snakemake.input.production,
        future_ratio=snakemake.input.future_ratio,
        base_ratio = snakemake.input.base_ratio,
        output_path=snakemake.output.file,
    )