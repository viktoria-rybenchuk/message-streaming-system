import csv
import logging
from typing import Iterator, Dict, Any

logger = logging.getLogger(__name__)


class CSVDatasetReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> Iterator[Dict[str, Any]]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    yield row
        except FileNotFoundError:
            logger.error(f"Dataset file not found at {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading dataset: {e}")
            raise