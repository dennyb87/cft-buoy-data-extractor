import csv
import subprocess
from dataclasses import dataclass
from enum import Enum
from tempfile import NamedTemporaryFile
from typing import Dict, List
from urllib.parse import urlencode

import cv2
import numpy as np
import requests


class Station(Enum):
    BOA_GORGONA = "TOS25000001"

class GraphType(str, Enum):
    SIGNIFICANT_WAVE_HEIGHT = "Hm0"
    PEAK_PERIOD = "Tp"
    PEAK_DIRECTION = "Dirp"
    SEA_TEMPERATURE = "Tsea"


@dataclass
class StationData:
    response: "requests.Response"



@dataclass
class StationDataExtractor:
    station_data_request: "StationDataRequest"
    response: "requests.Response"

    @property
    def debug(self):
        return self.station_data_request.debug

    def digitize_plot(self, plot_image) -> Dict[str, List[float]]:
        with (
            NamedTemporaryFile(suffix=".png") as plot_tmp,
            NamedTemporaryFile(suffix=".csv") as data_tmp,
            NamedTemporaryFile(suffix=".png") as data_plot_tmp,
        ):
            cv2.imwrite(plot_tmp.name, plot_image)
            height, width, _ = plot_image.shape
            process = subprocess.run(
                [
                    f"plotdigitizer",
                    f"{plot_tmp.name}",
                    "-p", "0,0", "-p", "10,0", "-p", "0,1",
                    "-l", "0,0", "-l", f"{width},0", "-l", f"0,{height}",
                    f"--output", f"{data_tmp.name}",
                    f"--plot", f"{data_plot_tmp.name}",
                ],
            )
            process.check_returncode()
            img = cv2.imread(data_plot_tmp.name, -1)
            if self.debug:
                self.show(img)
            return self.construct_xy_dict(data_tmp.name)

    def construct_xy_dict(self, temp_csv_path: str) -> Dict[str, List[float]]:
        out = {"x": [], "y": []}
        rows = csv.reader(open(temp_csv_path), delimiter=' ')
        for x, y in rows:
            out["x"].append(float(x))
            out["y"].append(float(y))
        return out

    def to_data(self) -> Dict[str, List[float]]:
        plot_image = self.prepare_plot_image()
        if self.debug:
            self.show(plot_image)
        return self.digitize_plot(plot_image)
    
    def isolate_trajectory(self, image):
        imghsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        black = np.array([0, 0, 0])
        upper_gray = np.array([200, 200, 200])

        mask = cv2.inRange(imghsv, black, upper_gray)

        image[mask > 0] = (255, 255, 255)
        return image

    def prepare_plot_image(self):
        image = np.asarray(bytearray(self.response.content), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR) # -1 as it is
        height, width, _ = image.shape
        cropped_image = image[30: height-200, 70: width-70]
        trajectory = self.isolate_trajectory(cropped_image)
        imghsv = cv2.cvtColor(trajectory, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([110, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(imghsv, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(trajectory, contours, -1, (0,0,0), 2)    
        return trajectory

    def show(self, image):
        cv2.imshow('output', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


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
        station_data = StationDataExtractor(
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
