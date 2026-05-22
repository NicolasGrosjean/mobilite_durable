import logging
import typing
from pathlib import Path

DATA_FOLDER: Path = Path(__file__).parent.parent / "src" / "data"
LOGGER_LEVEL: typing.Final = logging.INFO
EPSG_WEB_MERCATOR: str = "EPSG:3857"
EPSG_WGS84: str = "EPSG:4326"
