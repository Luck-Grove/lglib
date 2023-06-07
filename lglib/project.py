from pathlib import Path

from qgis.core import QgsProject


class CurrentProject:
    def __init__(self) -> None:
        self.instance = QgsProject.instance()

    @property
    def path(self) -> Path:
        return Path(self.instance.homePath())

    @property
    def layers_path(self) -> Path:
        return self.path / "Layers"

    @property
    def import_path(self) -> Path:
        return self.path / "Imports"

    @property
    def export_path(self) -> Path:
        return self.path / "Exports"

    @property
    def config(self) -> Path:
        return self.path / "Config" / "config.toml"
