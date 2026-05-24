from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class ProcessingLog:
    comment_id: str
    comment_timestamp: str
    sent_timestamp: datetime
    received_timestamp: datetime
    processed_timestamp: datetime
    message_size_bytes: int
    subreddit: str
    consumer_group: str

    @property
    def latency_ms(self) -> float:
        return (self.processed_timestamp - self.sent_timestamp).total_seconds() * 1000

    @classmethod
    def from_message(
        cls,
        message: Dict[str, Any],
        received_timestamp: datetime,
        processed_timestamp: datetime,
        message_size: int,
        consumer_group: str
    ) -> 'ProcessingLog':
        sent_timestamp_str = message.get('sent_timestamp')

        sent_timestamp = received_timestamp
        if sent_timestamp_str:
            try:
                sent_timestamp = datetime.fromisoformat(sent_timestamp_str)
            except ValueError:
                pass

        return cls(
            comment_id=message.get('comment_id', 'unknown'),
            comment_timestamp=message.get('timestamp', ''),
            sent_timestamp=sent_timestamp,
            received_timestamp=received_timestamp,
            processed_timestamp=processed_timestamp,
            message_size_bytes=message_size,
            subreddit=message.get('subreddit', 'unknown'),
            consumer_group=consumer_group
        )

    def to_csv_row(self) -> list:
        return [
            self.comment_id,
            self.comment_timestamp,
            self.sent_timestamp.isoformat(),
            self.received_timestamp.isoformat(),
            self.processed_timestamp.isoformat(),
            round(self.latency_ms, 2),
            self.message_size_bytes,
            self.subreddit,
            self.consumer_group
        ]