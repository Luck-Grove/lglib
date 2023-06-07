import geopandas as gpd
from lglib.data_interfaces import LayerReference
from lglib.file_generation.shapefile import ShapefileWriter


class GeometryValidator:
    def __init__(self, writer: ShapefileWriter) -> None:
        self.writer = writer

    def validate(self, ref: LayerReference) -> LayerReference:
        return ref


def get_valid_geometry(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Returns the rows of original geodataframe where geometry is valid"""
    mask = data.geometry.is_valid
    return data.loc[mask].reset_index(drop=True)
