import sys
import signal
import logging


class GracefulShutdown:
    """Class/context manager to manage graceful shutdown
    This class implements the singleton pattern, the reason is to avoid having the signal handler instantiated multiple times
    """

    def __init__(self, producer):
        self.was_signal_set = False
        self.safe_to_terminate = False
        self.producer = producer
        # Set signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def __enter__(self):
        self.safe_to_terminate = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.safe_to_terminate = True
        if self.was_signal_set:
            self.signal_handler(signal.SIGTERM, None)

    def signal_handler(self, sig, frame):
        if not self.was_signal_set:
            logging.info("Starting graceful shutdown...")
        if self.safe_to_terminate:
            logging.info("Graceful shutdown completed")
            if self.producer:
                logging.info("Flushing messages...")
                try:
                    self.producer.flush()
                except Exception as err:
                    logging.error(err)
            sys.exit(0)
        self.was_signal_set = True
