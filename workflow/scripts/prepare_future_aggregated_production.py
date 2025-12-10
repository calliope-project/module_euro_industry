"""Build future industrial production per country.

Description
-------

This rule uses the ``industrial_production_per_country.csv`` file and the expected recycling rates to calculate the future production of the industrial sectors.

**St_primary_fraction**
The fraction of steel that is coming from primary production. This is more energy intensive than recycling steel (secondary production).

**DRI_fraction**
The fraction of primary steel that is produced in DRI plants.

**Al_primary_fraction**
The fraction of aluminium that is coming from primary production. This is more energy intensive than recycling aluminium (secondary production).

**HVC_primary_fraction**
The fraction of high value chemicals that are coming from primary production (crude oil or Fischer Tropsch).

**HVC_mechanical_recycling_fraction**
The fraction of high value chemicals that are coming from mechanical recycling.

**HVC_chemical_recycling_fraction**
The fraction of high value chemicals that are coming from chemical recycling.

If not already present, the information is added as new column in the output file.

The unit of the production is kt/a.
"""

import sys
from typing import TYPE_CHECKING, Any

import pandas as pd
from _helpers import get,check_route_shares

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")


SECTOR_ALLIAS = {
    "HVC": "high_value_chemicals",
    "Iron and steel": "iron_and_steel",
    "Aluminium": "aluminium",
    "Cement": "cement",
    "Ceramics & other NMM": "ceramics",
    "Glass production": "glass",
    "Food, beverages and tobacco": "food_beverages_tobacco",
    "Transport equipment": "transport_equipment",
    "Machinery equipment": "machinery_equipment",
    "Textiles and leather": "textiles_and_leather",
    "Wood and wood products": "wood_and_wood_products",
    "Other industrial sectors": "other_industrial_sectors",
    "Pulp production": "pulp_production",
    "Paper production": "paper_production",
    "Printing and media reproduction": "printing_and_media_reproduction",
    "Pharmaceutical products etc.": "pharmaceutical_products",
    "Alumina production": "alumina_production",
    "Chlorine":"chlorine",
    "Ammonia": "ammonia" ,
    "Methanol":"methanol",
    "Other chemicals": "other_chemicals",
    "Other non-ferrous metals": "other_non_ferrous_metals"
}


def main(params: dict, year: int, aggregated_production, output_file: str):
    
    projections = params[year]
    production = pd.read_csv(aggregated_production, index_col=0)
    future_production = []

    default = projections["default"]
    production_level = projections["production_level"]

    if isinstance(production_level, str):
        production_level = pd.read_csv(production_level, index_col=0)
    else:
        production_level = pd.DataFrame.from_dict(production_level, orient="index")


    # check if all countries are in production level
    missing_countries = production.index.difference(production_level.index)
    if missing_countries.any():
        production_level.loc[missing_countries] = default

    # check if all industries are in production level
    missing_industries = production.columns.difference(production_level.columns)
    if missing_industries.any():
        production_level[missing_industries] = default


    shares = projections["shares"]

    for sector in production.columns:

        if sum(shares[SECTOR_ALLIAS[sector]].values()) != 1:
            raise ValueError(f"The sum of the production routes for {sector}, is not equal to 1.")

        sector_ratio = production_level[sector]
        sector_production = production[sector]

        for k,v in shares[SECTOR_ALLIAS[sector]].items():
            if v!=0:
                fd = (sector_production*sector_ratio*v).to_frame()
                fd.columns = pd.MultiIndex.from_tuples([(sector,k)])
                future_production.append(fd)

    future_production = pd.concat(future_production, axis=1)
    future_production.to_csv(output_file, float_format="%.2f")

if __name__ == "__main__":

    main(
        params=snakemake.params.industry,
        year=int(snakemake.wildcards.year),
        aggregated_production=snakemake.input.current,
        output_file=snakemake.output.future
    )
