"""Build industrial production per model region.

Adapted from PyPSA-Eur code (MIT licensed).
- Contributors to PyPSA-Eur: https://github.com/pypsa/pypsa-eur
- Commit: https://github.com/PyPSA/pypsa-eur/commit/822a92729e6973aa3aff741d6c94f1da2c75e8b2
"""

import sys
from itertools import product
from typing import TYPE_CHECKING, Any

import geopandas as gpd
import pandas as pd

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")


# map JRC/our sectors to hotmaps sector, where mapping exist
SECTOR_MAPPING = {
    "Electric arc": "EAF",
    "Integrated steelworks": "Integrated steelworks",
    "DRI + Electric arc": "DRI + EAF",
    "Ammonia": "Ammonia",
    "HVC": "Chemical industry",
    "HVC (mechanical recycling)": "Chemical industry",
    "HVC (chemical recycling)": "Chemical industry",
    "Methanol": "Chemical industry",
    "Chlorine": "Chemical industry",
    "Other chemicals": "Chemical industry",
    "Pharmaceutical products etc.": "Chemical industry",
    "Cement": "Cement",
    "Ceramics & other NMM": "Non-metallic mineral products",
    "Glass production": "Glass",
    "Pulp production": "Paper and printing",
    "Paper production": "Paper and printing",
    "Printing and media reproduction": "Paper and printing",
    "Alumina production": "Non-ferrous metals",
    "Aluminium - primary production": "Non-ferrous metals",
    "Aluminium - secondary production": "Non-ferrous metals",
    "Other non-ferrous metals": "Non-ferrous metals",
}


def diaggregate_production(
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
    diaggregate_production(
        shapes_path=snakemake.input.shapes,
        national_production_path=snakemake.input.future_national_production,
        ratios_path=snakemake.input.ratios,
        output_path=snakemake.output.production,
    )
