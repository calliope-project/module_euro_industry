from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630

def primary_route(idees):
    
    # Cement

    # This sector has process-emissions.
    # Includes three subcategories:
    # (a) Grinding, milling of raw material,
    # (b) Pre-heating and pre-calcination,
    # (c) clinker production (kilns),
    # (d) Grinding, packaging.
    # (b)+(c) represent 94% of fec. So (a) is joined to (b) and (d) is joined to (c).
    # Temperatures above 1400C are required for processing limestone and sand into clinker.
    # Everything (except current electricity and heat consumption and existing biomass)
    # is transformed into methane for high T.

    sector = "Cement"

    df = pd.DataFrame(index=CARRIER_INDEX)

    df[sector] = 0.0

    s_fec = idees["fec"][3:25]
    s_ued = idees["ued"][3:25]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # pre-processing: keep existing elec and biomass, rest to methane
    df.loc["elec", sector] += s_fec["Cement: Grinding, milling of raw material"]
    df.loc["biomass", sector] += s_fec["Biomass and waste"]
    df.loc["methane", sector] += (
        s_fec["Cement: Pre-heating and pre-calcination"] - s_fec["Biomass and waste"]
    )

    subsector = "Cement: Clinker production (kilns)"

    s_fec = idees["fec"][23:32]
    s_ued = idees["ued"][23:32]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    df.loc["biomass", sector] += s_fec["Biomass and waste"]
    df.loc["methane", sector] += (
        s_fec["Cement: Clinker production (kilns)"] - s_fec["Biomass and waste"]
    )
    df.loc["elec", sector] += s_fec["Cement: Grinding, packaging and precasting"]

    # Process emissions

    # come from calcination of limestone to chemically reactive calcium oxide (lime).
    # Calcium carbonate -> lime + CO2
    # CaCO3  -> CaO + CO2

    s_emi = idees["emi"][3:45]
    assert s_emi.index[0] == sector

    s_out = idees["out"][7:8]
    assert sector in str(s_out.index)

    # tCO2/t material
    df.loc["process emission", sector] += s_emi["Process emissions"] / s_out.values

    # MWh/t material
    sources =CARRIER_INDEX
    df.loc[sources, sector] = df.loc[sources, sector] * TOE_TO_MWH / s_out.values


    df.rename(columns={sector: "primary_route"}, inplace=True)

    return df


def cement(config,idees,output_file):
    
    primary_routes = {
        "primary_route": primary_route,
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
    df.columns = pd.MultiIndex.from_product([["Cement"],df.columns])
    df.to_csv(output_file)




if __name__ == "__main__":

    idees = load_idees_data(
        sector="Non-metallic mineral products",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    cement(
        idees=idees,
        config=snakemake.params.sector_config,
        output_file=snakemake.output.file
    )

