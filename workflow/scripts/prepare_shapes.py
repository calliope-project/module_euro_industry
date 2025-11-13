"""Brief polygon filtering.

Ensures the module processes only regions compatible with its limted geographic scope.
"""
import sys
from typing import TYPE_CHECKING, Any

import geopandas as gpd
from _schemas import ShapeSchema

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)

def main(input_path: str, output_path: str) -> None:
    """Save a filtered version of the input shapefile."""
    shapes_df = gpd.read_parquet(input_path)
    shapes_df = ShapeSchema.validate(shapes_df, lazy=True)
    shapes_df.to_parquet(output_path)

if __name__ == "__main__":
    main(
        input_path=snakemake.input.shapes,
        output_path=snakemake.output.filtered,
    )
