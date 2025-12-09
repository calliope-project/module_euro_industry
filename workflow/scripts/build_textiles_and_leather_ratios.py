from scripts._helpers import load_idees_data,CARRIER_INDEX,check_route_shares
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630

def textiles_and_leather(idees, config, projection_year, output_file):
    sector = "Textiles and leather"


    df = pd.DataFrame(index=CARRIER_INDEX)

    df[sector] = 0.0

    s_fec = idees["fec"][3:58]
    s_ued = idees["ued"][3:58]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    # in new JRC data zero assume old data

    eff_elec = 73.7 / 146.6
    df.loc["elec", sector] += s_ued["Textiles: Drying"] / eff_elec

    df.loc["elec", sector] += s_fec["Textiles: Electric general machinery"]
    df.loc["elec", sector] += s_fec["Textiles: Finishing Electric"]



    "Textiles: Pretreatment with steam" 
    "Textiles: Wet processing with steam"
    for carrier,data in config["steam_processing"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Textiles: Pretreatment with steam"]/data["efficiency"] * data["shares"][projection_year]
            df.loc[carrier,sector] += s_ued["Textiles: Wet processing with steam"]/data["efficiency"] * data["shares"][projection_year]


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
        info="Textiles and leather",
        routes=snakemake.params.sector_config["steam_processing"]["technology"],
        year=int(snakemake.wildcards.year)
    )

    idees = load_idees_data(
        sector="Textiles and leather",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    textiles_and_leather(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )

