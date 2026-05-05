from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from processors.distances import DistancesProcessor


@pytest.fixture
def mock_get_bus_stops(mocker: MockerFixture):
    res = pd.DataFrame(
        [(0, None, None, None), (None, 1, None, None), (None, None, 2, None)],
        columns=["osm_id", "gtfs_id", "navitia_id", "geometry"],
    )
    mocker.patch.object(DistancesProcessor, "_get_bus_stops", return_value=res)


@pytest.fixture
def mock_get_bus_stops2(mocker: MockerFixture):
    res = pd.DataFrame(
        [
            (0, None, None, None),
            (None, 1, None, None),
            (None, None, 2, None),
            (None, None, 3, None),
        ],
        columns=["osm_id", "gtfs_id", "navitia_id", "geometry"],
    )
    mocker.patch.object(DistancesProcessor, "_get_bus_stops", return_value=res)


@pytest.fixture
def mock_get_bus_stops3(mocker: MockerFixture):
    res = pd.DataFrame(
        [(0, None, None, None), (None, 1, 2, None)],
        columns=["osm_id", "gtfs_id", "navitia_id", "geometry"],
    )
    mocker.patch.object(DistancesProcessor, "_get_bus_stops", return_value=res)


@pytest.fixture
def mock_get_area_activities(mocker: MockerFixture):
    res = pd.DataFrame([(0, None, 420)], columns=["Id wp", "geometry", "latitude_index"])
    mocker.patch.object(DistancesProcessor, "_get_area_activities", return_value=res)


@pytest.fixture
def mock_compute_distance(mocker: MockerFixture):
    mocker.patch.object(DistancesProcessor, "_compute_distance", return_value=42.0)


@pytest.fixture
def mock_compute_distance_fail(mocker: MockerFixture):
    mocker.patch.object(
        DistancesProcessor,
        "_compute_distance",
        side_effect=Exception("Failed to compute distance"),
    )


class DummyDistancesProcessor(DistancesProcessor):
    @classmethod
    def write_dummy_output_file(cls):
        res = pd.DataFrame(
            [
                (0, None, None, 0, 14.0),
                (None, 1, None, 0, np.nan),
                (None, None, 2, 0, 4999.0),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m"],
        )
        cls.save(res, cls.output_file)

    @classmethod
    def write_dummy_part_file(cls, output_dir: Path, computed: bool = True):
        res = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, np.nan, computed),
                (None, None, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        cls.save(
            res, output_dir / "bus_stops_to_activities_distances_latitude_index_420.parquet"
        )


class TestFetch:
    def test_fetch_from_api_no_previous_distances(
        self,
        mock_get_bus_stops: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "non_existing.parquet"
        result = DummyDistancesProcessor.fetch()
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 42.0, True),
                (None, 1, None, 0, 42.0, True),
                (None, None, 2, 0, 42.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_from_file(
        self,
        mock_get_bus_stops: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_output_file()
        result = DummyDistancesProcessor.fetch()
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 14.0),
                (None, 1, None, 0, np.nan),
                (None, None, 2, 0, 4999.0),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_reload_pipeline(
        self,
        mock_get_bus_stops: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_output_file()
        result = DummyDistancesProcessor.fetch(reload_pipeline=True)
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 42.0, True),
                (None, 1, None, 0, 42.0, True),
                (None, None, 2, 0, 42.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_keep_old_distances(
        self,
        mock_get_bus_stops: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_part_file(tmp_path)
        result = DummyDistancesProcessor.fetch(fetch_api_kwargs={"keep_old_distances": True})
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, np.nan, True),
                (None, None, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_compute_non_computed_distances_only(
        self,
        mock_get_bus_stops3: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_part_file(tmp_path, computed=False)
        result = DummyDistancesProcessor.fetch(
            fetch_api_kwargs={"compute_non_computed_distances_only": True}
        )
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, 42.0, True),
                (None, None, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_compute_non_computed_distances_only_compute_distance_fail(
        self,
        mock_get_bus_stops3: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance_fail: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_part_file(tmp_path, computed=False)
        result = DummyDistancesProcessor.fetch(
            fetch_api_kwargs={"compute_non_computed_distances_only": True}
        )
        expected = pd.DataFrame(
            [
                (0, np.nan, None, 0, 14.0, True),
                (None, np.nan, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)
        expected_part = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, np.nan, False),
                (None, None, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        df_cross_part = DummyDistancesProcessor.fetch_from_file(
            tmp_path / "bus_stops_to_activities_distances_latitude_index_420.parquet"
        )
        pd.testing.assert_frame_equal(df_cross_part, expected_part)

    def test_fetch_compute_non_computed_distances_only_but_nothing_to_compute(
        self,
        mock_get_bus_stops3: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_part_file(tmp_path, computed=True)
        result = DummyDistancesProcessor.fetch(
            fetch_api_kwargs={"compute_non_computed_distances_only": True}
        )
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, np.nan, True),
                (None, None, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_reload_pipeline_and_keep_old_distances(
        self,
        mock_get_bus_stops: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_output_file()
        DummyDistancesProcessor.write_dummy_part_file(tmp_path)
        result = DummyDistancesProcessor.fetch(
            reload_pipeline=True, fetch_api_kwargs={"keep_old_distances": True}
        )
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, np.nan, True),
                (None, None, 2, 0, 4999.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_reload_pipeline_and_keep_old_distances2(
        self,
        mock_get_bus_stops2: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_output_file()
        DummyDistancesProcessor.write_dummy_part_file(tmp_path)
        result = DummyDistancesProcessor.fetch(
            reload_pipeline=True, fetch_api_kwargs={"keep_old_distances": True}
        )
        expected = pd.DataFrame(
            [
                (0, None, None, 0, 14.0, True),
                (None, 1, None, 0, np.nan, True),
                (None, None, 2, 0, 4999.0, True),
                (None, None, 3, 0, 42.0, True),
            ],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_fetch_reload_pipeline_and_keep_old_distances3(
        self,
        mock_get_bus_stops3: pd.DataFrame,
        mock_get_area_activities: pd.DataFrame,
        mock_compute_distance: MockerFixture,
        tmp_path: Path,
    ):
        DummyDistancesProcessor.output_dir = tmp_path
        DummyDistancesProcessor.output_file = tmp_path / "distances.parquet"
        DummyDistancesProcessor.write_dummy_output_file()
        DummyDistancesProcessor.write_dummy_part_file(tmp_path)
        result = DummyDistancesProcessor.fetch(
            reload_pipeline=True, fetch_api_kwargs={"keep_old_distances": True}
        )
        expected = pd.DataFrame(
            [(0, None, None, 0, 14.0, True), (None, 1, 2, 0, 42.0, True)],
            columns=["osm_id", "gtfs_id", "navitia_id", "Id wp", "distance_m", "computed"],
        )
        pd.testing.assert_frame_equal(result, expected)
