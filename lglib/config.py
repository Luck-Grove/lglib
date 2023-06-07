from pathlib import Path
from typing import Any
import toml


class ConfigManager:
    """Manages toml configs by ensuring data continuity when reading from
    and updating files"""

    def __init__(self, filename: Path) -> None:
        self.fn = filename
        self._check_file_valid()

    def data(self) -> dict:
        with open(self.fn, "r") as file:
            data = toml.load(file)
        return data

    def update(self, section_name: str, data: dict) -> None:
        """
        Updates the specified section of the TOML configuration file with the provided data.

        This method first retrieves the current data from the TOML file, then updates the specified
        section with the provided data. If the section does not exist, a new section is created.
        The updated data is then written back to the file.

        Args:
            data (dict): The dictionary containing the new configuration data to be updated.
            section_name (str): The name of the section in the TOML file that needs to be updated.

        Raises:
            TypeError: If 'data' is not of type dict.
        """
        toml_data = self.data()
        toml_data[section_name] = data
        self._write(toml_data)

    def _write(self, data: dict) -> None:
        with open(self.fn, "w") as file:
            toml.dump(data, file)

    def _check_file_valid(self) -> None:
        """If file does not exist, creates file"""
        if self.fn.is_file():
            return
        self.fn.parent.mkdir(parents=True)
        with open(self.fn, "w") as file:
            pass


class PluginConfig:
    def __init__(self, data: dict) -> None:
        self._config = data

    def update_config(self, config: dict[Any, Any]) -> None:
        """Takes in a dictionary and updates internal config"""
        self._config.update(config)

    @property
    def data(self) -> dict[Any, Any]:
        """Returns config dict"""
        return self._config
