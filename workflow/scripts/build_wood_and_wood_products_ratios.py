from scripts._helpers import load_idees_data,CARRIER_INDEX,check_route_shares
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630
sector = "Wood and wood products"

def wood_and_wood_products(idees, config, projection_year, output_file):
    

    df = pd.DataFrame(index=CARRIER_INDEX)

    df[sector] = 0.0

    s_fec = idees["fec"][3:47]
    s_ued = idees["ued"][3:47]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    key = "Wood: Electric drying"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Wood: Drying"] / eff_elec

    df.loc["elec", sector] += s_fec["Wood: Electric mechanical processes"]
    df.loc["elec", sector] += s_fec["Wood: Finishing Electric"]

    # Steam processing is supplied with biomass
    "Wood: Specific processes with steam"
    for carrier,data in config["steam_processing"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Wood: Specific processes with steam"]/data["efficiency"] * data["shares"][projection_year]

    s_out = idees["out"][3:4]
    assert "Physical output" in str(s_out.index)

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = (
        df.loc[sources, sector] * TOE_TO_MWH / s_out["Physical output (index)"]
    )


    df.columns = pd.MultiIndex.from_product([[sector], ["primary_route"]])

    df.fillna(0).to_csv(output_file)



if __name__ == "__main__":

    # initial checkups
    check_route_shares(
        info=sector,
        routes=snakemake.params.sector_config["steam_processing"]["technology"],
        year=int(snakemake.wildcards.year)
    )

    idees = load_idees_data(
        sector=sector,
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    wood_and_wood_products(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )

