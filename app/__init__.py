from .config import BaseConfig
from .database import Database

database = Database()

__all__ = ['BaseConfig', 'database']