import logging
import sys

from .config import ConsumerConfig
from .infrastructure import KafkaMessageConsumer, CSVLogStorage
from .services import ProcessingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    config = ConsumerConfig.from_env()

    message_consumer = KafkaMessageConsumer(
        topic=config.kafka.topic,
        bootstrap_servers=config.kafka.bootstrap_servers_list,
        group_id=config.kafka.group_id,
        auto_offset_reset=config.kafka.auto_offset_reset,
        enable_auto_commit=config.kafka.enable_auto_commit,
        auto_commit_interval_ms=config.kafka.auto_commit_interval_ms
    )

    log_storage = CSVLogStorage(config.log_file_path)

    service = ProcessingService(message_consumer, log_storage, config)

    try:
        service.process_messages()
    finally:
        message_consumer.close()


if __name__ == "__main__":
    main()