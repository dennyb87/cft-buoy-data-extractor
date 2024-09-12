from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from cft_buoy_data_extractor.constants import GraphType, Station
from cft_buoy_data_extractor.digitizer import StationDataDigitizer


@dataclass
class StationDataRequest:
    station: Station
    begin_date: str
    end_date: str
    graph_type: GraphType
    debug: bool = False
    
    @property
    def query_params(self):
        return urlencode(
            dict(
                id=self.station.value,
                begin_date=self.begin_date,
                end_date=self.end_date,
                type=self.graph_type,
            )
        )


class CFTBuoyDataExtractor:
    base_url = "https://www.cfr.toscana.it/ondametria/grafico_onda.php"

    @classmethod
    def get_station(cls, station_data_request: "StationDataRequest"):
        url = f"{cls.base_url}?{station_data_request.query_params}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers=headers)
        station_data = StationDataDigitizer(
            station_data_request=station_data_request,
            response=response,
        ).to_data()
        return station_data


if __name__ == "__main__":
    data_request = StationDataRequest(
        station=Station.BOA_GORGONA,
        begin_date="06/09/2024",
        end_date="07/09/2024",
        graph_type=GraphType.SIGNIFICANT_WAVE_HEIGHT,
        debug=True,
    )
    CFTBuoyDataExtractor.get_station(data_request)
