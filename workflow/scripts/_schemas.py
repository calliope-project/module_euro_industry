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


class ShapeSchema(DataFrameModel):
    class Config:
        coerce = True
        strict = "filter"
        drop_invalid_rows = True

    shape_id: Series[str] = Field(unique=True)
    "Unique ID for this shape."
    country_id: Series[str] = Field(isin=PYPSA_EUR_COUNTRIES)
    "ISO alpha-3 code."
    shape_class: Series[str] = Field(isin=["land"])
    "Shape classifier"
    geometry: GeoSeries
    "Shape polygon."
    population: Series[float] = Field(ge=0)
    "Population within shape."

    @check("geometry", element_wise=True)
    def geom_not_empty(cls, geom):
        return (geom is not None) and (not geom.is_empty) and geom.is_valid
