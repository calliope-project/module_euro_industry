from scripts._helpers import check_route_shares, load_idees_data,CARRIER_INDEX
import pandas as pd

# GWh/ktoe OR MWh/toe
TOE_TO_MWH = 11.630
sector = "Pulp, paper and printing"

def pulp_paper_printing(idees,config, projection_year, output_file):
    """
    Models the energy consumption for the pulp, paper, and printing sector,
    assuming complete electrification of all processes. This sector does not
    have any process emissions associated with it.

    Returns:
        pd.DataFrame: A DataFrame containing the energy consumption (in MWh/t material)
                      for the pulp, paper, and printing sector.
    """



    df = pd.DataFrame(index=CARRIER_INDEX)

    # Pulp production

    # Includes three subcategories:
    # (a) Wood preparation, grinding;
    # (b) Pulping;
    # (c) Cleaning.
    #
    # (b) Pulping is either biomass or electric; left like this (dominated by biomass).
    # (a) Wood preparation, grinding and (c) Cleaning represent only 10% of their current
    # energy consumption is assumed to be electrified without any change in efficiency

    sector = "Pulp production"

    df[sector] = 0.0

    s_fec = idees["fec"][3:29]
    s_ued = idees["ued"][3:29]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Industry-specific
    sel = [
        "Pulp: Wood preparation, grinding",
        "Pulp: Cleaning",
        "Pulp: Pulping electric",
    ]
    df.loc["elec", sector] += s_fec[sel].sum()

    # Efficiency changes due to biomass
    "Pulp: Pulping thermal"
    for carrier,data in config["pulping"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Pulp: Pulping thermal"]/data["efficiency"] * data["shares"][projection_year]

    s_out = idees["out"][8:9]
    assert sector in str(s_out.index)

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = (
        df.loc[sources, sector] * TOE_TO_MWH / s_out["Pulp production (kt)"]
    )

    # Paper production

    # Includes three subcategories:
    # (a) Stock preparation;
    # (b) Paper machine;
    # (c) Product finishing.
    #
    # (b) Paper machine and (c) Product finishing are left electric
    # and thermal is moved to biomass. The efficiency is calculated
    # from the pulping process that is already biomass.
    #
    # (a) Stock preparation represents only 7% and its current energy
    # consumption is assumed to be electrified without any change in efficiency.

    sector = "Paper production"

    df[sector] = 0.0

    s_fec = idees["fec"][30:80]
    s_ued = idees["ued"][30:80]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]

    # Industry-specific
    df.loc["elec", sector] += s_fec["Paper: Stock preparation"]

    # add electricity from process that is already electrified
    df.loc["elec", sector] += s_fec["Paper: Paper machine - Electricity"]

    # add electricity from process that is already electrified
    df.loc["elec", sector] += s_fec["Paper: Product finishing - Electricity"]

    s_fec = idees["fec"][55:66]
    s_ued = idees["ued"][55:66]
    assert s_fec.index[0] == "Paper: Paper machine - Steam use"
    assert s_ued.index[0] == "Paper: Paper machine - Steam use"


    "Paper: Paper machine - Steam use"
    for carrier,data in config["paper_machine_steam_use"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Paper: Paper machine - Steam use"]/data["efficiency"] * data["shares"][projection_year]


    s_fec = idees["fec"][68:79]
    s_ued = idees["ued"][68:79]
    assert s_fec.index[0] == "Paper: Product finishing - Steam use"
    assert s_ued.index[0] == "Paper: Product finishing - Steam use"

    "Paper: Product finishing - Steam use"
    for carrier,data in config["paper_finishing_steam_use"]["technology"].items():
        if data["shares"][projection_year] != 0:
            df.loc[carrier,sector] += s_ued["Paper: Product finishing - Steam use"]/data["efficiency"] * data["shares"][projection_year]

    s_out = idees["out"][9:10]
    assert sector in str(s_out.index)

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = df.loc[sources, sector] * TOE_TO_MWH / s_out.values

    # Printing and media reproduction

    # (a) Printing and publishing is assumed to be
    # electrified without any change in efficiency.

    sector = "Printing and media reproduction"

    df[sector] = 0.0

    s_fec = idees["fec"][81:93]
    s_ued = idees["ued"][81:93]
    assert s_fec.index[0] == sector
    assert s_ued.index[0] == sector

    sel = ["Lighting", "Air compressors", "Motor drives", "Fans and pumps"]
    df.loc["elec", sector] += s_fec[sel].sum()
    df.loc["elec", sector] += s_ued[sel].sum()

    df.loc["low-enthalpy-heat", sector] += s_fec["Low-enthalpy heat"]
    df.loc["low-enthalpy-heat", sector] += s_ued["Low-enthalpy heat"]

    # Industry-specific
    df.loc["elec", sector] += s_fec["Printing and publishing"]
    df.loc["elec", sector] += s_ued["Printing and publishing"]

    s_out = idees["out"][10:11]
    assert sector in str(s_out.index)

    # MWh/t material
    sources = CARRIER_INDEX
    df.loc[sources, sector] = df.loc[sources, sector] * TOE_TO_MWH / s_out.values

    df.columns = pd.MultiIndex.from_product([df.columns.tolist(), ["primary_route"]])

    df.fillna(0).to_csv(output_file)


if __name__ == "__main__":
    # initial checkups


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


            
    pulp_paper_printing(
        idees=idees,
        config=snakemake.params.sector_config,
        projection_year=int(snakemake.wildcards.year),
        output_file=snakemake.output.file
    )
