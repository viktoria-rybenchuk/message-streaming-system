import logging
import sys

from .config import AggregatorConfig
from .infrastructure import CSVLogReader, JSONReportStorage
from .services import MetricsService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    config = AggregatorConfig.from_env()

    if len(sys.argv) > 1:
        config.log_dir = sys.argv[1]

    log_reader = CSVLogReader(config.log_dir, config.log_file_pattern)
    report_storage = JSONReportStorage(config.reports_dir)

    service = MetricsService(log_reader, report_storage)
    service.generate_report()


if __name__ == "__main__":
    main()