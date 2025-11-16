# Adapted from PyPSA-Eur (https://github.com/pypsa/pypsa-eur)
# Copyright (c) 2017-2024 The PyPSA-Eur Authors
# Licensed under the MIT License
# Commit: 822a92729e6973aa3aff741d6c94f1da2c75e8b2
"""Build specific energy consumption by carrier and industries and by country.

Iterpolates between the current average energy consumption (from 2015-2020) and the ideal future best-in-class consumption.

Description
-------

The config["industry"]["sector_ratios_fraction_future"] parameter determines the progress towards the future best-in-class consumption.
For each bus, the following industry subcategories

- Electric arc
- DRI + Electric arc
- Integrated steelworks
- HVC
- HVC (mechanical recycling)
- HVC (chemical recycling)
- Ammonia
- Chlorine
- Methanol
- Other chemicals
- Pharmaceutical products etc.
- Cement
- Ceramics & other NMM
- Glass production
- Pulp production
- Paper production
- Printing and media reproduction
- Food, beverages and tobacco
- Alumina production
- Aluminium - primary production
- Aluminium - secondary production
- Other non-ferrous metals
- Transport equipment
- Machinery equipment
- Textiles and leather
- Wood and wood products
- Other Industrial Sectors

with the following carriers are considered:

- elec
- coal
- coke
- biomass
- methane
- hydrogen
- heat
- naphtha
- process emission
- process emission from feedstock
- (ammonia)

Unit of the output file is MWh/t.
"""

import logging
import sys
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from _helpers import get

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")

logger = logging.getLogger(__name__)


def prepare_future_europe_sector_rates(
    year: int,
    params: dict,
    sector_rates_path: str,
    current_demand_path: str,
    future_production_path: str,
    output_path: str,
):
    """Prepare sector rates per country for a future scenario.

    Args:
        year (int): future year to construct.
        params (dict): module configuration parameters.
        sector_rates_path (str): "best in class" rates.
        current_demand_path (str): current demand per country.
        future_production_path (str): future production per country.
        output_path (str): where to save the resulting dataset.
    """
    # in TWh/a
    demand = pd.read_csv(current_demand_path, header=[0, 1], index_col=0)

    # in Mt/a
    production = (pd.read_csv(future_production_path, index_col=0) / 1e3).stack()
    production.index.names = [None, None]

    # in MWh/t
    future_sector_rates = pd.read_csv(sector_rates_path, index_col=0)

    today_sector_rates = demand.div(production, axis=1).replace([np.inf, -np.inf], 0)

    today_sector_rates.dropna(how="all", axis=1, inplace=True)

    rename = {
        "waste": "biomass",
        "electricity": "elec",
        "solid": "coke",
        "gas": "methane",
        "other": "biomass",
        "liquid": "naphtha",
    }
    today_sector_rates = today_sector_rates.rename(rename).groupby(level=0).sum()

    fraction_future = get(params["sector_ratios_fraction_future"], year)

    future_sector_rates_ct = {}
    for country, group in today_sector_rates.T.groupby(level=0):
        today_sector_ratios_ct = group.droplevel(0).T.reindex_like(future_sector_rates)
        missing_mask = today_sector_ratios_ct.isna().all()
        today_sector_ratios_ct.loc[:, missing_mask] = future_sector_rates.loc[
            :, missing_mask
        ]
        today_sector_ratios_ct.loc[:, ~missing_mask] = today_sector_ratios_ct.loc[
            :, ~missing_mask
        ].fillna(future_sector_rates)
        future_sector_rates_ct[country] = (
            today_sector_ratios_ct * (1 - fraction_future)
            + future_sector_rates * fraction_future
        )

    future_sector_rates_ct = pd.concat(future_sector_rates_ct, axis="columns")

    future_sector_rates_ct.to_csv(output_path)


if __name__ == "__main__":
    prepare_future_europe_sector_rates(
        year=int(snakemake.wildcards.year),
        params=snakemake.params.industry,
        sector_rates_path=snakemake.input.sector_rates,
        current_demand_path=snakemake.input.current_european_demand,
        future_production_path=snakemake.input.future_european_production,
        output_path=snakemake.output.sector_rates,
    )
