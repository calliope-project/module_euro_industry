from scripts._helpers import load_idees_data,CARRIER_INDEX,check_route_shares
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630
sector = "Chemicals Industry"

def other_chemicals(idees, config, projection_year, output_file):
    
    df = pd.DataFrame(index=CARRIER_INDEX)

    # Other chemicals
    sector = "Other chemicals"

    df[sector] = 0.0

    s_fec = idees["fec"][59:65]
    assert s_fec.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    subsector = "Chemicals: High-enthalpy heat processing"

    s_fec = idees["fec"][70:83]
    s_ued = idees["ued"][70:83]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "High-enthalpy heat processing - Electric (microwave)"
    eff_elec = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff_elec

    subsector = "Chemicals: Furnaces"

    s_fec = idees["fec"][83:92]
    s_ued = idees["ued"][83:92]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Chemicals: Furnaces - Electric"
    eff_elec = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff_elec

    subsector = "Chemicals: Process cooling"

    s_fec = idees["fec"][91:105]
    s_ued = idees["ued"][91:105]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Chemicals: Process cooling - Electric"
    eff = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff

    subsector = "Chemicals: Generic electric process"

    s_fec = idees["fec"][105:106]
    assert s_fec.index[0] == subsector

    df.loc["elec", sector] += s_fec[subsector]

    # Process emissions

    s_emi = idees["emi"][59:107]
    s_out = idees["out"][9:10]
    assert s_emi.index[0] == sector
    assert sector in str(s_out.index)

    # tCO2/t material
    df.loc["process emission", sector] += s_emi["Process emissions"] / s_out.values

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = df.loc[sources, sector] * TOE_TO_MWH / s_out.values


    df.columns = pd.MultiIndex.from_product([[sector], ["primary_route"]])

    df.fillna(0).to_csv(output_file)
    
if __name__ == "__main__":


    idees = load_idees_data(
        sector=sector,
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    other_chemicals(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )

