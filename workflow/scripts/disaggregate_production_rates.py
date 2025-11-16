"""Build spatial distribution of industries from Hotmaps database.

Description
-------

This rule uses the `Hotmaps` database
<https://gitlab.com/hotmaps/industrial_sites/industrial_sites_Industrial_Database>`.

After removing entries without valid locations, it assigns each industrial site to a bus region based on its location.
Then, it calculates the nodal distribution key for each sector based on the emissions of the industrial sites in each region.
his leads to a distribution key of 1 if there is only one bus per country and <1 if there are multiple buses per country. The sum over buses of one country is 1.

The following subcategories of industry are considered:
- Iron and steel
- Cement
- Refineries
- Paper and printing
- Chemical industry
- Glass
- Non-ferrous metals
- Non-metallic mineral products
- Other non-classified
Furthermore, the population distribution is added
- Population
"""

import logging
import sys
import uuid
from itertools import product
from typing import TYPE_CHECKING, Any

import country_converter as coco
import geopandas as gpd
import pandas as pd
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)
cc = coco.CountryConverter()

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)

def locate_missing_industrial_sites(df):
    """Locate industrial sites without valid locations based on city and countries.

    Should only be used if the model's spatial resolution is coarser
    than individual cities.
    """
    locator = Nominatim(user_agent=str(uuid.uuid4()))
    geocode = RateLimiter(locator.geocode, min_delay_seconds=2)

    def locate_missing(s):
        if pd.isna(s.City) or s.City == "CONFIDENTIAL":
            return None

        loc = geocode([s.City, s.Country], geometry="wkt")
        if loc is not None:
            logger.debug(f"Found:\t{loc}\nFor:\t{s['City']}, {s['Country']}\n")
            return f"POINT({loc.longitude} {loc.latitude})"
        else:
            return None

    missing = df.index[df.geom.isna()]
    df.loc[missing, "coordinates"] = df.loc[missing].apply(locate_missing, axis=1)

    # report stats
    num_still_missing = df.coordinates.isna().sum()
    num_found = len(missing) - num_still_missing
    share_missing = len(missing) / len(df) * 100
    share_still_missing = num_still_missing / len(df) * 100
    logger.warning(
        f"Found {num_found} missing locations. \nShare of missing locations reduced from {share_missing:.2f}% to {share_still_missing:.2f}%."
    )

    return df


def prepare_hotmaps_database(regions: gpd.GeoDataFrame):
    """Load hotmaps database of industrial sites and map onto bus regions."""
    df = pd.read_csv(snakemake.input.hotmaps, sep=";", index_col=0)

    df[["srid", "coordinates"]] = df.geom.str.split(";", expand=True)

    if snakemake.params.hotmaps_locate_missing:
        df = locate_missing_industrial_sites(df)

    # remove those sites without valid locations
    df.drop(df.index[df.coordinates.isna()], inplace=True)

    df["coordinates"] = gpd.GeoSeries.from_wkt(df["coordinates"])

    gdf = gpd.GeoDataFrame(df, geometry="coordinates", crs=regions.crs)
    gdf = gpd.sjoin(gdf, regions, how="inner", predicate="within")

    # the .sjoin can lead to duplicates if a geom is in two overlapping regions
    if gdf.index.duplicated().any():
        # get all duplicated entries
        duplicated_i = gdf.index[gdf.index.duplicated()]
        # convert from raw data country name to iso-2-code
        code = cc.convert(gdf.loc[duplicated_i, "Country"], to="iso3")  # noqa: F841
        # screen out malformed country allocation
        gdf_filtered = gdf.loc[duplicated_i].query("country_id == @code")
        # concat not duplicated and filtered gdf
        gdf = pd.concat([gdf.drop(duplicated_i), gdf_filtered])

    return gdf


def prepare_gem_database(regions: gpd.GeoDataFrame):
    """Load GEM database of steel plants and map onto bus regions."""
    df = pd.read_excel(
        snakemake.input.gem_gspt,
        sheet_name="Steel Plants",
        na_values=["N/A", "unknown", ">0"],
    ).query("Region == 'Europe'")

    df["Retired Date"] = pd.to_numeric(
        df["Retired Date"].combine_first(df["Idled Date"]), errors="coerce"
    )
    df["Start date"] = pd.to_numeric(
        df["Start date"].str.split("-").str[0], errors="coerce"
    )

    latlon = (
        df["Coordinates"]
        .str.split(", ", expand=True)
        .rename(columns={0: "lat", 1: "lon"})
    )
    geometry = gpd.points_from_xy(latlon["lon"], latlon["lat"])
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=regions.crs)
    gdf = gpd.sjoin(gdf, regions, how="inner", predicate="within")

    return gdf


def prepare_ammonia_database(regions: gpd.GeoDataFrame):
    """Load ammonia database of plants and map onto bus regions."""
    df = pd.read_csv(snakemake.input.ammonia, index_col=0)

    geometry = gpd.points_from_xy(df.Longitude, df.Latitude)
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=regions.crs)

    gdf = gpd.sjoin(gdf, regions, how="inner", predicate="within")

    return gdf


def prepare_cement_supplement(regions: gpd.GeoDataFrame):
    """Load supplementary cement plants from non-EU-(NO-CH) and map onto bus regions."""
    df = pd.read_csv(snakemake.input.cement_supplement, index_col=0)

    geometry = gpd.points_from_xy(df.Longitude, df.Latitude)
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=regions.crs)
    gdf = gpd.sjoin(gdf, regions, how="inner", predicate="within")

    return gdf


def prepare_refineries_supplement(regions):
    """Load supplementary refineries from non-EU-(NO-CH) and map onto bus regions."""
    df = pd.read_csv(snakemake.input.refineries_supplement, index_col=0)

    geometry = gpd.points_from_xy(df.Longitude, df.Latitude)
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=regions.crs)
    gdf = gpd.sjoin(gdf, regions, how="inner", predicate="within")

    return gdf


def build_nodal_distribution_key(
    hotmaps, gem, ammonia, cement, refineries, regions
):
    """Build nodal distribution keys for each sector."""
    sectors = hotmaps.Subsector.unique()
    countries = regions["country_id"].unique()

    keys = pd.DataFrame(index=regions.index, columns=sectors, dtype=float)

    ct_total = regions.groupby("country_id")["population"].sum()
    keys["population"] = regions["population"] / regions["country_id"].map(ct_total)

    for sector, country in product(sectors, countries):
        regions_ct = regions[regions["country_id"] == country].index

        facilities = hotmaps.query("country_id == @country and Subsector == @sector")

        if not facilities.empty:
            emissions = facilities["Emissions_ETS_2014"].fillna(
                hotmaps["Emissions_EPRTR_2014"].dropna()
            )
            if emissions.sum() == 0:
                key = pd.Series(1 / len(facilities), facilities.index)
            else:
                # assume 20% quantile for missing values
                emissions = emissions.fillna(emissions.quantile(0.2))
                key = emissions / emissions.sum()
            key = key.groupby(facilities.shape_id).sum().reindex(regions_ct, fill_value=0.0)
        elif sector == "Cement" and country in cement["country_id"].unique():
            facilities = cement.query("country_id == @country")
            production = facilities["Cement [kt/a]"]
            if production.sum() == 0:
                key = pd.Series(1 / len(facilities), facilities.index)
            else:
                key = production / production.sum()
            key = key.groupby(facilities.shape_id).sum().reindex(regions_ct, fill_value=0.0)
        elif sector == "Refineries" and country in refineries["country_id"].unique():
            facilities = refineries.query("country_id == @country")
            production = facilities["Capacity [bbl/day]"]
            if production.sum() == 0:
                key = pd.Series(1 / len(facilities), facilities.index)
            else:
                key = production / production.sum()
            key = key.groupby(facilities.shape_id).sum().reindex(regions_ct, fill_value=0.0)
        else:
            key = keys.loc[regions_ct, "population"]

        keys.loc[regions_ct, sector] = key

    # add specific steel subsectors
    steel_processes = ["EAF", "DRI + EAF", "Integrated steelworks"]
    for process, country in product(steel_processes, countries):
        regions_ct = regions[regions["country_id"] == country].index

        facilities = gem.query("country_id == @country")

        if process == "EAF":
            status_list = [
                "construction",
                "operating",
                "operating pre-retirement",
                "retired",
            ]
            capacities = facilities.loc[
                facilities["Capacity operating status"].isin(status_list)
                & (
                    facilities["Retired Date"].isna()
                    | facilities["Retired Date"].gt(2025)
                ),
                "Nominal EAF steel capacity (ttpa)",
            ].dropna()
        elif process == "DRI + EAF":
            status_list = [
                "construction",
                "operating",
                "operating pre-retirement",
                "retired",
                "announced",
            ]
            sel = [
                "Nominal BOF steel capacity (ttpa)",
                "Nominal OHF steel capacity (ttpa)",
                "Nominal iron capacity (ttpa)",
            ]
            status_filter = facilities["Capacity operating status"].isin(status_list)
            retirement_filter = facilities["Retired Date"].isna() | facilities[
                "Retired Date"
            ].gt(2030)
            start_filter = (
                facilities["Start date"].isna()
                & ~facilities["Capacity operating status"].eq("announced")
            ) | facilities["Start date"].le(2030)
            capacities = (
                facilities.loc[status_filter & retirement_filter & start_filter, sel]
                .sum(axis=1)
                .dropna()
            )
        elif process == "Integrated steelworks":
            status_list = [
                "construction",
                "operating",
                "operating pre-retirement",
                "retired",
            ]
            sel = [
                "Nominal BOF steel capacity (ttpa)",
                "Nominal OHF steel capacity (ttpa)",
            ]
            capacities = (
                facilities.loc[
                    facilities["Capacity operating status"].isin(status_list)
                    & (
                        facilities["Retired Date"].isna()
                        | facilities["Retired Date"].gt(2025)
                    ),
                    sel,
                ]
                .sum(axis=1)
                .dropna()
            )
        else:
            raise ValueError(f"Unknown process {process}")

        if not capacities.empty:
            if capacities.sum() == 0:
                key = pd.Series(1 / len(capacities), capacities.index)
            else:
                key = capacities / capacities.sum()
            buses = facilities.loc[capacities.index, "shape_id"]
            key = key.groupby(buses).sum().reindex(regions_ct, fill_value=0.0)
        else:
            key = keys.loc[regions_ct, "population"]

        keys.loc[regions_ct, process] = key

    # add ammonia
    for country in countries:
        regions_ct = regions[regions["country_id"] == country].index

        facilities = ammonia.query("country_id == @country")

        if not facilities.empty:
            production = facilities["Ammonia [kt/a]"]
            if production.sum() == 0:
                key = pd.Series(1 / len(facilities), facilities.index)
            else:
                # assume 50% of the minimum production for missing values
                production = production.fillna(0.5 * facilities["Ammonia [kt/a]"].min())
                key = production / production.sum()
            key = key.groupby(facilities["shape_id"]).sum().reindex(regions_ct, fill_value=0.0)
        else:
            key = 0.0

        keys.loc[regions_ct, "Ammonia"] = key

    return keys


def main():
    """Core production disaggregation function."""
    shapes = gpd.read_parquet(snakemake.input.shapes).set_index("shape_id")
    # Ensure shapes are coordinate-compatible
    shapes = shapes.to_crs(snakemake.params.geographic_crs)

    # Prepare individual subsector proxies
    hotmaps = prepare_hotmaps_database(shapes)
    gem = prepare_gem_database(shapes)
    ammonia = prepare_ammonia_database(shapes)
    cement = prepare_cement_supplement(shapes)
    refineries = prepare_refineries_supplement(shapes)

    # Disaggregate per shape_id
    keys = build_nodal_distribution_key(
        hotmaps, gem, ammonia, cement, refineries, shapes
    )
    keys.to_csv(snakemake.output.production_rates)


if __name__ == "__main__":
    main()
