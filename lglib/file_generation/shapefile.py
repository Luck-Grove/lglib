import logging
from pathlib import Path
from typing import TypedDict, Optional, Protocol, Union, Any

import fiona
import geopandas as gpd
import pandas as pd
import toml
from fiona.crs import from_epsg
from abc import ABC, abstractmethod


class SchemaDict(TypedDict):
    geometry: str
    properties: dict[str, str]


def is_schema_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    if "geometry" not in value or not isinstance(value["geometry"], str):
        return False

    if "properties" not in value or not isinstance(value["properties"], dict):
        return False

    # Uncomment to validate property fields
    # for key, val in value["properties"].items():
    #     if not isinstance(key, str) or not isinstance(val, str):
    #         return False

    return True


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
            raise KeyError(
                f"{self.__class__.__name__} could not retrieve {schema_name=} from "
                f"data in {self.path}."
            )
        return res

    def load_schema_toml(self) -> dict[str, SchemaDict]:
        with open(self.path) as file:
            toml_data = toml.load(file)
        return toml_data


class FileWriter(ABC):
    def __init__(self, parser: SchemaParser) -> None:
        self.parser = parser

    def write(
        self, filename: Path, data: pd.DataFrame, schema: Union[SchemaDict, str]
    ) -> Path:
        pass


class ShapefileWriter(FileWriter):
    driver = "ESRI Shapefile"

    def __init__(self, parser: SchemaParser) -> None:
        super().__init__(parser)

    def create_shapefile(self, schema_name: str, output_fn: str, crs_code: int) -> None:

        if Path(output_fn).exists():
            raise FileExistsError(f"File {output_fn} already exists")

        schema = self.parser.get_schema(schema_name)
        driver = "ESRI Shapefile"
        crs = from_epsg(crs_code)
        with fiona.open(output_fn, "w", driver, schema, crs):
            pass

    def write(
        self,
        filename: Path,
        data: gpd.GeoDataFrame,
        schema: Union[SchemaDict, str],
    ) -> Path:
        """Method to write data from a geodataframe to a shapefile. Must provide either a schema name or
        a schema dict that can be used to write the file"""
        if isinstance(schema, str):
            file_schema = self.parser.get_schema(schema)

        elif is_schema_dict(schema):
            file_schema = schema

        else:
            raise ValueError(
                f"The schema parameter {schema} is neither a string nor SchemaDict."
            )

        data.to_file(
            filename=str(filename), driver=self.driver, schema=file_schema, index=False
        )
        return filename
