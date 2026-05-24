import json
import logging
from typing import Iterator, Dict, Any, List
from kafka import KafkaConsumer as KafkaClient
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaMessageConsumer:
    def __init__(
        self,
        topic: str,
        bootstrap_servers: List[str],
        group_id: str,
        auto_offset_reset: str = 'earliest',
        enable_auto_commit: bool = True,
        auto_commit_interval_ms: int = 5000
    ):
        try:
            self._consumer = KafkaClient(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=enable_auto_commit,
                auto_commit_interval_ms=auto_commit_interval_ms,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
            )
        except KafkaError as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            raise

    def poll(self) -> Iterator[tuple[Dict[str, Any], int]]:
        for message in self._consumer:
            try:
                message_value = message.value
                message_size = len(json.dumps(message_value).encode('utf-8'))
                yield message_value, message_size
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                continue

    def close(self) -> None:
        try:
            self._consumer.close()
        except Exception as e:
            logger.error(f"Error closing consumer: {e}")