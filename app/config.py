import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:

    @staticmethod
    def get(key: str) -> any:
        return os.getenv(key)