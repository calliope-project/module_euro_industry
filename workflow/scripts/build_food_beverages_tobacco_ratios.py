from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630


def food_beverages_tobacco(idees,config,projection_year,output_file):
    """
    Calculates the energy consumption for the food, beverages, and tobacco
    sector, assuming complete electrification of all processes. This sector
    does not have any process emissions associated with it.

    Returns:
        pd.DataFrame: A DataFrame containing the energy consumption (in MWh/t material)
                      for the food, beverages, and tobacco sector.
    """

    sector = "Food, beverages and tobacco"


    df = pd.DataFrame(index=CARRIER_INDEX)

    df[sector] = 0.0

    s_fec = idees["fec"][3:79]
    s_ued = idees["ued"][3:79]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification

    key = "Food: Direct Heat - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Food: Oven (direct heat)"] / eff_elec

    key = "Food: Process Heat - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Food: Specific process heat"] / eff_elec

    key = "Food: Electric drying"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Food: Drying"] / eff_elec

    key = "Food: Electric cooling"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += (
        s_ued["Food: Process cooling and refrigeration"] / eff_elec
    )

    # add electricity from process that is already electrified
    df.loc["elec", sector] += s_fec["Food: Electric machinery"]

    s_out = idees["out"][3:4]
    assert "Physical output" in str(s_out.index)

    # user specific inputs
    "Food: Steam processing"
    for carrier,data in config["steam_processing"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Food: Steam processing"]/data["efficiency"] * data["shares"][projection_year]

    # MWh/t material
    df.loc[CARRIER_INDEX, sector] = (
        df.loc[CARRIER_INDEX, sector] * TOE_TO_MWH / s_out["Physical output (index)"]
    )


    df.columns = pd.MultiIndex.from_product([[sector], ["primary_route"]])

    df.fillna(0).to_csv(output_file)




if __name__ == "__main__":
    # initial checkups
    check_route_shares(
        info="Food, beverages and tobacco",
        routes=snakemake.params.sector_config["steam_processing"]["technology"],
        year=int(snakemake.wildcards.year)
    )
    
    idees = load_idees_data(
        sector="Food, beverages and tobacco",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
            
            
    food_beverages_tobacco(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )
