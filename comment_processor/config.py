import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class KafkaConfig:
    bootstrap_servers: str
    topic: str
    group_id: str
    auto_offset_reset: str = 'earliest'
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000

    @property
    def bootstrap_servers_list(self) -> List[str]:
        return self.bootstrap_servers.split(',')


@dataclass
class ConsumerConfig:
    kafka: KafkaConfig
    processing_delay_sec: float
    log_dir: str

    @property
    def log_file_path(self) -> str:
        return os.path.join(self.log_dir, f'processing_logs_{self.kafka.group_id}.csv')

    @classmethod
    def from_env(cls) -> 'ConsumerConfig':
        kafka_config = KafkaConfig(
            bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            topic=os.getenv('KAFKA_TOPIC', 'reddit-comments'),
            group_id=os.getenv('CONSUMER_GROUP_ID', 'reddit-comment-processor'),
            auto_offset_reset=os.getenv('AUTO_OFFSET_RESET', 'earliest'),
            enable_auto_commit=os.getenv('ENABLE_AUTO_COMMIT', 'true').lower() == 'true',
            auto_commit_interval_ms=int(os.getenv('AUTO_COMMIT_INTERVAL_MS', '5000'))
        )

        log_dir = '/app/logs' if os.path.exists('/app/logs') else '.'

        return cls(
            kafka=kafka_config,
            processing_delay_sec=float(os.getenv('PROCESSING_DELAY_SEC', '1.0')),
            log_dir=log_dir
        )