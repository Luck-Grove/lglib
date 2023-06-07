import geopandas as gpd


def subset_df_to_schema(data: gpd.GeoDataFrame, schema: dict) -> gpd.GeoDataFrame:
    """Subsets columns in a dataframe to those contained in a schema"""
    schema_properties = get_schema_properties(schema)
    schema_properties.append("geometry")
    return data[schema_properties]


def get_schema_properties(schema: dict) -> list[str]:
    """Returns a list of all properties in a schema"""
    properties_dict = schema["properties"]
    return [key for key, val in properties_dict.items()]
