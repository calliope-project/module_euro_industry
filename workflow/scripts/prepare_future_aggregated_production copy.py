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
from _helpers import get

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")


def main(params: dict, year: int, input_file: str, output_file: str) -> None:
    """Build future industrial production per country."""
    production = pd.read_csv(input_file, index_col=0)

    keys = ["Integrated steelworks", "Electric arc"]
    total_steel = production[keys].sum(axis=1)

    st_primary_fraction = get(params["St_primary_fraction"], year)
    dri_fraction = get(params["DRI_fraction"], year)
    int_steel = production["Integrated steelworks"].sum()
    fraction_persistent_primary = st_primary_fraction * total_steel.sum() / int_steel

    dri = (
        dri_fraction * fraction_persistent_primary * production["Integrated steelworks"]
    )
    production.insert(2, "DRI + Electric arc", dri)

    not_dri = 1 - dri_fraction
    production["Integrated steelworks"] = (
        not_dri * fraction_persistent_primary * production["Integrated steelworks"]
    )
    production["Electric arc"] = (
        total_steel
        - production["DRI + Electric arc"]
        - production["Integrated steelworks"]
    )

    keys = ["Aluminium - primary production", "Aluminium - secondary production"]
    total_aluminium = production[keys].sum(axis=1)

    key_pri = "Aluminium - primary production"
    key_sec = "Aluminium - secondary production"

    al_primary_fraction = get(params["Al_primary_fraction"], year)
    fraction_persistent_primary = (
        al_primary_fraction * total_aluminium.sum() / (production[key_pri].sum() or 1)
    )

    production[key_pri] = fraction_persistent_primary * production[key_pri]
    production[key_sec] = total_aluminium - production[key_pri]

    production["HVC (mechanical recycling)"] = (
        get(params["HVC_mechanical_recycling_fraction"], year)
        * production["HVC"]
    )
    production["HVC (chemical recycling)"] = (
        get(params["HVC_chemical_recycling_fraction"], year)
        * production["HVC"]
    )

    production["HVC"] *= get(params["HVC_primary_fraction"], year)

    production.to_csv(output_file, float_format="%.2f")


if __name__ == "__main__":

    main(
        params=snakemake.params.industry,
        year=int(snakemake.wildcards.year),
        input_file=snakemake.input.current,
        output_file=snakemake.output.future
    )
















