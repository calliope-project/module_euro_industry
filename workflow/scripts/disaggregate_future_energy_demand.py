# Adapted from PyPSA-Eur (https://github.com/pypsa/pypsa-eur)
# Copyright (c) 2017-2024 The PyPSA-Eur Authors
# Licensed under the MIT License
# Commit: 822a92729e6973aa3aff741d6c94f1da2c75e8b2
"""Build industrial energy demand per model region.

Description
-------
This rule aggregates the energy demand of the industrial sectors per model region.
For each bus, the following carriers are considered:
- electricity
- coal
- coke
- solid biomass
- methane
- hydrogen
- low-temperature heat
- naphtha
- ammonia
- process emission
- process emission from feedstock

which can later be used as values for the industry load.
"""

import sys
from typing import TYPE_CHECKING, Any

import geopandas as gpd
import pandas as pd

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)

if __name__ == "__main__":
    shapes_df = gpd.read_parquet(snakemake.input.shapes).set_index("shape_id")
    # import ratios
    sector_ratios = pd.read_csv(
        snakemake.input.sector_rates, header=[0, 1], index_col=0
    )
    # material demand per node and industry (Mton/a)
    shape_prod_df = (
        pd.read_csv(snakemake.input.future_production, index_col=0) / 1e3
    )
    # energy demand today to get current electricity
    shape_curr_dem_df = pd.read_csv(
        snakemake.input.current_energy_demand, index_col=0
    )
    shape_subsec_rate_df = pd.concat(
        {
            idx: sector_ratios[shapes_df.loc[idx, "country_id"]]
            for idx in shape_prod_df.index
        },
        axis="columns"
    )
    shape_prod_df = shape_prod_df.stack()
    shape_prod_df.index.names = [None, None]  # FIXME: bad practice. fix with tidy data

    # final energy consumption per region and industry subsector (TWh/a)
    shape_fut_dem_df = (
        (shape_subsec_rate_df.multiply(shape_prod_df))
        .T.groupby(level=0)
        .sum()
    )

    rename_sectors = {
        "elec": "electricity",
        "biomass": "solid biomass",
        "heat": "low-temperature heat",
    }
    shape_fut_dem_df = shape_fut_dem_df.rename(columns=rename_sectors)

    shape_fut_dem_df["current electricity"] = shape_curr_dem_df["electricity"]

    shape_fut_dem_df.index.name = "TWh/a (MtCO2/a)"

    fn = snakemake.output.energy_demand
    shape_fut_dem_df.to_csv(fn, float_format="%.2f")
