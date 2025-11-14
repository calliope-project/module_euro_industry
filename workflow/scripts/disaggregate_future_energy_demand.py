# SPDX-FileCopyrightText: Contributors to PyPSA-Eur <https://github.com/pypsa/pypsa-eur>
#
# SPDX-License-Identifier: MIT
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
    shapes_df = gpd.read_parquet(snakemake.input.shapes)
    # import ratios
    sector_ratios = pd.read_csv(
        snakemake.input.sector_ratios, header=[0, 1], index_col=0
    )
    # material demand per node and industry (Mton/a)
    nodal_production = (
        pd.read_csv(snakemake.input.disaggregated_future_production, index_col=0) / 1e3
    )
    # energy demand today to get current electricity
    current_energy_demand = pd.read_csv(
        snakemake.input.disaggregated_current_energy_demand, index_col=0
    )
    breakpoint()
    nodal_sector_ratios = pd.concat(
        {node: sector_ratios[node[:2]] for node in nodal_production.index},
        axis="columns",
    )

    nodal_production_stacked = nodal_production.stack()
    nodal_production_stacked.index.names = [None, None]

    # final energy consumption per node and industry (TWh/a)
    nodal_df = (
        (nodal_sector_ratios.multiply(nodal_production_stacked))
        .T.groupby(level=0)
        .sum()
    )

    rename_sectors = {
        "elec": "electricity",
        "biomass": "solid biomass",
        "heat": "low-temperature heat",
    }
    nodal_df.rename(columns=rename_sectors, inplace=True)

    nodal_df["current electricity"] = current_energy_demand["electricity"]

    nodal_df.index.name = "TWh/a (MtCO2/a)"

    fn = snakemake.output.industrial_energy_demand_per_node
    nodal_df.to_csv(fn, float_format="%.2f")
