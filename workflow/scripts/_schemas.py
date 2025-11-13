"""Schemas for key files."""

from pandera.pandas import DataFrameModel, Field, check
from pandera.typing.geopandas import GeoSeries
from pandera.typing.pandas import Series

PYPSA_EUR_COUNTRIES = [
    "ALB",
    "AUT",
    "BEL",
    "BGR",
    "BIH",
    "CHE",
    "CZE",
    "DEU",
    "DNK",
    "ESP",
    "EST",
    "FIN",
    "FRA",
    "GBR",
    "GRC",
    "HRV",
    "HUN",
    "IRL",
    "ITA",
    "LTU",
    "LUX",
    "LVA",
    "MKD",
    "MNE",
    "NLD",
    "NOR",
    "POL",
    "PRT",
    "ROU",
    "SRB",
    "SVK",
    "SVN",
    "SWE",
    "XKX",
]


class ShapeSchema(DataFrameModel):
    class Config:
        coerce = True
        strict = False

    shape_id: Series[str] = Field(unique=True)
    "Unique ID for this shape."
    country_id: Series[str] = Field(isin=PYPSA_EUR_COUNTRIES)
    "ISO alpha-3 code."
    shape_class: Series[str] = Field(isin=["land", "maritime"])
    "Shape classifier"
    geometry: GeoSeries
    "Shape polygon."

    @check("geometry", element_wise=True)
    def geom_not_empty(cls, geom):
        return (geom is not None) and (not geom.is_empty) and geom.is_valid
