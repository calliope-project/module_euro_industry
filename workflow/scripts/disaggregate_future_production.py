# Adapted from PyPSA-Eur (https://github.com/pypsa/pypsa-eur)
# Copyright (c) 2017-2024 The PyPSA-Eur Authors
# Licensed under the MIT License
# Commit: 822a92729e6973aa3aff741d6c94f1da2c75e8b2
"""Build industrial production per region in the shape file."""

import sys
from itertools import product
from typing import TYPE_CHECKING, Any

import geopandas as gpd
import pandas as pd
from _schemas import SECTOR_MAPPING

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")


def disaggregate_production(
    shapes_path: str, national_production_path: str, ratios_path: str, output_path: str
):
    """Map industrial production per country to each shape using proxies.

    The ratios file provides a value between 0 and 1 for each shape and industry subcategory,
    indicating the share of the country's production of that sector.
    The industrial production per country is multiplied by the ratio at that shape.
    The unit of the production is kt/a. NOTE: resulting file should have this embedded.

    Args:
        shapes_path (str): filtered polygons
        national_production_path (str): path to national production statistics
        ratios_path (str): proxied ratios
        output_path (str): path to resulting file
    """
    # Load input files
    shapes_df = gpd.read_parquet(shapes_path).set_index("shape_id")
    nat_prod_df = pd.read_csv(national_production_path, index_col=0)
    ratios_df = pd.read_csv(ratios_path, index_col=0)

    shape_production_df = pd.DataFrame(
        index=ratios_df.index, columns=nat_prod_df.columns, dtype=float
    )
    countries = shapes_df["country_id"].unique()
    sectors = nat_prod_df.columns

    # Map industry shares using selected proxies
    for country, sector in product(countries, sectors):
        country_shapes = shapes_df[shapes_df["country_id"] == country].index
        mapping = SECTOR_MAPPING.get(sector, "population")

        ratios = ratios_df.loc[country_shapes, mapping]
        shape_production_df.loc[country_shapes, sector] = (
            nat_prod_df.at[country, sector] * ratios
        )

    shape_production_df.to_csv(output_path)


if __name__ == "__main__":
    disaggregate_production(
        shapes_path=snakemake.input.shapes,
        national_production_path=snakemake.input.future_europe_production,
        ratios_path=snakemake.input.production_rates,
        output_path=snakemake.output.production,
    )
