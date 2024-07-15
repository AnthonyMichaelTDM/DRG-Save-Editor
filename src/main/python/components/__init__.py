try:  # Python 3.8+
    from .Enums import Dwarf, Resource
except ImportError:
    pass

from .StateManager import Stats

__all__ = ["Dwarf", "Resource", "Stats"]
