import unittest

import numpy as np
import responses
from expected_data import onda_linear_data

from cft_buoy_data_extractor.client import (CFTBuoyDataExtractor,
                                            StationDataRequest)
from cft_buoy_data_extractor.constants import SignificantWaveHeight, Station


class CFTBuoyDataExtractorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data_request = StationDataRequest(
            station=Station.BOA_GORGONA,
            graph=SignificantWaveHeight(hours=24, date="18/09/2024"),
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

        np.testing.assert_almost_equal(data["x"], expected_x, decimal=6)
        np.testing.assert_almost_equal(data["y"], expected_y, decimal=6)

    def test_sliced(self):
        self.data_request.graph.hours = 12

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.GET,
                f"{CFTBuoyDataExtractor.base_url}?{self.data_request.query_params}",
                body=self.raw_img,
                status=200,
            )
            data = CFTBuoyDataExtractor.get_station_data(self.data_request)

        expected_x = onda_linear_data["x"][:106]
        expected_y = onda_linear_data["y"][:106]

        np.testing.assert_allclose(data["x"], expected_x, rtol=10**-2)
        np.testing.assert_allclose(data["y"], expected_y, rtol=10**-6)
