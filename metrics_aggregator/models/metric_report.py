from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class ThroughputMetrics:
    mbps: float
    bytes_per_second: float
    total_bytes: int


@dataclass
class LatencyMetrics:
    max_ms: float
    avg_ms: float
    min_ms: float


@dataclass
class MessageMetrics:
    total: int
    per_second: float


@dataclass
class MetricReport:
    timestamp: datetime
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    throughput: ThroughputMetrics
    latency: LatencyMetrics
    messages: MessageMetrics
    consumers: Dict[str, int]

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': round(self.duration_seconds, 2),
            'throughput': {
                'mbps': round(self.throughput.mbps, 4),
                'bytes_per_second': round(self.throughput.bytes_per_second, 2),
                'total_bytes': self.throughput.total_bytes,
            },
            'latency': {
                'max_ms': round(self.latency.max_ms, 2),
                'avg_ms': round(self.latency.avg_ms, 2),
                'min_ms': round(self.latency.min_ms, 2),
            },
            'messages': {
                'total': self.messages.total,
                'per_second': round(self.messages.per_second, 2),
            },
            'consumers': self.consumers,
        }