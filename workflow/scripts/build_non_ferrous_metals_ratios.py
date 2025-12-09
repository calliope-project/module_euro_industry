from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630
sector = "Non Ferrous Metals"
# Except Aluminium production

def non_ferrous_metals(idees, config, projection_year, output_file):
    
    df = pd.DataFrame(index=CARRIER_INDEX)

    # Alumina

    # High-enthalpy heat is converted to user given inputs.
    # Process heat at T>500C is required here.
    # Refining is electrified.
    # There are no process emissions associated to Alumina manufacturing.

    sector = "Alumina production"

    df[sector] = 0.0

    s_fec = idees["fec"][3:31]
    s_ued = idees["ued"][3:31]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # High-enthalpy heat is transformed into methane

    s_fec = idees["fec"][14:25]
    s_ued = idees["ued"][14:25]
    assert s_fec.index[0] == "Alumina production: High-enthalpy heat"
    assert s_ued.index[0] == "Alumina production: High-enthalpy heat"

    "Alumina production: High-enthalpy heat"
    for carrier,data in config["alumina_high_enthalpy_heat"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Alumina production: High-enthalpy heat"]/data["efficiency"] * data["shares"][projection_year]

    # Efficiency changes due to electrification

    s_fec = idees["fec"][25:31]
    s_ued = idees["ued"][25:31]
    assert s_fec.index[0] == "Alumina production: Refining"
    assert s_ued.index[0] == "Alumina production: Refining"

    eff_elec = s_ued["Electricity"] / s_fec["Electricity"]
    df.loc["elec", sector] += s_ued["Alumina production: Refining"] / eff_elec

    s_out = idees["out"][9:10]
    assert sector in str(s_out.index)

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = (
        df.loc[sources, sector] * TOE_TO_MWH / s_out["Alumina production (kt)"]
    )

    # Other non-ferrous metals

    sector = "Other non-ferrous metals"

    df[sector] = 0.0

    s_fec = idees["fec"][113:156]
    s_ued = idees["ued"][113:156]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    key = "Metal production - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Other Metals: production"] / eff_elec

    key = "Metal processing - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    key = "Metal processing  (metallurgy e.g. cast house, reheating)"
    df.loc["elec", sector] += s_ued[key] / eff_elec

    key = "Metal finishing - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Metal finishing"] / eff_elec

    s_emi = idees["emi"][113:157]
    assert s_emi.index[0] == sector

    s_out = idees["out"][13:14]
    assert sector in str(s_out.index)

    # tCO2/t material
    df.loc["process emission", sector] = (
        s_emi["Process emissions"] / s_out["Other non-ferrous metals (kt lead eq.)"]
    )

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = (
        df.loc[sources, sector]
        * TOE_TO_MWH
        / s_out["Other non-ferrous metals (kt lead eq.)"]
    )

    df.columns = pd.MultiIndex.from_product([df.columns.tolist(), ["primary_route"]])

    df.fillna(0).to_csv(output_file)

if __name__ == "__main__":

    for k,v in snakemake.params.sector_config.items():
        check_route_shares(
            info=sector + "-->" + k,
            routes=v["technology"],
            year=int(snakemake.wildcards.year)
        )
    
    idees = load_idees_data(
        sector=sector,
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )         
            
    non_ferrous_metals(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )
