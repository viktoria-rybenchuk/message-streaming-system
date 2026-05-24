import json
import logging
from typing import Dict, Any, List
from kafka import KafkaProducer as KafkaClient

logger = logging.getLogger(__name__)


class KafkaMessageProducer:
    def __init__(
        self,
        bootstrap_servers: List[str],
        topic: str,
        acks: str = 'all',
        retries: int = 3
    ):
        self.topic = topic
        self._producer = KafkaClient(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks=acks,
            retries=retries
        )

    def send(self, key: str, value: Dict[str, Any]) -> None:
        self._producer.send(self.topic, key=key, value=value)

    def flush(self, timeout: int = 10) -> None:
        self._producer.flush(timeout=timeout)

    def close(self) -> None:
        self._producer.close()