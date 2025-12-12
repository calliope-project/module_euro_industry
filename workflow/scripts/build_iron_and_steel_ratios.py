

from scripts._helpers import load_idees_data,CARRIER_INDEX
import pandas as pd


# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630



def electric_arc(idees):
    """Calculates the electric arc route for secondary steel according to JRC-IDEES as current production route with minimal electrification on easy options

    Assumptions:
    - ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"] are assumed to be fully electrified with the current final energy consumption
    - ["Low-enthalpy heat"] is considered as low-enthalpy-heat
    - "Steel: Smelter" remains using methane (a mix of Natural gas and biogas). Fuel oil and solid is ignored
    - "Steel: Electric arc" consumes electricity as of now
    - "Steel: Furnaces, refining and rolling" is assumed to be fully electrified using the current electric option efficiency
    -  "Steel: Product finishing" is assumed to be fully electrified using the current electric option efficiency
    """

    df = pd.DataFrame(index=CARRIER_INDEX)

    ## Electric arc
    sector = "Electric arc"

    df[sector] = 0.0

    s_fec = idees["fec"][52:68]
    assert s_fec.index[0] == sector

    # - ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"] are assumed to be fully electrified with the current final energy consumption
    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.at["elec", sector] += s_fec.loc[sel].sum()

    # - ["Low-enthalpy heat"] is considered as heat
    df.at["low-enthalpy-heat", sector] += s_fec.loc["Low-enthalpy heat"]

    # - Steel: Smelter remains using methane (a mix of Natural gas and biogas). Fuel oil and solid is ignored
    subsector = "Steel: Smelters"
    s_fec = idees["fec"][63:68]
    s_ued = idees["ued"][63:68]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    # efficiency changes due to transforming all the smelters into methane
    key = "Natural gas and biogas"
    eff_met = s_ued.loc[key] / s_fec.loc[key]

    df.at["methane", sector] += s_ued[subsector] / eff_met

    subsector = "Steel: Electric arc"
    s_fec = idees["fec"][69:70]
    assert s_fec.index[0] == subsector

    df.at["elec", sector] += s_fec[subsector]

    subsector = "Steel: Furnaces, refining and rolling"
    s_fec = idees["fec"][70:77]
    s_ued = idees["ued"][70:77]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Steel: Furnaces, refining and rolling - Electric"
    eff = s_ued[key] / s_fec[key]

    # assume fully electrified, other processes scaled by used energy
    df.at["elec", sector] += s_ued[subsector] / eff

    subsector = "Steel: Product finishing"
    s_fec = idees["fec"][77:95]
    s_ued = idees["ued"][77:95]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Steel: Product finishing - Electric"
    eff = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.at["elec", sector] += s_ued[subsector] / eff

    # Process emissions (per physical output)
    s_emi = idees["emi"][52:95]
    assert s_emi.index[0] == sector

    s_out = idees["out"][7:8]
    assert s_out.index[0] == sector

    # tCO2/t material
    df.loc["process emission", sector] += s_emi["Process emissions"] / s_out[sector]

    # final energy consumption MWh/t material
    sel = CARRIER_INDEX
    df.loc[sel, sector] = df.loc[sel, sector] * TOE_TO_MWH / s_out[sector]

    df.rename(columns={sector: "Electric arc"}, inplace=True)

    return df

def integrated_steelworks(idees):
    sector = "Integrated steelworks"
    df = pd.DataFrame(index=CARRIER_INDEX)
    df[sector] = 0.0

    s_fec = idees["fec"][3:50]
    assert s_fec.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    subsector = "Steel: Sinter/Pellet-making"

    s_fec = idees["fec"][14:20]
    s_ued = idees["ued"][14:20]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    df.loc["elec", sector] += s_fec["Electricity"]

    sel = ["Natural gas and biogas", "Fuel oil"]
    df.loc["methane", sector] += s_fec[sel].sum()

    df.loc["coal", sector] += s_fec["Solids"]

    subsector = "Steel: Blast /Basic oxygen furnace"

    s_fec = idees["fec"][20:26]
    s_ued = idees["ued"][20:26]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    sel = ["Natural gas and biogas", "Fuel oil"]
    df.loc["methane", sector] += s_fec[sel].sum()

    df.loc["coal", sector] += s_fec["Solids"]

    df.loc["coke", sector] = s_fec["Coke"]

    subsector = "Steel: Furnaces, refining and rolling"

    s_fec = idees["fec"][26:33]
    s_ued = idees["ued"][26:33]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Steel: Furnaces, refining and rolling - Electric"
    eff = s_ued[key] / s_fec[key]

    # assume fully electrified, other processes scaled by used energy
    df.loc["elec", sector] += s_ued[subsector] / eff

    subsector = "Steel: Product finishing"

    s_fec = idees["fec"][33:50]
    s_ued = idees["ued"][33:50]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Steel: Product finishing - Electric"
    eff = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff

    # Process emissions (per physical output)

    s_emi = idees["emi"][3:51]
    assert s_emi.index[0] == sector

    s_out = idees["out"][6:7]
    assert s_out.index[0] == sector

    # tCO2/t material
    df.loc["process emission", sector] = s_emi["Process emissions"] / s_out[sector]

    # final energy consumption MWh/t material
    sel = CARRIER_INDEX
    df.loc[sel, sector] = df.loc[sel, sector] * TOE_TO_MWH / s_out[sector]


    df.rename(columns={sector: "Integrated steelworks"}, inplace=True)

    return df



def iron_and_steel(config,idees,output_file):
    
    primary_routes = {
        "Integrated steelworks": integrated_steelworks,
        "Electric arc": electric_arc,
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
    df.columns = pd.MultiIndex.from_product([["Iron and steel"],df.columns])
    df.to_csv(output_file)




if __name__ == "__main__":

    idees = load_idees_data(
        sector="Iron and steel",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    iron_and_steel(
        idees=idees,
        config=snakemake.params.sector_config,
        output_file=snakemake.output.file
    )


    


             
            