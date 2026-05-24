import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class KafkaConfig:
    bootstrap_servers: str
    topic: str
    acks: str = 'all'
    retries: int = 3

    @property
    def bootstrap_servers_list(self) -> List[str]:
        return self.bootstrap_servers.split(',')


@dataclass
class ProducerConfig:
    kafka: KafkaConfig
    dataset_path: str
    message_delay_sec: float
    progress_log_interval: int = 100

    @classmethod
    def from_env(cls) -> 'ProducerConfig':
        kafka_config = KafkaConfig(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            topic=os.getenv('KAFKA_TOPIC', 'reddit-comments'),
            acks=os.getenv('KAFKA_ACKS', 'all'),
            retries=int(os.getenv('KAFKA_RETRIES', '3'))
        )

        return cls(
            kafka=kafka_config,
            dataset_path=os.getenv('DATASET_PATH', 'datasets/lifestyle_progresspics.csv'),
            message_delay_sec=float(os.getenv('MESSAGE_DELAY_SEC', '0.1')),
            progress_log_interval=int(os.getenv('PROGRESS_LOG_INTERVAL', '100'))
        )