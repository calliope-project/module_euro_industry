"""This rule builds the historical industrial production per country.

Description
-------

The industrial production is taken from the `JRC-IDEES`
<https://joint-research-centre.ec.europa.eu/potencia-policy-oriented-tool-energy-and-climate-change-impact-assessment/jrc-idees_en)>.

This dataset provides detailed information about the consumption of energy for various processes.
If the country is not part of the EU28, the energy consumption in the industrial sectors is taken from `Eurostat`.
<https://ec.europa.eu/eurostat/de/data/database>`

The industrial production is calculated for the year specified in the config["industry"]["reference_year"].

The ammonia production is provided by the rule `build_ammonia_production`.
<https://pypsa-eur.readthedocs.io/en/latest/sector.html#module-build_ammonia_production>`

Since Switzerland is not part of the EU28 nor reported by eurostat, the energy consumption in the industrial sectors is taken from the `BFE <https://pubdb.bfe.admin.ch/de/publication/download/11817> dataset.
After the industrial production is calculated, the basic chemicals are separated into ammonia, chlorine, methanol and HVC. The production of these chemicals is assumed to be proportional to the production of basic chemicals without ammonia.

The following subcategories [kton/a] are considered:
- Electric arc
- Integrated steelworks
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
- Other industrial sectors
- Ammonia
- HVC
- Chlorine
- Methanol
"""

import multiprocessing as mp
import sys
from functools import partial
from typing import TYPE_CHECKING, Any

import country_converter as coco
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    snakemake: Any
sys.stderr = open(snakemake.log[0], "w")

cc = coco.CountryConverter()

TJ_TO_KTOE = 0.0238845
KTOE_TO_TWH = 0.01163

SUB_SHEET_NAME_DICT = {
    "Iron and steel": "ISI",
    "Chemical industry": "CHI",
    "Non-metallic mineral products": "NMM",
    "Pulp, paper and printing": "PPA",
    "Food, beverages and tobacco": "FBT",
    "Non Ferrous Metals": "NFM",
    "Transport equipment": "TRE",
    "Machinery equipment": "MAE",
    "Textiles and leather": "TEL",
    "Wood and wood products": "WWP",
    "Other industrial sectors": "OIS",
}

EU27 = cc.EU27as("ISO2").ISO2.values

JRC_NAMES = {"GR": "EL", "GB": "UK"}

SECT2SUB = {
    "Iron and steel": ["Electric arc", "Integrated steelworks"],
    "Chemical industry": [
        "Basic chemicals",
        "Other chemicals",
        "Pharmaceutical products etc.",
    ],
    "Non-metallic mineral products": [
        "Cement",
        "Ceramics & other NMM",
        "Glass production",
    ],
    "Pulp, paper and printing": [
        "Pulp production",
        "Paper production",
        "Printing and media reproduction",
    ],
    "Food, beverages and tobacco": ["Food, beverages and tobacco"],
    "Non Ferrous Metals": [
        "Alumina production",
        "Aluminium - primary production",
        "Aluminium - secondary production",
        "Other non-ferrous metals",
    ],
    "Transport equipment": ["Transport equipment"],
    "Machinery equipment": ["Machinery equipment"],
    "Textiles and leather": ["Textiles and leather"],
    "Wood and wood products": ["Wood and wood products"],
    "Other industrial sectors": ["Other industrial sectors"],
}

SUB2SECT = {v: k for k, vv in SECT2SUB.items() for v in vv}

FIELDS = {
    "Electric arc": "Electric arc",
    "Integrated steelworks": "Integrated steelworks",
    "Basic chemicals": "Basic chemicals (kt ethylene eq.)",
    "Other chemicals": "Other chemicals (kt ethylene eq.)",
    "Pharmaceutical products etc.": "Pharmaceutical products etc. (kt ethylene eq.)",
    "Cement": "Cement (kt)",
    "Ceramics & other NMM": "Ceramics & other NMM (kt bricks eq.)",
    "Glass production": "Glass production  (kt)",
    "Pulp production": "Pulp production (kt)",
    "Paper production": "Paper production  (kt)",
    "Printing and media reproduction": "Printing and media reproduction (kt paper eq.)",
    "Food, beverages and tobacco": "Physical output (index)",
    "Alumina production": "Alumina production (kt)",
    "Aluminium - primary production": "Aluminium - primary production",
    "Aluminium - secondary production": "Aluminium - secondary production",
    "Other non-ferrous metals": "Other non-ferrous metals (kt lead eq.)",
    "Transport equipment": "Physical output (index)",
    "Machinery equipment": "Physical output (index)",
    "Textiles and leather": "Physical output (index)",
    "Wood and wood products": "Physical output (index)",
    "Other industrial sectors": "Physical output (index)",
}

EB_SECTORS = {
    "Iron & steel": "Iron and steel",
    "Chemical & petrochemical": "Chemical industry",
    "Non-ferrous metals": "Non-metallic mineral products",
    "Paper, pulp & printing": "Pulp, paper and printing",
    "Food, beverages & tobacco": "Food, beverages and tobacco",
    "Non-metallic minerals": "Non Ferrous Metals",
    "Transport equipment": "Transport equipment",
    "Machinery": "Machinery equipment",
    "Textile & leather": "Textiles and leather",
    "Wood & wood products": "Wood and wood products",
    "Not elsewhere specified (industry)": "Other industrial sectors",
}


CH_MAPPING = {
    "Nahrung": "Food, beverages and tobacco",
    "Textil / Leder": "Textiles and leather",
    "Papier / Druck": "Pulp, paper and printing",
    "Chemie / Pharma": "Chemical industry",
    "Zement / Beton": "Non-metallic mineral products",
    "Andere NE-Mineralien": "Other non-ferrous metals",
    "Metall / Eisen": "Iron and steel",
    "NE-Metall": "Non Ferrous Metals",
    "Metall / Geräte": "Transport equipment",
    "Maschinen": "Machinery equipment",
    "Andere Industrien": "Other industrial sectors",
}


def find_physical_output(df):
    start = np.where(df.index.str.contains("Physical output", na=""))[0][0]
    empty_row = np.where(df.index.isnull())[0]
    end = empty_row[np.argmax(empty_row > start)]
    return slice(start, end)


def get_energy_ratio(country, eurostat_dir, jrc_dir, year, snakemake):
    if country == "CH":
        # data ranges between 2014-2023
        e_country = pd.read_csv(
            snakemake.input.ch_industrial_production, index_col=0
        ).dropna()
        e_country = e_country.rename(index=CH_MAPPING).groupby(level=0).sum()
        e_country = e_country[str(min(2019, year))]
        e_country *= TJ_TO_KTOE
    else:
        ct_eurostat = country.replace("GB", "UK")
        # estimate physical output, energy consumption in the sector and country
        fn = f"{eurostat_dir}/{ct_eurostat}-Energy-balance-sheets-April-2023-edition.xlsb"
        df = pd.read_excel(
            fn, sheet_name=str(min(2019, year)), index_col=2, header=0, skiprows=4
        )
        e_country = df.loc[EB_SECTORS.keys(), "Total"].rename(EB_SECTORS)

    fn = f"{jrc_dir}/EU27/JRC-IDEES-2021_Industry_EU27.xlsx"

    df = pd.read_excel(fn, sheet_name="Ind_Summary", index_col=0, header=0).squeeze(
            "columns"
    )

    assert df.index[49] == "by sector"
    year_i = df.columns.get_loc(year)
    e_eu27 = df.iloc[50:77, year_i]
    e_eu27.index = e_eu27.index.str.lstrip()

    e_ratio = e_country / e_eu27

    return pd.Series({k: e_ratio[v] for k, v in SUB2SECT.items()})


def industry_production_per_country(country, year, eurostat_dir, jrc_dir, snakemake):
    def get_sector_data(sector, country):
        jrc_country = JRC_NAMES.get(country, country)
        fn = f"{jrc_dir}/{jrc_country}/JRC-IDEES-2021_Industry_{jrc_country}.xlsx"
        sheet = SUB_SHEET_NAME_DICT[sector]
        df = pd.read_excel(fn, sheet_name=sheet, index_col=0, header=0).squeeze(
                "columns"
        )

        year_i = df.columns.get_loc(year)
        df = df.iloc[find_physical_output(df), year_i]

        df = df.loc[map(FIELDS.get, SECT2SUB[sector])]
        df.index = SECT2SUB[sector]

        return df

    ct = "EU27" if country not in EU27 else country
    demand = pd.concat([get_sector_data(s, ct) for s in SECT2SUB])

    if country not in EU27:
        demand *= get_energy_ratio(country, eurostat_dir, jrc_dir, year, snakemake)

    demand.name = country

    return demand


def industry_production(countries, year, eurostat_dir, jrc_dir):
    func = partial(
        industry_production_per_country,
        year=year,
        eurostat_dir=eurostat_dir,
        jrc_dir=jrc_dir,
        snakemake=snakemake,
    )

    demand_l = [func(c) for c in countries]

    demand = pd.concat(demand_l, axis=1).T
    demand.index.name = "kton/a"
    return demand


def separate_basic_chemicals(ammonia_path, demand, year, params):
    """Separate basic chemicals into ammonia, chlorine, methanol and HVC."""
    # ammonia data from 2018-2022
    ammonia = pd.read_csv(ammonia_path, index_col=0)

    there = ammonia.index.intersection(demand.index)
    missing = demand.index.symmetric_difference(there)

    print(f"Following countries have no ammonia demand: {missing.tolist()}")

    demand["Ammonia"] = 0.0

    year_to_use = min(max(year, 2018), 2022)
    if year_to_use != year:
        print(
            f"Year {year} outside data range. Using data from {year_to_use} for ammonia production."
        )
    demand.loc[there, "Ammonia"] = ammonia.loc[there, str(year_to_use)]

    demand["Basic chemicals"] -= demand["Ammonia"]

    # EE, HR and LT got negative demand through subtraction - poor data
    col = "Basic chemicals"
    demand[col] = demand[col].clip(lower=0.0)

    # assume HVC, methanol, chlorine production proportional to non-ammonia basic chemicals
    distribution_key = (
        demand["Basic chemicals"]
        / params["basic_chemicals_without_NH3_production_today"]
        / 1e3
    )
    demand["HVC"] = params["HVC_production_today"] * 1e3 * distribution_key
    demand["Chlorine"] = params["chlorine_production_today"] * 1e3 * distribution_key
    demand["Methanol"] = params["methanol_production_today"] * 1e3 * distribution_key

    demand.drop(columns=["Basic chemicals"], inplace=True)


def main(
    countries: list[str],
    params: dict,
    jrc_dir: str,
    eurostat_dir: str,
    ammonia_production: str,
    output_path: str,
):
    year = params["reference_year"]
    demand = industry_production(countries, year, eurostat_dir, jrc_dir)
    separate_basic_chemicals(ammonia_production, demand, year, params)
    demand.fillna(0.0, inplace=True)

    demand.to_csv(output_path, float_format="%.2f")


if __name__ == "__main__":
    main(
        countries=snakemake.params.countries,
        params=snakemake.params.industry,
        jrc_dir=snakemake.input.jrc_dir,
        eurostat_dir=snakemake.input.eurostat_dir,
        ammonia_production=snakemake.input.ammonia_production,
        output_path=snakemake.output.production_per_country,
    )
