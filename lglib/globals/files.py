from qgis.core import QgsApplication
from pathlib import Path


def active_profile_path() -> Path:
    return Path(QgsApplication.qgisSettingsDirPath())


def layers_schema_path() -> Path:
    p = active_profile_path() / "toml_files" / "layer_schemas.toml"
    return p
