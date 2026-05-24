import logging

from .config import ProducerConfig
from .infrastructure import CSVDatasetReader, KafkaMessageProducer
from .services import StreamingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    config = ProducerConfig.from_env()

    dataset_reader = CSVDatasetReader(config.dataset_path)
    message_producer = KafkaMessageProducer(
        bootstrap_servers=config.kafka.bootstrap_servers_list,
        topic=config.kafka.topic,
        acks=config.kafka.acks,
        retries=config.kafka.retries
    )

    service = StreamingService(dataset_reader, message_producer, config)

    try:
        service.stream_comments()
    except KeyboardInterrupt:
        logger.info("Streaming interrupted by user")
    finally:
        message_producer.close()
        logger.info("Producer closed.")


if __name__ == "__main__":
    main()