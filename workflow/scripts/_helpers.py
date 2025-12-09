import logging
import pandas as pd

logger = logging.getLogger(__name__)

SHEET_NAMES = {
    "Iron and steel": "ISI",
    "Chemicals Industry": "CHI",
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


CARRIER_INDEX = [
    "elec",
    "coal",
    "coke",
    "biomass",
    "methane",
    "hydrogen",
    "low-enthalpy-heat",
    "mid-enthalpy-heat",
    "high-enthalpy-heat",
    "naphtha",
    "ammonia",
    "methanol",
    "process emission",
    "process emission from feedstock",
]


def get(item, investment_year=None):
    """Check whether item depends on investment year."""
    if not isinstance(item, dict):
        return item
    elif investment_year in item.keys():
        return item[investment_year]
    else:
        print.warning(
            f"Investment key {investment_year} not found in dictionary {item}."
        )
        keys = sorted(item.keys())
        if investment_year < keys[0]:
            logger.warning(f"Lower than minimum key. Taking minimum key {keys[0]}")
            return item[keys[0]]
        elif investment_year > keys[-1]:
            logger.warning(f"Higher than maximum key. Taking maximum key {keys[0]}")
            return item[keys[-1]]
        else:
            logger.warning(
                "Interpolate linearly between the next lower and next higher year."
            )
            lower_key = max(k for k in keys if k < investment_year)
            higher_key = min(k for k in keys if k > investment_year)
            lower = item[lower_key]
            higher = item[higher_key]
            return lower + (higher - lower) * (investment_year - lower_key) / (
                higher_key - lower_key
            )


def load_idees_data(sector,path,year,country="EU27"):
    suffixes = {"out": "", "fec": "_fec", "ued": "_ued", "emi": "_emi"}
    sheets = {k: SHEET_NAMES[sector] + v for k, v in suffixes.items()}

    def usecols(x):
        return isinstance(x, str) or x == year

    idees = pd.read_excel(
        f"{path}/{country}/JRC-IDEES-2021_Industry_{country}.xlsx",
        sheet_name=list(sheets.values()),
        index_col=0,
        header=0,
        usecols=usecols,
    )

    for k, v in sheets.items():
        idees[k] = idees.pop(v).squeeze()
        idees[k] = idees[k][year]

    return idees


def check_route_shares(info,routes,year):
    summer = 0
    for k,v in routes.items():
        summer+=v["shares"][year]
    
    if summer != 1:
        raise ValueError(f"The sum of the production routes for {info}, in year {year} is not equal to 1 but equal to {summer}.")
