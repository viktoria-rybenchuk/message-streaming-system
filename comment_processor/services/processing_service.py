import time
import logging
from datetime import datetime
from typing import Dict, Any

from ..models import ProcessingLog
from ..config import ConsumerConfig

logger = logging.getLogger(__name__)


class ProcessingService:
    def __init__(
        self,
        message_consumer,
        log_storage,
        config: ConsumerConfig
    ):
        self.message_consumer = message_consumer
        self.log_storage = log_storage
        self.config = config
        self.messages_processed = 0

    def process_messages(self) -> None:
        logger.info(f"Starting consumer: {self.config.kafka.group_id} | Topic: {self.config.kafka.topic}")

        try:
            for message, message_size in self.message_consumer.poll():
                self._process_message(message, message_size)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            logger.info(f"Processed {self.messages_processed} messages")

    def _process_message(self, message: Dict[str, Any], message_size: int) -> None:
        try:
            received_timestamp = datetime.now()

            time.sleep(self.config.processing_delay_sec)

            processed_timestamp = datetime.now()

            log = ProcessingLog.from_message(
                message=message,
                received_timestamp=received_timestamp,
                processed_timestamp=processed_timestamp,
                message_size=message_size,
                consumer_group=self.config.kafka.group_id
            )

            self.log_storage.save(log.to_csv_row())

            self.messages_processed += 1

        except Exception as e:
            logger.error(f"Error processing message: {e}")