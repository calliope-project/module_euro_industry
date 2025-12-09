from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630


def primary_route(idees):
    # Glass production

    # This sector has process emissions.
    # Includes four subcategories:
    # (a) Melting tank
    # (b) Forming
    # (c) Annealing
    # (d) Finishing processes.
    # (a) represents 73%. (b), (d) are joined to (c).
    # Everything is electrified.

    sector = "Glass production"
    df = pd.DataFrame(index=CARRIER_INDEX)
    df[sector] = 0.0

    s_fec = idees["fec"][97:126]
    s_ued = idees["ued"][97:126]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Efficiency changes due to electrification
    key = "Glass: Electric melting tank"
    eff_elec = s_ued[key] / s_fec[key]

    df.loc["elec", sector] += s_ued["Glass: Melting tank"] / eff_elec

    key = "Glass: Annealing - electric"
    eff_elec = s_ued[key] / s_fec[key]

    sel = ["Glass: Forming", "Glass: Annealing", "Glass: Finishing processes"]
    df.loc["elec", sector] += s_ued[sel].sum() / eff_elec

    s_emi = idees["emi"][97:127]
    assert s_emi.index[0] == sector

    s_out = idees["out"][9:10]
    assert sector in str(s_out.index)

    # tCO2/t material
    df.loc["process emission", sector] += s_emi["Process emissions"] / s_out.values

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = df.loc[sources, sector] * TOE_TO_MWH / s_out.values

    df.rename(columns={sector: "primary_route"}, inplace=True)

    return df


def glass(config,idees,output_file):
    
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
    df.columns = pd.MultiIndex.from_product([["Glass production"],df.columns])
    df.to_csv(output_file)




if __name__ == "__main__":

    idees = load_idees_data(
        sector="Non-metallic mineral products",
        path=snakemake.input.idees_path,
        year=snakemake.params.reference_year,
    )
            
    glass(
        idees=idees,
        config=snakemake.params.sector_config,
        output_file=snakemake.output.file
    )