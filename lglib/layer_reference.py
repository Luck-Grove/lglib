from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
from qgis.core import QgsVectorLayer, QgsProject

from lglib.file_generation.shapefile import FileWriter


@dataclass(frozen=True)
class LayerReference:
    layer_name: str
    layer_source: Path
    qgis_layer: QgsVectorLayer


class LayerPreprocessor(ABC):
    """
    Base class for functions that are used to preprocess and validate layer references
    """

    @abstractmethod
    def run(self, ref: LayerReference) -> LayerReference:
        pass


class GeometryValidator(LayerPreprocessor):
    """
    Removes any invalid geometries from LayerReferences
    """

    def __init__(self, instance: QgsProject, writer: FileWriter) -> None:
        self.instance = instance
        self.writer = writer

    def run(self, ref: LayerReference) -> LayerReference:
        """Removes any invalid geometries and writes to file if any are found"""
        ref.qgis_layer.commitChanges()
        df = gpd.read_file(str(ref.layer_source), engine="fiona")
        valid_df = df.loc[df.geometry.is_valid].reset_index(drop=True)
        if len(df.index) != len(valid_df.index):
            self.writer.write(ref.layer_source, valid_df, ref.layer_name)
        return ref
