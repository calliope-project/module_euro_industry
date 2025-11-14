"""Functions to prepare coke oven data.

Based on PyPSA-Eur code.
"""

import sys
from functools import partial
from typing import TYPE_CHECKING, Any

import _schemas
import country_converter as coco
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w", buffering=1)

IDX = pd.IndexSlice
IDEES_RENAME = {"GR": "EL", "GB": "UK"}


def eurostat_per_country(input_eurostat: str, country: str) -> pd.DataFrame:
    """Read energy balance data for a specific country from Eurostat.

    Parameters
    ----------
    input_eurostat : str
        Path to the directory containing Eurostat data files.
    country : str
        Country code for the specific country.

    Returns
    -------
    pd.DataFrame
        Concatenated energy balance data for the specified country.

    Notes
    -----
    - The function reads `<input_eurostat>/<country>.-Energy-balance-sheets-April-2023-edition.xlsb`
    - It removes the "Cover" sheet from the data and concatenates all the remaining sheets into a single DataFrame.
    """
    filename = (
        f"{input_eurostat}/{country}-Energy-balance-sheets-April-2023-edition.xlsb"
    )
    sheet = pd.read_excel(
        filename,
        engine="pyxlsb",
        sheet_name=None,
        skiprows=4,
        index_col=list(range(4)),
        na_values=":",
    )
    sheet.pop("Cover")
    return pd.concat(sheet)


def build_eurostat(input_eurostat: str) -> pd.DataFrame:
    """Return multi-index for all countries' energy data in TWh/a.

    Parameters
    ----------
    input_eurostat : str
        Path to the Eurostat database.

    Returns
    -------
    pd.DataFrame
        Multi-index DataFrame containing energy data for all countries in TWh/a.

    Notes
    -----
    - The function first renames the countries in the input list using the `idees_rename` mapping and removes "CH".
    - It then reads country-wise data using :func:`eurostat_per_country` into a single DataFrame.
    - The data is reordered, converted to TWh/a, and missing values are filled.
    """
    countries = _schemas.PYPSA_EUR_COUNTRIES
    countries_a2 = coco.convert(names=countries, src="ISO3", to="ISO2")
    countries_a2_no_che = {
        IDEES_RENAME.get(country, country) for country in countries_a2
    } - {"CH"}
    func = partial(eurostat_per_country, input_eurostat)

    # Regular for-loop instead of multiprocessing + tqdm
    dfs = []
    for country in countries_a2_no_che:
        dfs.append(func(country))

    index_names = ["country_id", "year", "lvl1", "lvl2", "lvl3", "lvl4"]
    df = pd.concat(dfs, keys=countries_a2_no_che, names=index_names)
    df.index = df.index.set_levels(df.index.levels[1].astype(int), level=1)

    # drop columns with all NaNs
    unnamed_cols = df.columns[df.columns.astype(str).str.startswith("Unnamed")]
    df.drop(unnamed_cols, axis=1, inplace=True)
    df.drop(list(range(1990, 2022)), axis=1, inplace=True, errors="ignore")

    # make numeric values where possible
    df.replace("Z", 0, inplace=True)
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.select_dtypes(include=[np.number])

    # write 'International aviation' to the lower level of the multiindex
    int_avia = df.index.get_level_values(3) == "International aviation"
    temp = df.loc[int_avia]
    temp.index = pd.MultiIndex.from_frame(
        temp.index.to_frame().fillna("International aviation")
    )
    df = pd.concat([temp, df.loc[~int_avia]]).sort_index()

    # Fill in missing data on "Domestic aviation" for each country.
    for country in countries_a2_no_che:
        slicer = IDX[country, :, :, :, "Domestic aviation"]
        # For the Total and Fossil energy columns, fill in zeros with
        # the closest non-zero value in the year index.
        for col in ["Total", "Fossil energy"]:
            df.loc[slicer, col] = (
                df.loc[slicer, col].replace(0.0, np.nan).ffill().bfill()
            )

    # Renaming some indices
    index_rename = {
        "Households": "Residential",
        "Commercial & public services": "Services",
        "Domestic navigation": "Domestic Navigation",
        "International maritime bunkers": "Bunkers",
        "UK": "GB",
        "EL": "GR",
    }
    columns_rename = {"Total": "Total all products"}
    df.rename(index=index_rename, columns=columns_rename, inplace=True)
    df.sort_index(inplace=True)

    # convert to TWh/a from ktoe/a
    df *= 11.63 / 1e3

    return df


def build_transformation_output_coke(eurostat: pd.DataFrame, output_path: str) -> None:
    """Extracts and builds the transformation output data for coke ovens from the Eurostat dataset.

    This function specifically filters the Eurostat data to extract
    transformation output related to coke ovens.
    Since the transformation output for coke ovens
    is not included in the final energy consumption of the iron and steel sector,
    it needs to be processed and added separately. The filtered data is saved
    as a CSV file.

    Args:
        eurostat (pd.DataFrame): A pandas DataFrame containing Eurostat data with a multi-level index.
        output_path (str): The file path where the resulting file should be saved.
    """
    slicer = pd.IndexSlice[:, :, :, "Coke ovens", "Other sources", :]
    df = eurostat.loc[slicer, :].droplevel(level=[2, 3, 4, 5])
    df = df.reset_index()
    df["country_id"] = coco.convert(names=df["country_id"], src="ISO2", to="ISO3")

    df.to_csv(output_path, index=False)


def main(eurostat_dir: str, output_coke_path: str):
    """Main processing."""
    eurostat_df = build_eurostat(eurostat_dir)
    build_transformation_output_coke(eurostat_df, output_coke_path)


if __name__ == "__main__":
    main(
        eurostat_dir=snakemake.input.eurostat_dir,
        output_coke_path=snakemake.output.coke,
    )
