# Adapted from PyPSA-Eur (https://github.com/pypsa/pypsa-eur)
# Copyright (c) 2017-2024 The PyPSA-Eur Authors
# Licensed under the MIT License
# Commit: 822a92729e6973aa3aff741d6c94f1da2c75e8b2
"""Build historical annual ammonia production per country in ktonNH3/a.

Description
-------

This functions takes data from the `Minerals Yearbook` (July 2024) published by the
US Geological Survey (USGS) and the National Minerals Information Center.
<https://www.usgs.gov/centers/national-minerals-information-center/nitrogen-statistics-and-information>
"""

import sys
from typing import TYPE_CHECKING, Any

import country_converter as coco
import pandas as pd

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)

cc = coco.CountryConverter()


def main(input_path: str, output_path: str) -> None:
    """Extracts the annual ammonia production per country in ktonN/a.

    The data is converted to ktonNH3/a.
    """
    ammonia = pd.read_excel(
        input_path,
        sheet_name="T12",
        skiprows=5,
        header=0,
        index_col=0,
        skipfooter=7,
        na_values=["--"],
    )

    ammonia.index = cc.convert(ammonia.index, to="ISO3")

    years = [str(i) for i in range(2018, 2023)]

    ammonia = ammonia.rename(columns=lambda x: str(x))[years]

    # convert from ktonN to ktonNH3
    ammonia *= 17 / 14

    ammonia.index.name = "ktonNH3/a"

    ammonia.to_csv(output_path)


if __name__ == "__main__":
    main(input_path=snakemake.input.usgs, output_path=snakemake.output.production)
