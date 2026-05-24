import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..models import MetricReport, ThroughputMetrics, LatencyMetrics, MessageMetrics
from ..config import BYTES_PER_MBIT, BITS_PER_BYTE

logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(self, log_reader, report_storage):
        self.log_reader = log_reader
        self.report_storage = report_storage

    def generate_report(self) -> Optional[MetricReport]:
        logs = self.log_reader.read_logs()

        if not logs:
            logger.error("No logs found")
            return None

        report = self._calculate_metrics(logs)

        if not report:
            logger.error("Failed to calculate metrics")
            return None

        self._print_report(report)
        self.report_storage.save(report)

        return report

    def _calculate_metrics(self, logs: List[Dict[str, Any]]) -> Optional[MetricReport]:
        if not logs:
            return None

        timestamps = self._extract_timestamps(logs)
        if not timestamps:
            return None

        start_time = min(timestamps)
        end_time = max(timestamps)
        duration_seconds = max((end_time - start_time).total_seconds(), 1)

        throughput = self._calculate_throughput(logs, duration_seconds)
        latency = self._calculate_latency(logs)
        messages = self._calculate_message_metrics(logs, duration_seconds)
        consumers = self._count_consumers(logs)

        return MetricReport(
            timestamp=datetime.utcnow(),
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            throughput=throughput,
            latency=latency,
            messages=messages,
            consumers=consumers
        )

    def _extract_timestamps(self, logs: List[Dict[str, Any]]) -> List[datetime]:
        timestamps = []
        for log in logs:
            if log.get('processed_timestamp'):
                try:
                    timestamps.append(datetime.fromisoformat(log['processed_timestamp']))
                except ValueError:
                    continue
        return timestamps

    def _calculate_throughput(self, logs: List[Dict[str, Any]], duration_seconds: float) -> ThroughputMetrics:
        def get_bytes(log: Dict[str, Any]) -> int:
            value = log.get('message_size_bytes', 0)
            if isinstance(value, int):
                return value
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0

        total_bytes = sum(get_bytes(log) for log in logs)
        total_bits = total_bytes * BITS_PER_BYTE
        throughput_bps = total_bits / duration_seconds
        throughput_mbps = throughput_bps / BYTES_PER_MBIT

        return ThroughputMetrics(
            mbps=throughput_mbps,
            bytes_per_second=total_bytes / duration_seconds,
            total_bytes=total_bytes
        )

    def _calculate_latency(self, logs: List[Dict[str, Any]]) -> LatencyMetrics:
        latencies = [log['latency_ms'] for log in logs if log.get('latency_ms')]

        if not latencies:
            return LatencyMetrics(max_ms=0, avg_ms=0, min_ms=0)

        return LatencyMetrics(
            max_ms=max(latencies),
            avg_ms=sum(latencies) / len(latencies),
            min_ms=min(latencies)
        )

    def _calculate_message_metrics(self, logs: List[Dict[str, Any]], duration_seconds: float) -> MessageMetrics:
        total_messages = len(logs)
        messages_per_second = total_messages / duration_seconds

        return MessageMetrics(
            total=total_messages,
            per_second=messages_per_second
        )

    def _count_consumers(self, logs: List[Dict[str, Any]]) -> Dict[str, int]:
        consumer_counts = {}
        for log in logs:
            consumer = log.get('consumer_group', 'unknown')
            consumer_counts[consumer] = consumer_counts.get(consumer, 0) + 1
        return consumer_counts

    def _print_report(self, report: MetricReport) -> None:
        logger.info(f"Throughput: {report.throughput.mbps:.4f} Mbps")
        logger.info(f"Latency - Max: {report.latency.max_ms:.2f}ms | Avg: {report.latency.avg_ms:.2f}ms")
        logger.info(f"Messages: {report.messages.total:,} ({report.messages.per_second:.2f} msg/sec)")
        logger.info(f"Duration: {report.duration_seconds}s")