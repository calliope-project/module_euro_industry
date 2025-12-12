from scripts._helpers import load_idees_data,CARRIER_INDEX
import pandas as pd


# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630


def primary_production(idees):

    df = pd.DataFrame(index=CARRIER_INDEX)


    sector = "Aluminium - primary production"

    df[sector] = 0.0

    s_fec = idees["fec"][32:68]
    s_ued = idees["ued"][32:68]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Add aluminium  electrolysis (smelting
    df.loc["elec", sector] += s_fec["Aluminium electrolysis (smelting)"]

    # Efficiency changes due to electrification
    key = "Aluminium processing - Electric"
    eff_elec = s_ued[key] / s_fec[key]

    key = "Aluminium processing  (metallurgy e.g. cast house, reheating)"
    df.loc["elec", sector] += s_ued[key] / eff_elec

    key = "Aluminium finishing - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Aluminium finishing"] / eff_elec

    s_emi = idees["emi"][32:69]
    assert s_emi.index[0] == sector

    s_out = idees["out"][11:12]
    assert sector in str(s_out.index)

    # tCO2/t material
    df.loc["process emission", sector] = (
        s_emi["Process emissions"] / s_out["Aluminium - primary production"]
    )

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = (
        df.loc[sources, sector] * TOE_TO_MWH / s_out["Aluminium - primary production"]
    )

    df.rename(columns={sector: "Aluminium - primary production"}, inplace=True)

    return df

def secondary_production(idees):

    df = pd.DataFrame(index=CARRIER_INDEX)

    # Aluminium secondary route
    # All is converted into secondary route fully electrified.

    sector = "Aluminium - secondary production"

    df[sector] = 0.0

    s_fec = idees["fec"][70:112]
    s_ued = idees["ued"][70:112]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    key = "Secondary aluminium - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    key = "Secondary aluminium (incl. pre-treatment, remelting)"
    df.loc["elec", sector] += s_ued[key] / eff_elec

    key = "Aluminium processing - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    key = "Aluminium processing  (metallurgy e.g. cast house, reheating)"
    df.loc["elec", sector] += s_ued[key] / eff_elec

    key = "Aluminium finishing - Electric"
    eff_elec = s_ued[key] / s_fec[key]
    df.loc["elec", sector] += s_ued["Aluminium finishing"] / eff_elec

    s_out = idees["out"][12:13]
    assert sector in str(s_out.index)

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = (
        df.loc[sources, sector] * TOE_TO_MWH / s_out["Aluminium - secondary production"]
    )

    df.rename(columns={sector: "Aluminium - secondary production"}, inplace=True)

    return df


def aluminium(config,idees,output_file):
    
    primary_routes = {
        "Aluminium - primary production": primary_production,
        "Aluminium - secondary production": secondary_production,
    }

    ratios = []
    for route,info in config.items():
        
        rs = info["ratios"]
        if route in primary_routes and rs == "JRC-IDEES":
            ratios.append(
                primary_routes[route](idees)
            )
            print(f"adding {route} to ratios")
        else:
            df = pd.DataFrame(index=CARRIER_INDEX)
            df.loc[
                rs.keys(),route
            ] = list(rs.values())
            print(f"adding {route} to ratios")
            ratios.append(df)


    df = pd.concat(ratios,axis=1).fillna(0)
    df.columns = pd.MultiIndex.from_product([["Aluminium"],df.columns])
    df.to_csv(output_file)




if __name__ == "__main__":

    idees = load_idees_data(
        sector="Non Ferrous Metals",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    aluminium(
        idees=idees,
        config=snakemake.params.sector_config,
        output_file=snakemake.output.file
    )
