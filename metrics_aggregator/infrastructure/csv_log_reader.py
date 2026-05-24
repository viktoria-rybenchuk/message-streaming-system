import csv
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CSVLogReader:
    def __init__(self, log_dir: str, file_pattern: str = 'processing_logs_*.csv'):
        self.log_dir = Path(log_dir)
        self.file_pattern = file_pattern

    def read_logs(self) -> List[Dict[str, Any]]:
        all_logs = []
        csv_files = list(self.log_dir.glob(self.file_pattern))

        if not csv_files:
            logger.warning(f"No CSV files found in: {self.log_dir}")
            return all_logs

        for csv_file in csv_files:
            try:
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_logs.append(self._parse_row(row))

            except Exception as e:
                logger.error(f"Error reading {csv_file}: {e}")

        return all_logs

    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        parsed = row.copy()

        if row.get('latency_ms'):
            try:
                parsed['latency_ms'] = float(row['latency_ms'])
            except ValueError:
                pass

        if row.get('message_size_bytes'):
            try:
                parsed['message_size_bytes'] = int(row['message_size_bytes'])
            except ValueError:
                pass

        return parsed