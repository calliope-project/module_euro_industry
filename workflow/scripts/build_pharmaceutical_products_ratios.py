from scripts._helpers import load_idees_data,CARRIER_INDEX,check_route_shares
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630
sector = "Chemicals Industry"

def pharmaceutical(idees, config, projection_year, output_file):
    
    df = pd.DataFrame(index=CARRIER_INDEX)

   
    sector = "Pharmaceutical products etc."

    df[sector] = 0.0

    s_fec = idees["fec"][108:114]
    assert s_fec.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    subsector = "Chemicals: High-enthalpy heat processing"

    s_fec = idees["fec"][119:132]
    s_ued = idees["ued"][119:132]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "High-enthalpy heat processing - Electric (microwave)"
    eff_elec = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff_elec

    subsector = "Chemicals: Furnaces"

    s_fec = idees["fec"][132:140]
    s_ued = idees["ued"][132:140]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Chemicals: Furnaces - Electric"
    eff = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff

    subsector = "Chemicals: Process cooling"

    s_fec = idees["fec"][140:154]
    s_ued = idees["ued"][140:154]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Chemicals: Process cooling - Electric"
    eff_elec = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff_elec

    subsector = "Chemicals: Generic electric process"

    s_fec = idees["fec"][154:155]
    s_out = idees["out"][10:11]
    assert s_fec.index[0] == subsector
    assert sector in str(s_out.index)

    df.loc["elec", sector] += s_fec[subsector]

    # tCO2/t material
    df.loc["process emission", sector] += 0.0

 
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
            
    pharmaceutical(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )

