import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AggregatorConfig:
    log_dir: str
    reports_dir: str
    log_file_pattern: str = 'processing_logs_*.csv'

    @classmethod
    def from_env(cls) -> 'AggregatorConfig':
        return cls(
            log_dir=os.getenv('LOG_DIR', 'logs'),
            reports_dir=os.getenv('REPORTS_DIR', 'reports')
        )


BYTES_PER_MBIT = 1024 * 1024
BITS_PER_BYTE = 8