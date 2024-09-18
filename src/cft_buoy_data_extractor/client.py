from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from cft_buoy_data_extractor.constants import Graph, Station
from cft_buoy_data_extractor.digitizer import StationDataDigitizer


@dataclass
class StationDataRequest:
    station: Station
    graph: "Graph"
    debug: bool = False

    @property
    def query_params(self):
        return urlencode(
            dict(
                id=self.station.value,
                begin_date=self.graph.date,
                end_date=self.graph.date,
                type=self.graph.type,
            )
        )


class CFTBuoyDataExtractor:
    base_url = "https://www.cfr.toscana.it/ondametria/grafico_onda.php"

    @classmethod
    def get_station_data(cls, station_data_request: "StationDataRequest"):
        url = f"{cls.base_url}?{station_data_request.query_params}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers=headers)
        station_data = StationDataDigitizer(
            station_data_request=station_data_request,
            response=response,
        ).to_data()
        return station_data
