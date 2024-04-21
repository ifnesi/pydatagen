import sys
import signal
import logging


class GracefulShutdown:
    """Class/context manager to manage graceful shutdown
    This class implements the singleton pattern, the reason is to avoid having the signal handler instantiated multiple times
    """

    def __init__(self, kafka_producer):
        self.was_signal_set = False
        self.safe_to_terminate = False
        self.kafka_producer = kafka_producer
        self._frame = None
        self._signal = signal.SIGTERM
        # Set signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def __enter__(self):
        self.safe_to_terminate = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.safe_to_terminate = True
        if self.was_signal_set:
            self.signal_handler(self._signal, self._frame)

    def signal_handler(self, sig, frame):
        if not self.was_signal_set:
            self._signal = sig
            self._frame = frame
            logging.info("Starting graceful shutdown...")
        if self.safe_to_terminate:
            logging.info("Graceful shutdown completed")
            if self.kafka_producer:
                logging.info("Flushing messages...")
                try:
                    self.kafka_producer.flush()
                except Exception as err:
                    logging.error(sys_exc(sys.exc_info()))
            sys.exit(0)
        self.was_signal_set = True


def sys_exc(exc_info) -> str:
    """
    Get details about Exceptions
    """
    exc_type, exc_obj, exc_tb = exc_info
    return f"{exc_type} | {exc_tb.tb_lineno} | {exc_obj}"
