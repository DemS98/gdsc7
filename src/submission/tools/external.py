"""
Module for managing UNESCO API calls
"""

import json

from typing import Literal
from langchain_core.tools import tool
import requests

import pandas as pd

_PIRLS_HISTORICAL_SCORES = pd.read_csv(
    "src/submission/resources/previous_pirls.csv",
    sep=";",
    index_col="Country",
    na_values="",
)


@tool("get_indicators_data")
def get_indicators_data(
    indicators: list[
        Literal[
            "10",
            "13",
            "20162",
            "21506",
            "CR.1",
            "READ.PRIMARY",
            "PREPFUTURE.1.READ",
            "XGDP.1.FSGOV",
            "NY.GDP.MKTP.CD",
            "NY.GDP.PCAP.CD",
            "NY.GDP.MKTP.KD.ZG",
        ]
    ],
    countries: list[str],
    year: int = 2021,
) -> str:
    """
    Get UNESCO data for given 'indicators', related to 'countries' in the specified 'year'

    Args:
        indicators (list[str]): list of indicators for which data has to be retrieved
        countries (list[str]): list of countries for which data has to be retrieved
        year (int): the year of the data

    Returns:
        str: the UNESCO data
    """

    data = requests.get(
        "https://api.uis.unesco.org/api/public/data/indicators",
        params={
            "indicator": indicators,
            "indicatorMetadata": False,
            "geoUnit": countries,
            "geoUnitType": "NATIONAL",
            "start": year,
            "end": year,
        },
        timeout=30,
    )

    return json.dumps(data.json(), indent=2) if data.status_code == 200 else ""


@tool("get_previous_pirls_scores")
def get_previous_pirls_scores(countries: list[str]) -> str:
    """
    Get historical average reading scores from PIRLS surveys prior to 2021, for given 'countries'.

    Args:
        countries (list[str]): list of country names for which to retrieve historical PIRLS scores

    Returns:
        str: the historical PIRLS scores data
    """

    available_countries = _PIRLS_HISTORICAL_SCORES.index.intersection(countries)

    return _PIRLS_HISTORICAL_SCORES.loc[available_countries].to_json(
        orient="index", index=True, indent=2, double_precision=0
    )
