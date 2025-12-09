from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630


def machinery_equipment(idees,config,projection_year,output_file):

    sector = "Machinery equipment"

    df = pd.DataFrame(index=CARRIER_INDEX)

    df[sector] = 0.0

    s_fec = idees["fec"][3:46]
    s_ued = idees["ued"][3:46]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    key = "Mach. Eq.: Electric Foundries"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Mach. Eq.: Foundries"] / eff_elec

    key = "Mach. Eq.: Electric connection"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Mach. Eq.: Connection techniques"] / eff_elec

    key = "Mach. Eq.: Heat treatment - Electric"
    eff_elec = s_ued[key] / s_fec[key]

    df.loc["elec", sector] += s_ued["Mach. Eq.: Heat treatment"] / eff_elec

    df.loc["elec", sector] += s_fec["Mach. Eq.: General machinery"]
    df.loc["elec", sector] += s_fec["Mach. Eq.: Product finishing"]

    # Steam processing 
    # user inputs
    "Mach. Eq.: Steam processing"
    for carrier,data in config["steam_processing"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Mach. Eq.: Steam processing"]/data["efficiency"] * data["shares"][projection_year]

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
        info="Machinery equipment",
        routes=snakemake.params.sector_config["steam_processing"]["technology"],
        year=int(snakemake.wildcards.year)
    )
    
    idees = load_idees_data(
        sector="Machinery equipment",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    machinery_equipment(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )
