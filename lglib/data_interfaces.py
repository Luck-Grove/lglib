from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
from qgis.core import QgsProject, QgsVectorLayer

from lglib.layer_reference import LayerReference, LayerPreprocessor
from lglib.file_generation.shapefile import FileWriter


class DataProviderCreationError(Exception):
    """Raised when DP Factory cannot complete instantiation"""

    pass


@dataclass(frozen=True)
class LayerResult:
    layer: QgsVectorLayer = None
    error: str = None


class LayerReferenceFactory:
    def __init__(self, instance: QgsProject) -> None:
        self.instance = instance

    def make(self, name: str) -> LayerReference | str:
        """
        Creates a LayerReference object
        :param name: name of layer to create reference for
        :return: LayerReference if successful, str message if not
        """
        layer_result = self._get_layer(name)
        if not layer_result.layer:
            return layer_result.error
        layer = layer_result.layer
        layer.commitChanges(stopEditing=True)
        source = self._get_layer_source(layer)
        return LayerReference(name, source, layer)

    def _get_layer(self, name: str) -> LayerResult:
        layer_list = self.instance.mapLayersByName(name)
        if len(layer_list) == 0:
            return LayerResult(error=f"No layer with name {name} detected")
        if len(layer_list) > 1:
            return LayerResult(error=f"Multiple layers with name {name} detected")
        return LayerResult(layer=layer_list[0])

    @staticmethod
    def _get_layer_source(layer: QgsVectorLayer) -> Path:
        return Path(layer.dataProvider().dataSourceUri().split("|")[0])


class DataProviderFactory:
    def __init__(
        self,
        instance: QgsProject,
        layer_names: list[str],
    ) -> None:
        self.errors = []
        self.instance = instance
        self.layer_names = layer_names

    def create_provider(
        self, writer: FileWriter, preprocessors: list[LayerPreprocessor]
    ) -> DataProvider:
        data = {}
        ref_factory = LayerReferenceFactory(self.instance)
        for name in self.layer_names:
            ref_result = ref_factory.make(name)
            if isinstance(ref_result, str):
                self.errors.append(ref_result)
            else:
                data[name] = ref_result
                for preproc in preprocessors:
                    preproc.run(ref_result)
        if len(self.errors) > 0:
            raise DataProviderCreationError("Unable to complete DataProvider creation.")
        return DataProvider(data, writer)


class DataProvider:
    def __init__(self, data: dict[str, LayerReference], writer: FileWriter) -> None:
        self._data = data
        self._writer = writer

    def get_data(self, layer_name: str) -> gpd.GeoDataFrame:
        """Returns data for a given layer name as a geodataframe"""
        layer_ref = self.get_ref(layer_name)
        return gpd.read_file(str(layer_ref.layer_source), engine="fiona")

    def get_ref(self, layer_name: str) -> LayerReference:
        """Returns references to qgis layer and its data source as a bundle"""
        layer_ref = self._data.get(layer_name)
        if layer_ref is None:
            raise ValueError(f"No reference exists in data provider for {layer_name}")
        return layer_ref

    def get_schema(self, schema_name: str) -> dict:
        schema = self._writer.parser.get_schema(schema_name)
        if schema is None:
            raise KeyError("Schema Not Found in File Writer")
        return schema

    def save_data(self, data: gpd.GeoDataFrame, layer_name: str, schema=None) -> None:
        """Uses writer object to save data back into file"""
        outfn = self.get_ref(layer_name).layer_source
        if schema:
            self._writer.write(outfn, data, schema)
        else:
            self._writer.write(outfn, data, layer_name)

    @property
    def layer_list(self) -> list[str]:
        """Returns list of names of layers currently available"""
        return list(self._data.keys())
