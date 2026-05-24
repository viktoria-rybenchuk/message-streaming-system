import csv
import fcntl
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CSV_HEADERS = [
    'comment_id',
    'comment_timestamp',
    'sent_timestamp',
    'received_timestamp',
    'processed_timestamp',
    'latency_ms',
    'message_size_bytes',
    'subreddit',
    'consumer_group'
]


class CSVLogStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._init_file()

    def _init_file(self) -> None:
        try:
            Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

            # Check file existence first, then create with headers atomically
            file_exists = Path(self.file_path).exists()

            if not file_exists:
                # File doesn't exist - create it with headers
                # Use 'x' mode to fail if file was created by another process
                try:
                    with open(self.file_path, 'x', newline='') as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                        try:
                            writer = csv.writer(f)
                            writer.writerow(CSV_HEADERS)
                            logger.info(f"Initialized CSV file with headers: {self.file_path}")
                        finally:
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except FileExistsError:
                    # Another process created it first - that's OK, they wrote headers
                    logger.info(f"CSV file already exists (created by another process): {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to initialize CSV file: {e}")
            raise

    def save(self, log_row: list) -> None:
        try:
            # Check if file needs headers (file was deleted or never created)
            if not Path(self.file_path).exists():
                self._init_file()

            with open(self.file_path, 'a', newline='') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    writer = csv.writer(f)
                    writer.writerow(log_row)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception as e:
            logger.error(f"Failed to save to CSV: {e}")