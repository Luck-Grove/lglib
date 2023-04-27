from qgis.core import QgsMessageLog


def hello() -> None:
    return QgsMessageLog.logMessage("Hello, World")
