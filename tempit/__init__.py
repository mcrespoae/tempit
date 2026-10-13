from importlib.metadata import PackageNotFoundError, version

from .core import TempitConfig, tempit

try:
    __version__ = version("tempit")
except PackageNotFoundError:  # Running from a source tree without installed metadata
    __version__ = "0.0.0+unknown"

__all__ = ["tempit", "TempitConfig", "__version__"]
