from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630


def primary_route(idees):

    # Ceramics & other NMM

    # This sector has process emissions.
    # Includes four subcategories:
    # (a) Mixing of raw material,
    # (b) Drying and sintering of raw material,
    # (c) Primary production process,
    # (d) Product finishing.
    # (b) represents 65% of fec and (a) 4%. So (a) is joined to (b).
    # Everything is electrified

    df = pd.DataFrame(index=CARRIER_INDEX)

    sector = "Ceramics & other NMM"

    df[sector] = 0.0

    s_fec = idees["fec"][46:95]
    s_ued = idees["ued"][46:95]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    key = "Ceramics: Microwave drying and sintering"
    # the values are zero in new JRC-data -> assume here value from JRC-2015
    # eff_elec = s_ued[key] / s_fec[key]
    eff_elec = 11.6 / 26

    sel = [
        "Ceramics: Mixing of raw material",
        "Ceramics: Drying and sintering of raw material",
    ]
    df.loc["elec", sector] += s_ued[sel].sum() / eff_elec

    key = "Ceramics: Electric kiln"
    eff_elec = s_ued[key] / s_fec[key]

    df.loc["elec", sector] += s_ued["Ceramics: Primary production process"] / eff_elec

    key = "Ceramics: Electric furnace"
    eff_elec = s_ued[key] / s_fec[key]

    df.loc["elec", sector] += s_ued["Ceramics: Product finishing"] / eff_elec

    s_emi = idees["emi"][46:96]
    assert s_emi.index[0] == sector

    s_out = idees["out"][8:9]
    assert sector in str(s_out.index)

    # tCO2/t material
    df.loc["process emission", sector] += s_emi["Process emissions"] / s_out.values

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = df.loc[sources, sector] * TOE_TO_MWH / s_out.values

    df.rename(columns={sector: "primary_route"}, inplace=True)

    return df


def ceramics(config,idees,output_file):
    
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
    df.columns = pd.MultiIndex.from_product([["Ceramics & other NMM"],df.columns])
    df.to_csv(output_file)




if __name__ == "__main__":

    idees = load_idees_data(
        sector="Non-metallic mineral products",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    ceramics(
        idees=idees,
        config=snakemake.params.sector_config,
        output_file=snakemake.output.file
    )