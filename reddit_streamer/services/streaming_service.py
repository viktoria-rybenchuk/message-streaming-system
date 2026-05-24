import time
import logging
from typing import Iterator, Dict, Any

from ..models import Comment
from ..config import ProducerConfig

logger = logging.getLogger(__name__)


class StreamingService:
    def __init__(
        self,
        dataset_reader,
        message_producer,
        config: ProducerConfig
    ):
        self.dataset_reader = dataset_reader
        self.message_producer = message_producer
        self.config = config
        self.messages_sent = 0

    def stream_comments(self) -> None:
        logger.info("Starting Reddit Comment Streamer...")
        logger.info(f"Kafka Servers: {self.config.kafka.bootstrap_servers}")
        logger.info(f"Topic: {self.config.kafka.topic}")
        logger.info(f"Dataset: {self.config.dataset_path}")
        logger.info(f"Message Delay: {self.config.message_delay_sec}s")
        logger.info("-" * 50)

        try:
            for row in self.dataset_reader.read():
                comment = Comment.from_csv_row(row)
                message = comment.to_message()

                self.message_producer.send(
                    key=comment.comment_id,
                    value=message
                )

                self.messages_sent += 1

                if self.messages_sent % self.config.progress_log_interval == 0:
                    logger.info(f"Sent {self.messages_sent} messages...")

                if self.config.message_delay_sec > 0:
                    time.sleep(self.config.message_delay_sec)

        except Exception as e:
            logger.error(f"Error streaming data: {e}")
            raise
        finally:
            logger.info(f"Total messages sent: {self.messages_sent}")
            self.message_producer.flush()