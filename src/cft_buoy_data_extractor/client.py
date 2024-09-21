from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from cft_buoy_data_extractor.constants import Graph, Station
from cft_buoy_data_extractor.digitizer import StationDataDigitizer


@dataclass
class CFTBuoyDataExtractor:
    station: Station
    graph: "Graph"
    debug: bool = False
    base_url = "https://www.cfr.toscana.it/ondametria/grafico_onda.php"

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
    
    @property
    def station_url(self):
        return f"{self.base_url}?{self.query_params}"
    
    @property
    def headers(self):
        return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_station_data(self):
        response = requests.get(self.station_url, headers=self.headers)
        station_data = StationDataDigitizer(
            graph=self.graph,
            debug=self.debug,
            raw_image=response.content,
        ).to_data()
        return station_data
