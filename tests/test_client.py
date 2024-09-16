import unittest

import numpy as np
import responses
from expected_data import onda_linear_data

from cft_buoy_data_extractor.client import (CFTBuoyDataExtractor,
                                            StationDataRequest)
from cft_buoy_data_extractor.constants import Graphs, Station


class CFTBuoyDataExtractorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data_request = StationDataRequest(
            station=Station.BOA_GORGONA,
            begin_date="15/09/2024",
            end_date="16/09/2024",
            graph=Graphs.SIGNIFICANT_WAVE_HEIGHT,
            debug=False,
        )
        with open("tests/grafico_onda_linear.png", "rb") as graph_file:
            self.raw_img = graph_file.read()

    def test_get_station_data(self):
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.GET,
                f"{CFTBuoyDataExtractor.base_url}?{self.data_request.query_params}",
                body=self.raw_img,
                status=200,
            )
            data = CFTBuoyDataExtractor.get_station_data(self.data_request)

        expected_x = onda_linear_data["x"]
        expected_y = onda_linear_data["y"]

        np.testing.assert_almost_equal(data["x"], expected_x, decimal=4)
        np.testing.assert_almost_equal(data["y"], expected_y, decimal=4)
