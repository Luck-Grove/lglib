import logging
from pathlib import Path
from typing import TypedDict, Optional, Protocol

import fiona
import geopandas as gpd
import toml
from fiona.crs import from_epsg


class SchemaDict(TypedDict):
    geometry: str
    properties: dict[str, str]


class SchemaParser(Protocol):
    def get_schema(self, schema_name) -> Optional[SchemaDict]:
        pass


class TOMLSchemaParser:
    def __init__(self, toml_path: Path) -> None:
        self.path = toml_path
        self._data = self.load_schema_toml()

    def get_schema(self, schema_name: str) -> Optional[SchemaDict]:
        res = self._data.get(schema_name)
        if res is None:
            logging.debug(f"Failed to fetch schema for {schema_name}")
        return res

    def load_schema_toml(self) -> dict[str, SchemaDict]:
        with open(self.path) as file:
            toml_data = toml.load(file)
        return toml_data


class ShapefileWriter:
    driver = "ESRI Shapefile"

    def __init__(self, parser: SchemaParser) -> None:
        self.parser = parser

    def create_shapefile(self, schema_name: str, output_fn: str, crs_code: int) -> None:

        if Path(output_fn).exists():
            raise FileExistsError(f"File {output_fn} already exists")

        schema = self.parser.get_schema(schema_name)
        if schema is None:
            raise KeyError(f"Schema {schema_name} is not available to parser")

        driver = "ESRI Shapefile"
        crs = from_epsg(crs_code)
        with fiona.open(output_fn, "w", driver, schema, crs):
            pass

    def write_shapefile(
        self,
        filename: Path,
        data: gpd.GeoDataFrame,
        schema: SchemaDict,
    ) -> Path:
        data.to_file(
            filename=str(filename), driver=self.driver, schema=schema, index=False
        )
        return filename
