# Adapted from PyPSA-Eur (https://github.com/pypsa/pypsa-eur)
# Copyright (c) 2017-2024 The PyPSA-Eur Authors
# Licensed under the MIT License
# Commit: 822a92729e6973aa3aff741d6c94f1da2c75e8b2
"""Calculate current energy demand per region.

This rule maps the industrial energy demand per country to each region.
The unit of the energy demand is TWh/a.
"""

import sys
from itertools import product
from typing import TYPE_CHECKING, Any

import geopandas as gpd
import numpy as np
import pandas as pd
from _schemas import SECTOR_MAPPING

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)


def disaggregate_current_energy_demand(
    shapes_path: str,
    ratios_path: str,
    national_energy_demand_path: str,
    output_path: str,
):
    """Use ratios to disaggregate national energy demand for industry subsectors."""
    shapes_gdf = gpd.read_parquet(shapes_path)
    national_demand = pd.read_csv(
        national_energy_demand_path, header=[0, 1], index_col=0
    )
    ratios_df = pd.read_csv(ratios_path, index_col=0)

    disaggregated_demand = pd.DataFrame(
        0.0, dtype=float, index=ratios_df.index, columns=national_demand.index
    )

    countries = shapes_gdf["country_id"].unique()
    sectors = national_demand.columns.unique(1)

    for country, sector in product(countries, sectors):
        country_shapes = shapes_gdf[shapes_gdf["country_id"] == country]["shape_id"]
        mapping = SECTOR_MAPPING.get(sector, "population")

        ratio = ratios_df.loc[country_shapes, mapping]
        demand = national_demand[country, sector]

        outer = pd.DataFrame(
            np.outer(ratio, demand), index=ratio.index, columns=demand.index
        )
        disaggregated_demand.loc[country_shapes] += outer

    disaggregated_demand.index.name = "TWh/a"
    disaggregated_demand.to_csv(output_path)


if __name__ == "__main__":
    disaggregate_current_energy_demand(
        shapes_path=snakemake.input.shapes,
        ratios_path=snakemake.input.shape_ratios,
        national_energy_demand_path=snakemake.input.current_national_energy_demand,
        output_path=snakemake.output.demand_per_shape,
    )
