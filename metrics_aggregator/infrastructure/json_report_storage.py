import json
import logging
from pathlib import Path
from datetime import datetime

from ..models import MetricReport

logger = logging.getLogger(__name__)


class JSONReportStorage:
    def __init__(self, reports_dir: str):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save(self, report: MetricReport) -> None:
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = self.reports_dir / f"metrics_report_{timestamp}.json"

            with open(filename, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)

            logger.info(f"Saved: {filename}")

        except Exception as e:
            logger.error(f"Failed to save: {e}")