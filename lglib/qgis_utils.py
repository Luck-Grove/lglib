from pathlib import Path
from qgis.core import QgsProject, QgsVectorLayer


def get_qgis_layer_by_name(instance: QgsProject, layer_name: str) -> QgsVectorLayer:
    layer_list = instance.mapLayersByName(layer_name)
    if len(layer_list) == 0:
        raise ValueError(f"No layer with name {layer_name} detected")
    if len(layer_list) > 1:
        raise ValueError(f"Multiple layers with name {layer_name} detected")
    return layer_list[0]


def get_qgis_layer_source(layer: QgsVectorLayer) -> Path:
    """Returns path to data file qgis layer references"""
    filepath = layer.dataProvider().dataSourceUri().split("|")[0]
    if not filepath:
        raise ValueError(f"Could not parse source path for layer {layer.name()}")
    return Path(filepath)
