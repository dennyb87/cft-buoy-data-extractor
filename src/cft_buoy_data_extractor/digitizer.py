
import csv
from dataclasses import dataclass
import subprocess
from tempfile import NamedTemporaryFile
from typing import Dict, List, TYPE_CHECKING

import numpy as np
import requests
import cv2

if TYPE_CHECKING:
    from cft_buoy_data_extractor.client import StationDataRequest


@dataclass
class StationDataDigitizer:
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
            if self.debug:
                img = cv2.imread(data_plot_tmp.name, -1)
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
        cropped_image = image[31: height-200, 71: width-60]
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
