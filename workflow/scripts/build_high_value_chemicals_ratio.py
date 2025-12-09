

from scripts._helpers import load_idees_data,CARRIER_INDEX
import pandas as pd
import country_converter as coco




cc = coco.CountryConverter()
eu27 = cc.EU27as("ISO2").ISO2.tolist()

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630
sector = "Chemicals Industry"





def primary_route(idees,**kwargs):
    params = kwargs["params"]
    year = kwargs["year"]

    df = pd.DataFrame(index=CARRIER_INDEX)

    # Basic chemicals
    sector = "Basic chemicals"

    df[sector] = 0.0

    s_fec = idees["fec"][3:9]
    assert s_fec.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    subsector = "Chemicals: Feedstock (energy used as raw material)"
    # There are Solids, Refinery gas, LPG, Diesel oil, Fuel oil,
    # Other liquids, Naphtha, Natural gas for feedstock.
    # Naphta represents 47%, methane 17%. LPG (18%) solids, refinery gas,
    # diesel oil, Fuel oils and other liquids are assimilated to Naphtha

    s_fec = idees["fec"][14:23]
    assert s_fec.index[0] == subsector

    df.loc["naphtha", sector] += s_fec["Naphtha"]

    df.loc["methane", sector] += s_fec["Natural gas"]

    # LPG and other feedstock materials are assimilated to naphtha
    # since they will be produced through Fischer-Tropsch process
    sel = [
        "Solids",
        "Refinery gas",
        "LPG",
        "Diesel oil",
        "Fuel oil",
        "Other liquids",
    ]
    df.loc["naphtha", sector] += s_fec[sel].sum()

    subsector = "Chemicals: Steam processing"
    # All the final energy consumption in the steam processing is
    # converted to methane, since we need >1000 C temperatures here.
    # The current efficiency of methane is assumed in the conversion.

    s_fec = idees["fec"][23:34]
    s_ued = idees["ued"][23:34]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    # efficiency of natural gas
    eff_ch4 = s_ued["Natural gas and biogas"] / s_fec["Natural gas and biogas"]

    # replace all fec by methane
    df.loc["methane", sector] += s_ued[subsector] / eff_ch4

    subsector = "Chemicals: Furnaces"

    s_fec = idees["fec"][34:42]
    s_ued = idees["ued"][34:42]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    # efficiency of electrification
    key = "Chemicals: Furnaces - Electric"
    eff_elec = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff_elec

    subsector = "Chemicals: Process cooling"

    s_fec = idees["fec"][42:56]
    s_ued = idees["ued"][42:56]
    assert s_fec.index[0] == subsector
    assert s_ued.index[0] == subsector

    key = "Chemicals: Process cooling - Electric"
    eff_elec = s_ued[key] / s_fec[key]

    # assume fully electrified
    df.loc["elec", sector] += s_ued[subsector] / eff_elec

    subsector = "Chemicals: Generic electric process"

    s_fec = idees["fec"][56:57]
    assert s_fec.index[0] == subsector

    df.loc["elec", sector] += s_fec[subsector]

    # Process emissions

    # Correct everything by subtracting 2019's ammonia demand and
    # putting in ammonia demand for H2 and electricity separately

    s_emi = idees["emi"][3:58]
    assert s_emi.index[0] == sector

    # convert from MtHVC/a to ktHVC/a
    s_out = params["HVC_production_today"] * 1e3

    # tCO2/t material
    df.loc["process emission", sector] += (
        s_emi["Process emissions"]
        - params["petrochemical_process_emissions"] * 1e3
        - params["NH3_process_emissions"] * 1e3
    ) / s_out

    # emissions originating from feedstock, could be non-fossil origin
    # tCO2/t material
    df.loc["process emission from feedstock", sector] += (
        params["petrochemical_process_emissions"] * 1e3
    ) / s_out

    # convert from ktoe/a to GWh/a
    sources = CARRIER_INDEX
    df.loc[sources, sector] *= TOE_TO_MWH

    # subtract ammonia energy demand (in ktNH3/a)
    ammonia = pd.read_csv(params["ammonia_production"], index_col=0)
    ammonia_total = ammonia.loc[
        ammonia.index.intersection(eu27), str(max(2018, year))
    ].sum()
    df.loc["methane", sector] -= ammonia_total * params["MWh_CH4_per_tNH3_SMR"]
    df.loc["elec", sector] -= ammonia_total * params["MWh_elec_per_tNH3_SMR"]

    # subtract chlorine demand (in MtCl/a)
    chlorine_total = params["chlorine_production_today"]
    df.loc["hydrogen", sector] -= chlorine_total * params["MWh_H2_per_tCl"] * 1e3
    df.loc["elec", sector] -= chlorine_total * params["MWh_elec_per_tCl"] * 1e3

    # subtract methanol demand (in MtMeOH/a)
    methanol_total = params["methanol_production_today"]
    df.loc["methane", sector] -= methanol_total * params["MWh_CH4_per_tMeOH"] * 1e3
    df.loc["elec", sector] -= methanol_total * params["MWh_elec_per_tMeOH"] * 1e3

    # MWh/t material
    df.loc[sources, sector] = df.loc[sources, sector] / s_out

    df.rename(columns={sector: "HVC"}, inplace=True)

    # HVC mechanical recycling

    sector = "HVC (mechanical recycling)"
    df[sector] = 0.0
    df.loc["elec", sector] = params["MWh_elec_per_tHVC_mechanical_recycling"]

    # HVC chemical recycling

    sector = "HVC (chemical recycling)"
    df[sector] = 0.0
    df.loc["elec", sector] = params["MWh_elec_per_tHVC_chemical_recycling"]

    # Ammonia

    sector = "Ammonia"
    df[sector] = 0.0

    df.loc["ammonia", sector] = params["MWh_NH3_per_tNH3"]


    # Chlorine
    sector = "Chlorine"
    df[sector] = 0.0
    df.loc["hydrogen", sector] = params["MWh_H2_per_tCl"]
    df.loc["elec", sector] = params["MWh_elec_per_tCl"]

    # Methanol

    sector = "Methanol"
    df[sector] = 0.0
    df.loc["methanol", sector] = params["MWh_MeOH_per_tMeOH"]


    df.loc[sources, sector] = df.loc[sources, sector] / s_out

    df.rename(columns={sector: "HVC"}, inplace=True)

    return df




def high_value_chemicals(config,idees,output_file,params,reference_year):
    
    primary_routes = {
        "primary_route": primary_route,
    }


    ratios = []
    for route,info in config.items():
        
        rs = info["ratios"]
        if route in primary_routes and rs == "JRC-IDEES":
            ratios.append(
                primary_routes[route](idees,params=params,year=reference_year)
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
    df.columns = pd.MultiIndex.from_product([["High Value Chemicals"],df.columns])
    df.to_csv(output_file)




if __name__ == "__main__":

    idees = load_idees_data(
        sector=sector,
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )

    params = snakemake.params.extra_data
    params["ammonia_production"] = snakemake.input.ammonia_production


    high_value_chemicals(
        idees=idees,
        config=snakemake.params.sector_config,
        params=params,
        output_file=snakemake.output.file,
        reference_year=params["reference_year"],
    )


    


             
            