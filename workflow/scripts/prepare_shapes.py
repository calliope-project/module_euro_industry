"""Brief polygon filtering.

Ensures the module processes only regions compatible with its limted geographic scope.
"""

import sys
from typing import TYPE_CHECKING, Any

import geopandas as gpd
import gregor
import rioxarray as rxr
from _schemas import ShapeSchema

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)


def main(shapes_path: str, population_path: str, output_path: str) -> None:
    """Save a filtered version of the input shapefile."""
    shapes_df = gpd.read_parquet(shapes_path)
    population_da = rxr.open_rasterio(population_path).squeeze()  # type: ignore

    shapes_df["population"] = gregor.aggregate.aggregate_raster_to_polygon(
        population_da, shapes_df, stats="sum"
    )["sum"]

    shapes_df = ShapeSchema.validate(shapes_df, lazy=True)
    shapes_df = shapes_df.reset_index(drop=True)

    shapes_df.to_parquet(output_path)


if __name__ == "__main__":
    main(
        shapes_path=snakemake.input.shapes,
        population_path=snakemake.input.population,
        output_path=snakemake.output.shapes,
    )
