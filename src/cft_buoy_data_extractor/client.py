from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlencode

import requests

from cft_buoy_data_extractor.constants import Graph, Graphs, Station
from cft_buoy_data_extractor.digitizer import StationDataDigitizer


@dataclass
class StationDataRequest:
    station: Station
    begin_date: str
    end_date: str
    graph: "Graphs"
    debug: bool = False

    class UnsupportedTimedelta(Exception):
        pass

    @property
    def timedelta_hours(self):
        begin = datetime.strptime(self.begin_date, "%d/%m/%Y").date()
        end = datetime.strptime(self.end_date, "%d/%m/%Y").date()
        delta = end - begin
        delta_days = delta.days + 1
        if delta_days != 2:
            raise self.UnsupportedTimedelta(
                f"Graph behaviour is not consistent with different timedelta \
                    therefore we only support {delta_days} days timedelta!"
            )
        return delta_days * 24

    @property
    def query_params(self):
        return urlencode(
            dict(
                id=self.station.value,
                begin_date=self.begin_date,
                end_date=self.end_date,
                type=self.graph.value.type,
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
